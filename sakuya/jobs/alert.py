# -*- coding: utf-8 -*-

import sys
import os
import logging
import datetime
import yaml
import json
import time
from collections import OrderedDict
from sakuya.models.sakuya_db import Charts, Categories, Follows, Events, Users, ChartdataTmpl, WarnRules
from sakuya.models import engine_sakuya_db as engine
from sakuya.config import get_config
from sakuya.lib import haopan, util
from sqlalchemy.orm import sessionmaker
from turbomail import Message, interface

NOTIFY_SCREEN_LATENCY = 60 * 10 # 10 min

# make session
Session = sessionmaker(bind=engine)
session = Session()

# setup logging
util.setup_logging('alert', False, True)

logging.getLogger('turbomail').setLevel(logging.WARN)

user_events = {}
skipped_user = set()

LEVEL_TEXT = {
    Events.CONST_TYPE_OK: 'OK',
    Events.CONST_TYPE_WARNING: 'Warning',
    Events.CONST_TYPE_CRITICAL: 'Critical'
}

# The cron job is started at the beginning of the minute,
# so the check time should be last minute,
# otherwise there'll be no data.
check_time = util.current_minute() - datetime.timedelta(minutes=2)

no_data = False # if no-data event happens for storm charts, notify jizhang only.

def compare_and_notify():
    """
    iterate through all charts, checking data whether it is out of the marks, notify the related people
    """
    charts = session.query(Charts).filter_by(alert_enable=1).all()
    session.expunge_all() # make charts objects not expired after commit
    for chart in charts:
        try:
            compare_and_notify_one(chart)
        except Exception, e:
            logging.exception('Fail to process chart %d' % chart.id)
            session.rollback()
    process_user_events()

def compare_and_notify_one(chart):

    logging.debug('Checking chart %d.' % chart.id)

    # get rules
    rules = get_rules(chart.id)
    if not rules:
        logging.debug('No rule to check.')
        return

    # parse haopan title
    if haopan.is_haopan(chart.cate_id):
        chart.name = haopan.format_title(chart.name.encode('utf-8')).decode('utf-8')

    chart_level, chart_msg = (Events.CONST_TYPE_OK, None)
    rule_warn = OrderedDict()
    for rule in rules:

        # get current data
        end = check_time
        start = end - datetime.timedelta(minutes=rule['latency'])
        data = get_data(chart.id, start, end)

        if data:
            if rule['warn_type'] == 'HWM':
                level, msg = get_alert_level_hwm(chart.name, rule['hwm_warning'], rule['hwm_critical'], data)

            elif rule['warn_type'] == 'LWM':
                level, msg = get_alert_level_lwm(chart.name, rule['lwm_warning'], rule['lwm_critical'], data)

            elif rule['warn_type'] == 'RANGE':
                prev_end = end - datetime.timedelta(7)
                prev_start = start - datetime.timedelta(7)
                prev_data = get_data(chart.id, prev_start, prev_end)
                if not prev_data:
                    prev_end = end - datetime.timedelta(1)
                    prev_start = start - datetime.timedelta(1)
                    prev_data = get_data(chart.id, prev_start, prev_end)
                level, msg = get_alert_level_range(chart.name,
                                                   rule['hwm_warning'], rule['hwm_critical'],
                                                   rule['lwm_warning'], rule['lwm_critical'],
                                                   data, prev_data)

        else:
            if 'rule' in chart.get_ext():
                no_data = True
            else:
                level = Events.CONST_TYPE_CRITICAL
                msg = u'%s 没有数据' % chart.name

        if level > chart_level:
            chart_level, chart_msg = level, msg

        rule_warn[rule['id']] = (level, msg, rule)

    # for chart
    if chart_level == Events.CONST_TYPE_OK:
        logging.debug('Chart %s' % LEVEL_TEXT[chart_level])
    else:
        logging.debug('Chart %s' % ' - '.join((LEVEL_TEXT[chart_level], chart_msg)))
        event_exists = session.\
                       query(Events).\
                       filter_by(cid=chart.id).\
                       filter(Events.type >= chart_level).\
                       filter(Events.time > check_time - datetime.timedelta(seconds=NOTIFY_SCREEN_LATENCY)).\
                       count() > 0
        if event_exists:
            logging.debug('Chart event exists (within %d minutes).' % (NOTIFY_SCREEN_LATENCY / 60))
        else:
            add_events(chart.id, chart_level, chart_msg)
    update_chart_status(chart.id, chart_level)

    # per user
    for follow in session.\
                  query(Follows).\
                  filter_by(cid=chart.id, recv_warning=True):

        if follow.follower in skipped_user:
            continue

        try:
            user = session.query(Users).get(follow.follower)
            if user is None:
                raise ValueError('User not found')

            if not user.email:
                raise ValueError('User email is empty')

            email_list = util.unique(user.email.splitlines())
            if not email_list:
                raise ValueError('User email is empty')

        except Exception, e:
            logging.warn('%s: %d' % (e, follow.follower))
            skipped_user.add(follow.follower)
            continue

        recv_rules = follow.get_recv_rules()
        if recv_rules == 'all':
            recv_rules = rule_warn.keys()

        level, msg, rule = Events.CONST_TYPE_OK, None, None
        for rid in recv_rules:
            if rid not in rule_warn:
                continue
            if rule_warn[rid][0] > level:
                level, msg, rule = rule_warn[rid]

        if level == Events.CONST_TYPE_CRITICAL:
            logging.debug('User %s %s' % (user.truename, ' - '.join((LEVEL_TEXT[level], msg))))
            if util.timestamp(check_time) - rule['last_critical'] <= rule['interval'] * 60:
                logging.debug('User event exists (within %d minutes).' % rule['interval'])
            else:
                update_rule_status(rule['id'])
                if user.id not in user_events:
                    user_events[user.id] = {
                        'truename': user.truename,
                        'email_list': email_list,
                        'events': []
                    }
                user_events[user.id]['events'].append((chart, msg))

