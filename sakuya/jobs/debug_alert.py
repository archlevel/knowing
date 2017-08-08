#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, logging, datetime, yaml
from json import JSONDecoder
from traceback import print_exc
root_path =  os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../")

sys.path.append(root_path)

from sakuya.models.sakuya_db import Charts, Categories, Follows, Events, Users
from sakuya.models import engine_sakuya_db as engine
from sqlalchemy.orm import sessionmaker
from turbomail import Message, interface
from logging import basicConfig, getLogger, DEBUG

CONST_HWM = 'HWM'
CONST_LWM = 'LWM'
CONST_LEVEL_WARNING = 'warning'
CONST_LEVEL_CRITICAL = 'critical'
CONST_LEVEL_OK = 'ok'

Session = sessionmaker(bind=engine)
session = Session()


logging_format = '%(asctime)-15s [%(levelname)s]: %(message)s'
basicConfig(format=logging_format, level=DEBUG)
logger = getLogger()

def compare_and_notify():
    """
    iterate through all charts, checking data whether it is out of the marks, notify the related people
    """

    json_decoder = JSONDecoder()

    charts = session.query(Charts).all()

    # now = datetime.datetime.now()
    now = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d_%H:%M:%S")

    for i in charts:
        logger.debug("checking chart \"%s\"" % i.name)
        if i.alert_mode and i.alert_enable:
            try:
                duration = json_decoder.decode(i.alert_duration)
                alert_start = duration["start"]
                alert_end = duration["end"]

                if not (alert_start <= now <= alert_end):
                    continue
            except:
                pass

            td = datetime.date.today()
            tablename = 't_chartdata_%s' % td.strftime('%Y%m%d')

            latency = i.alert_latency
            delta5mins = datetime.timedelta(minutes = 5)
            delta7days = datetime.timedelta(days = 7)
            tablename_lastweek = 't_chartdata_%s' % (td - delta7days).strftime('%Y%m%d')
            start = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) - datetime.timedelta(minutes = latency)
            end = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
            data_this_time = __get_chartdata(i, tablename, start, end)
            logger.debug("data_this_time: %s" % str(data_this_time))

            if i.alert_mode == CONST_HWM or i.alert_mode == CONST_LWM:
                if i.alert_mode == CONST_HWM:
                    level, msg = __get_alert_level_hwm(i, data_this_time)
                if i.alert_mode == CONST_LWM:
                    level, msg = __get_alert_level_lwm(i, data_this_time)
            else:
                start = start - delta7days
                end = end - delta7days
                data_last_week = __get_chartdata(i, tablename_lastweek, start, end)
                logger.debug("data_last_week: %s" % str(data_last_week))
                level, msg = __get_alert_level_range(i, data_this_time, data_last_week)

            logger.debug("%s: %s, %s" % (i.name, level, msg))


            add_events(i, level, msg)

            if level == CONST_LEVEL_CRITICAL:
                __notify(i, msg)

def __get_alert_level_hwm(chart, data):
    """
    return alert level and msg for High Water Mark mode

    chart: Charts data row
    data: value to check in timespan

    return value: (level, error_message)
    """
    hwm_w = chart.alert_hwm_warning
    hwm_c = chart.alert_hwm_critical

    flag_w = True
    flag_c = True

    msg = chart.name + u' 突然升至%d/分'

    max = 0

    for i in data:
        if i > max:
            max = i
        if i< hwm_w:
            flag_w = False
        if i < hwm_c:
            flag_c = False

    msg %= max

    if flag_c:
        return CONST_LEVEL_CRITICAL, msg
    if flag_w:
        return CONST_LEVEL_WARNING, msg
    return CONST_LEVEL_OK, ""

def __get_alert_level_lwm(chart, data):
    """
    return alert level and msg for Low Water Mark mode

    chart: Charts data row
    data: value to check in timespan

    return value: (level, error_message)
    """
    lwm_w = chart.alert_lwm_warning
    lwm_c = chart.alert_lwm_critical

    flag_w = True
    flag_c = True

    msg = chart.name + u' 突然降至%d/分'

    min = sys.maxint

    for i in data:
        if i < min:
            min = i
        if i < lwm_w:
            flag_w = False
        if i < lwm_c:
            flag_c = False

    msg %= min

    if flag_c:
        return CONST_LEVEL_CRITICAL, msg
    if flag_w:
        return CONST_LEVEL_WARNING, msg
    return CONST_LEVEL_OK, ""