def get_rules(chart_id):

    result = []
    for row in session.\
               query(WarnRules).\
               filter_by(chart_id=chart_id).\
               order_by(WarnRules.id):

        try:
            rule = json.loads(row.content)
            r0 = [int(hm) for hm in rule['duration_start'].split(':')]
            r1 = [int(hm) for hm in rule['duration_end'].split(':')]
            duration_start = check_time.replace(hour=r0[0], minute=r0[1])
            duration_end = check_time.replace(hour=r1[0], minute=r1[1])
            if check_time < duration_start or check_time > duration_end:
                continue

            warn_type = rule['type']
            if warn_type == 'HWM':
                hwm_warning = int(rule['hwm_warning'])
                hwm_critical = int(rule['hwm_critical'])
                lwm_warning = lwm_critical = None
            elif warn_type == 'LWM':
                lwm_warning = int(rule['lwm_warning'])
                lwm_critical = int(rule['lwm_critical'])
                hwm_warning = hwm_critical = None
            elif warn_type == 'RANGE':
                hwm_warning = int(rule['hwm_warning'])
                hwm_critical = int(rule['hwm_critical'])
                lwm_warning = int(rule['lwm_warning'])
                lwm_critical = int(rule['lwm_critical'])
            else:
                raise ValueError('Invalid warn type %s.' % rule['type'])

            latency = int(rule['latency'])
            interval = int(rule['interval'])
            if latency <= 0 or interval <= 0:
                raise ValueError('Invalid latency or interval.')

            result.append({
                'id': row.id,
                'warn_type': warn_type,
                'hwm_warning': hwm_warning,
                'hwm_critical': hwm_critical,
                'lwm_warning': lwm_warning,
                'lwm_critical': lwm_critical,
                'latency': latency,
                'interval': interval,
                'last_critical': int(rule.get('last_critical', 0))
            })

        except Exception, e:
            logging.debug('parse rule %d error' % row.id, exc_info=True)

    return result