def __get_alert_level_range(chart, data1, data2):
    """
    return alert level and msg for Range mode (compare the average value)

    chart: Charts data row
    data1: value to check in timespan (this time)
    data2: value to check in same timespan last week

    return value: (level, error_message)
    """

    hwm_w = chart.alert_hwm_warning
    hwm_c = chart.alert_hwm_critical
    lwm_w = chart.alert_lwm_warning
    lwm_c = chart.alert_lwm_critical

    avg_data1 = __avg_value(data1)
    avg_data2 = __avg_value(data2)


    ratio = abs(int(float((avg_data1 - avg_data2)) / avg_data2 * 100))

    flag_w = False
    flag_c = False

    msg = chart.name + " "

    if avg_data1 > avg_data2:
        msg += (u'超过上周%.2f' % ratio + "%")
        if ratio > hwm_w:
            flag_w = True
        if ratio > hwm_c:
            flag_c = True
    else:
        msg += (u'低于上周%.2f' % ratio + "%")
        if ratio > lwm_w:
            flag_w = True
        if ratio > lwm_c:
            flag_c = True

    if flag_c:
        return CONST_LEVEL_CRITICAL, msg
    if flag_w:
        return CONST_LEVEL_WARNING, msg
    return CONST_LEVEL_OK, ""


def __avg_value(data):
    """
    return average value

    data: int or float values in list
    """
    if not data:
        return

    counter = 0
    sum = 0
    for i in data:
        sum += i
        counter += 1

    return int(sum / counter)


def __get_chartdata(chart, tablename, start, end):
    """
    get the chart data in the time range

    tablename: chart data table name (eg. 't_chartdata_20120101')
    start: start time (datetime)
    end: end time (datetime)

    return value list of row data (eg. [{"f_data": 1}, {"f_data": 2}])
    """
    sql = 'select f_data from %s where f_ds_id = :ds_id and f_time >= :start and f_time <= :end' % tablename
    # params = {'start': str(start)[0:19], 'end': str(end)[0:19]}
    params = {'start': start, 'end': end, 'ds_id': chart.id}
    d = session.execute(sql, params)
    logger.debug("sql: %s; params: %s" % (sql, str(params)))
    ret = []
    if d:
        for i in d:
            ret.append(i[0])
    return ret

def __notify(chart, message):
    """
    notify using email

    chart: Charts data row
    message: message body

    sending alert email to owner and followers
    """
    config = __get_config('webapp')

    mail_config = {}
    mail_config['mail.on'] = config['turbomail']['enable']
    mail_config['mail.manager'] = config['turbomail']['manager']
    mail_config['mail.transport'] = config['turbomail']['transport']
    mail_config['mail.smtp.server'] = config['turbomail']['server']

    sender = config['turbomail']['sender']
    """
    rand send email 
    """
    day_str = datetime.datetime.strftime(datetime.datetime.today(),"%d%H")
    sender = 'Knowing <Knowing-noreply-%s@dm.anjuke.com>' % day_str

    subject = message

    u = session.query(Users).filter(Users.username == chart.owner)

    addressee = ''
    if u:
        for i in u:
            if i.mobile:
                addressee = i.mobile + '@139.com'
            else:
                logger.warning("no mobile set for user \"%s\"" % i.username)
                return

    interface.start(mail_config)
    now = str(datetime.datetime.now())[0:19]

    chart_url = 'http://knowing.corp.anjuke.com/chart/%d' % chart.id

    html_part = u"<html><body><h1>Look, %s</h1><p>时间: %s</p><p>详细信息: %s</p><p><a href='%s'>%s</a></p><p>This mail is sent by Knowing</p></body></html>"
    html_part %= (chart.name, now, message, chart_url, chart_url)
    text_part = u"[critical] 时间: %s 详细信息: %s"
    text_part %= (now, message)

    mail = Message(sender, addressee, subject)
    mail.encoding = 'utf-8'
    mail.plain = message
    mail.rich = html_part
    flag = mail.send()

def add_events(chart, level, message):

    if level not in (CONST_LEVEL_WARNING, CONST_LEVEL_CRITICAL):
        return

    type = 0 if level == CONST_LEVEL_WARNING else 0

    event = Events()
    event.cid = chart.id
    event.info = message
    event.time = datetime.datetime.now()
    event.type = type
    event.deal_status = 0 # not dealed
    session.add(event)
    session.flush()

def __get_config(name='webapp'):

    config_file = root_path + "/sakuya/config/%s.yml" % name

    content = ''
    with open(config_file, 'r') as f:
        content = f.read()

    _env = os.environ.get('BOTTLE_ENV', 'development')

    return yaml.load(content)[_env]

def main():
    logger.debug("alert job started.")
    compare_and_notify()

if __name__ == '__main__':
    sys.exit(main())