def get_data(id, start, end):

    def _get_data(model):
        data = []
        for row in session.\
                   query(model.data).\
                   filter_by(ds_id=id).\
                   filter(model.time >= start).\
                   filter(model.time < end):
            data.append(row.data)
        return data

    start_day = start.strftime('%Y%m%d')
    data = _get_data(ChartdataTmpl.gen(start_day))
    end_day = end.strftime('%Y%m%d')
    if end_day != start_day:
        data.extend(_get_data(ChartdataTmpl.gen(end_day)))

    return data

def get_alert_level_hwm(name, warning, critical, data):
    """
    return alert level and msg for High Water Mark mode
    return value: (level, error_message)
    """
    flag_w = True
    flag_c = True
    max = data[0]
    for i in data:
        if i > max:
            max = i
        if i < warning:
            flag_w = False
        if i < critical:
            flag_c = False

    msg = u'%s 突然升至%d/分' % (name, max)
    if flag_c:
        return Events.CONST_TYPE_CRITICAL, msg
    if flag_w:
        return Events.CONST_TYPE_WARNING, msg
    return Events.CONST_TYPE_OK, None

def get_alert_level_lwm(name, warning, critical, data):
    """
    return alert level and msg for Low Water Mark mode
    return value: (level, error_message)
    """
    flag_w = True
    flag_c = True
    min = data[0]
    for i in data:
        if i < min:
            min = i
        if i > warning:
            flag_w = False
        if i > critical:
            flag_c = False

    msg = u'%s 突然降至%d/分' % (name, min)
    if flag_c:
        return Events.CONST_TYPE_CRITICAL, msg
    if flag_w:
        return Events.CONST_TYPE_WARNING, msg
    return Events.CONST_TYPE_OK, None

def get_alert_level_range(name, hwm_warning, hwm_critical, lwm_warning, lwm_critical, data, prev_data):
    """
    return alert level and msg for Range mode (compare the average value)
    return value: (level, error_message)
    """
    if not prev_data:
        logging.debug('Nothing to compare, skipping.')
        return Events.CONST_TYPE_OK, None

    avg = float(sum(data)) / len(data)
    prev_avg = float(sum(prev_data)) / len(prev_data)

    ratio = (avg - prev_avg) / prev_avg * 100

    flag_w = False
    flag_c = False

    if ratio >= 0:
        msg = u'%s 超过上周%.2f%%' % (name, ratio)
        if ratio >= hwm_warning:
            flag_w = True
        if ratio >= hwm_critical:
            flag_c = True
    else:
        msg = u'%s 低于上周%.2f%%' % (name, -ratio)
        if -ratio >= lwm_warning:
            flag_w = True
        if -ratio >= lwm_critical:
            flag_c = True

    if flag_c:
        return Events.CONST_TYPE_CRITICAL, msg
    if flag_w:
        return Events.CONST_TYPE_WARNING, msg
    return Events.CONST_TYPE_OK, None

def process_user_events():
    logging.info('Processing user events (%d users).' % len(user_events))

    # prepare email interface
    config = get_config('webapp')
    mail_config = {}
    mail_config['mail.on'] = config['turbomail']['enable']
    mail_config['mail.manager'] = config['turbomail']['manager']
    mail_config['mail.transport'] = config['turbomail']['transport']
    mail_config['mail.smtp.server'] = config['turbomail']['server']
    interface.start(mail_config)

    for id, info in user_events.iteritems():

        if len(info['events']) <= 5:
            for event in info['events']:
                title, plain, rich = format_single(event)
                send_email(config['turbomail']['sender'], info['truename'], info['email_list'], title, plain, rich)
        else:
            title, plain, rich = format_batch(info['events'])
            send_email(config['turbomail']['sender'], info['truename'], info['email_list'], title, plain, rich)

    if no_data:
        send_email(config['turbomail']['sender'], 'jizhang', ['jizhang@anjuke.com', '13817655796@139.com'], 'no data', 'no data', 'no data')

def format_single(event):
    chart, msg = event
    chart_url = 'http://knowing.corp.anjuke.com/chart/%d' % chart.id
    rich = u'<html><body><h1>%(title)s</h1>'\
           u'<p>时间：%(time)s</p>'\
           u'<p>详细信息：<a href="%(url)s">%(url)s</a></p>'\
           u'<p>本邮件由 Knowing 监控系统自动发送，请勿回复。</p></body></html>'\
           % dict(title=msg, time=time.strftime('%Y-%m-%d %H:%M'), url=chart_url)
    return msg, msg, rich

def format_batch(events):
    title = u'您有%d条报警信息待处理' % len(events)
    plain = '\r\n'.join(event[1] for event in events)
    rich = u'<html><body><h1>%s</h1><p>时间：%s</p>' % (title, time.strftime('%Y-%m-%d %H:%M'))
    for event in events:
        chart, msg = event
        chart_url = 'http://knowing.corp.anjuke.com/chart/%d' % chart.id
        rich += '<p>%(msg)s<br><a href="%(url)s">%(url)s</a></p>' % dict(msg=msg, url=chart_url)
    rich += u'<p>本邮件由 Knowing 监控系统自动发送，请勿回复。</p></body></html>'
    return title, plain, rich

def send_email(sender, truename, emails, title, plain, rich):
    """
    notify using email
    sending alert email to followers
    """
    """
    rand send email 
    """
    day_str = datetime.datetime.strftime(datetime.datetime.today(),"%d%H")
    sender = 'Knowing <Knowing-noreply-%s@dm.anjuke.com>' % day_str
    
    logging.debug('Send email %s' % ', '.join((truename, str(emails), title, plain, rich)))

    try:
        mail = Message()
        mail.subject = title
        mail.sender = sender
        mail.to = u'%s <%s>' % (truename, emails[0])
        if len(emails) > 1:
            mail.cc = u','.join(emails[1:])
        mail.encoding = 'utf-8'
        mail.plain = plain
        mail.rich = rich
        mail.send()

    except Exception, e:
        logging.exception('Fail to send email.')

def update_chart_status(id, level):
    chart = session.query(Charts).get(id)
    if chart is None:
        return

    check_timestamp = util.timestamp(check_time)

    if level == Events.CONST_TYPE_OK:
        chart.warnings = 0
        if chart.criticals and check_timestamp - chart.criticals > NOTIFY_SCREEN_LATENCY:
            chart.criticals = 0

    elif level == Events.CONST_TYPE_WARNING:
        if not chart.criticals:
            chart.warnings = check_timestamp
        elif check_timestamp - chart.criticals > NOTIFY_SCREEN_LATENCY:
            chart.criticals = 0
            chart.warnings = check_timestamp

    elif level == Events.CONST_TYPE_CRITICAL:
        chart.warnings = 0
        chart.criticals = check_timestamp

    else:
        return

    session.commit()

def update_rule_status(id):
    rule = session.query(WarnRules).get(id)
    if rule is None:
        return

    try:
        content = json.loads(rule.content)
    except Exception, e:
        logging.exception(e)
        return

    check_timestamp = util.timestamp(check_time)
    content['last_critical'] = check_timestamp
    rule.content = json.dumps(content)
    session.commit()

def add_events(id, level, message, dealt=False):
    event = Events()
    event.cid = id
    event.info = message
    event.time = datetime.datetime.now()
    event.type = level
    event.deal_status = 1 if dealt else 0
    session.add(event)
    session.commit()

def main():
    util.process_exists('alert')
    logging.info('Alert job started.')
    compare_and_notify()
    logging.info('Alert job ended.')

if __name__ == '__main__':
    main()
