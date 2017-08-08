# -*- coding: utf-8 -*-

import time
import traceback
import datetime
import json
import math
from bottle import request, abort
from sakuya import app, view
from sakuya.models.sakuya_db import Charts, Follows, Users, Events, Categories
from sakuya.models.sakuya_db import ChartdataTmpl, ChartdataWeekly, ChartdataMonthly, ChartdataQuarterly
from sakuya.lib import auth, util, haopan, storm, warn
from sakuya.lib import chart as libchart
from sakuya.controllers import category as category_controller
from sakuya.config import get_config

@app.get('/chart/<id:int>')
@app.get('/chart/<id:int>/<id2:int>')
@view('chart')
def chart(sakuya_db, id, id2=None):

    chart_info = sakuya_db.query(Charts).get(id)
    if chart_info is None:
        abort(404)

    chart_info2 =[]
    if id2:
        chart_info2 = sakuya_db.query(Charts).get(id2)

    title = chart_info.name 
    is_haopan = haopan.is_haopan(chart_info.cate_id)
    
    rt = {
        'id': str(id),
        'is_haopan': is_haopan,
        'createtime': chart_info.createtime.strftime('%Y-%m-%d %H:%M:%S')
    }

    rt['is_admin'] = auth.is_role('admin')
    rt['is_admin'] = True
    rt['status'] = chart_info.status
    '''
    more chart line
    '''
    if is_haopan is False:
        if chart_info2:
            is_haopan = True

            title = chart_info2.name
            rt['is_haopan'] = True
            rt['t1_title'] = u'当日'+chart_info.name
            rt['t2_title'] = u'当日'+chart_info2.name
            rt['t3_title'] = u'上周'+chart_info.name
            rt['t4_title'] = u'上周'+chart_info2.name

    else:
        title=haopan.format_title(chart_info.name)
        rt['t1_title'] = u'当日有效点击'
        rt['t2_title'] = u'当日无效点击'
        rt['t3_title'] = u'上周有效点击'
        rt['t4_title'] = u'上周无效点击'
        id2 = haopan.get_id2(chart_info.id)

    if is_haopan:
        rt['title'] = title#haopan.format_title(chart_info.name)
        rt['id2'] = id2#haopan.get_id2(chart_info.id)
        rt['owner'] = '系统'

    else:
        rt['title'] = title

        # owner
        owner = sakuya_db.query(Users).filter_by(username=chart_info.owner).first()
        if owner is not None:
            rt['owner'] = owner.truename
        else:
            rt['owner'] = '未知'

        # datasource
        try:
            ext_info = json.loads(chart_info.ext_info)
            if 'rule' in ext_info:
                ruc = ext_info['rule']
                storm_info = {
                    'datasource': ruc['datasource'],
                    'rule_type': storm.rule_types[ruc['rule_type']][0]
                }
                if storm.rule_types[ruc['rule_type']][1]:
                    storm_info['field'] = ruc['field']

                storm_info['filters'] = []
                for item in ruc['filters']:

                    storm_info['filters'].append({
                        'field': item[0],
                        'operator': storm.operators[storm.datasources[ruc['datasource']][item[0]][0]][0][item[1]],
                        'negative': item[2],
                        'content': item[3]
                    })

                rt['storm_info'] = storm_info

            elif chart_info.api_ip and chart_info.api_ts:
                rt['api_ip'] = util.long2ip(chart_info.api_ip)
                rt['api_ts'] = datetime.datetime.fromtimestamp(chart_info.api_ts).strftime('%Y-%m-%d %H:%M:%S')

        except Exception, e:
            pass

    # alert info
    if chart_info.alert_enable:
        rt['alert_info'] = warn.get_warn(sakuya_db, id)

        # Show subscribers for respective warning rule.
        rule_subscribers = dict((i['id'], []) for i in rt['alert_info'])
        for row in sakuya_db.\
                   query(Follows).\
                   filter_by(cid=chart_info.id).\
                   filter_by(recv_warning=True):
            if not row.recv_rules:
                continue
            tmp_user = sakuya_db.query(Users).get(row.follower)
            if tmp_user is None:
                continue
            if row.recv_rules == 'all':
                for k, v in rule_subscribers.iteritems():
                    v.append(tmp_user.truename)
            else:
                for i in row.recv_rules.split(','):
                    try:
                        i = int(i)
                    except Exception, e:
                        continue
                    if i in rule_subscribers:
                        rule_subscribers[i].append(tmp_user.truename)

        for item in rt['alert_info']:
            if rule_subscribers[item['id']]:
                item['subscriber'] = u'，'.join(rule_subscribers[item['id']])
            else:
                item['subscriber'] = '无'

        rt['warning_logs'] = []
        for row in sakuya_db.\
                   query(Events).\
                   filter_by(cid=id).\
                   filter(Events.type > 0).\
                   order_by(Events.time.desc()).\
                   limit(20):

            rt['warning_logs'].append({
                'id': row.id,
                'level': 'critical' if row.type == Events.CONST_TYPE_CRITICAL else 'warning',
                'content': row.info,
                'time': row.time.strftime('%Y-%m-%d %H:%M')
            })
    
    # initial start/end time
    now = datetime.datetime.now()
    def before_days(days):
        tmp_dt = now + datetime.timedelta(days=days)
        return tmp_dt.strftime('%Y-%m-%d')
    rt['dt_range'] = dict((days, before_days(days)) for days in [0, -1, -2, -6, -14, -29])

    # whether followed
    user = auth.get_user()
    if user is not None:
        follow = sakuya_db.query(Follows).filter_by(cid=id, follower=user['userid']).first()
        if follow is not None:
            rt['following'] = True
            if follow.recv_warning:
                rt['recv_warning'] = True
                rt['recv_rules'] = follow.get_recv_rules()
            else:
                rt['recv_warning'] = False
        else:
            rt['following'] = False
    else:
        rt['following'] = False

    # authorization
    if auth.is_role('sa'):
        rt['editable'] = True
        rt['deletable'] = not is_haopan
    elif auth.is_role('haopan') and is_haopan:
        rt['editable'] = True
        rt['deletable'] = False
    elif user and user['username'] == chart_info.owner:
        rt['editable'] = True
        rt['deletable'] = False
    else:
        rt['editable'] = False

    # breadcrumbs
    rt['active_tab'] = None
    rt['breadcrumbs'] = []
    category_path = libchart.get_category_path(sakuya_db, chart_info.cate_id)
    if len(category_path) > 1:
        category_path.popleft() # pop root category
        if category_path[0][0] in category_controller.PID_TAB_D:
            category_links = [category_controller.PID_TAB_D[category_path[0][0]]]
            rt['active_tab'] = category_links[0]
            rt['breadcrumbs'].append({
                'link': '/' + category_links[0],
                'name': category_path[0][1]
            })
            category_path.popleft() # pop monitor/speed/security category
            for item in category_path:
                category_links.append(str(item[0]))
                rt['breadcrumbs'].append({
                    'link': '/%s' % '/'.join(category_links),
                    'name': item[1]
                })

    # category list for ack function
    cl2s = []
    cl3s = {}
    for cl1_id in (2, 3, 4):
        cl1 = sakuya_db.query(Categories).get(cl1_id)
        for cl2 in sakuya_db.query(Categories).filter_by(parent_cate_id=cl1.id):
            cl2s.append((cl2.id, cl1.name + ' / ' + cl2.name))
            cl3s[cl2.id] = []
            for cl3 in sakuya_db.query(Categories).filter_by(parent_cate_id=cl2.id):
                cl3s[cl2.id].append((cl3.id, cl3.name))
                if cl3.id == chart_info.cate_id:
                    rt['cur_cl2'] = cl2.id
                    rt['cur_cl3'] = cl3.id
    rt['cl2s'] = cl2s
    rt['cl3s'] = cl3s
    rt['cl3s_json'] = json.dumps(cl3s)

    return rt

@app.get('/chart/hide/<id:int>')
@auth.login
def hide(sakuya_db, id):
    try:
        
        if auth.is_role('admin') is False:
            return util.output('error', msg='Role Error.')

        chart = sakuya_db.query(Charts).get(id)
        if chart is None:
            return util.output('error', msg='Chart not found.')

        status = int(request.params['status'])

        chart.status = status
        sakuya_db.commit()

        return util.output('ok')

    except Exception:
        traceback.print_exc()
        sakuya_db.rollback()
        return util.output('error', msg='隐藏失败')


@app.get('/chart/follow/<id:int>')
@auth.login
def follow(sakuya_db, id):

    try:
        chart = sakuya_db.query(Charts).get(id)
        if chart is None:
            return util.output('error', msg='Chart not found.')

        user = auth.get_user()

        follow = sakuya_db.query(Follows).filter_by(cid=id, follower=user['userid']).first()
        if follow is None:
            follow = Follows()
            follow.cid = id
            follow.follower = user['userid']
            follow.recv_warning = False
            sakuya_db.add(follow)

            if not chart.followers:
                chart.followers = 1
            else:
                chart.followers += 1

            sakuya_db.commit()

        return util.output('ok')

    except Exception:
        traceback.print_exc()
        sakuya_db.rollback()
        return util.output('error', msg='订阅失败')

@app.get('/chart/unfollow/<id:int>')
@auth.login
def unfollow(sakuya_db, id):

    try:
        chart = sakuya_db.query(Charts).get(id)
        if chart is None:
            return util.output('error', msg='Chart not found.')

        user = auth.get_user()

        row = sakuya_db.query(Follows).filter_by(cid=id, follower=user['userid']).first()
        if row is not None:
            sakuya_db.delete(row)

            if chart.followers:
                chart.followers -= 1

            sakuya_db.commit()

        return util.output('ok')

    except Exception:
        traceback.print_exc()
        sakuya_db.rollback()
        return util.output('error', msg='取消失败')

@app.get('/chart/recv_warning')
@auth.login
def recv_warning(sakuya_db):

    try:
        chart_id = int(request.params['chart_id'])
        recv_rules = request.params['recv_rules']

    except Exception, e:
        return util.output('error', msg='参数不正确')

    user = auth.get_user()
    row = sakuya_db.query(Follows).filter_by(cid=chart_id, follower=user['userid']).first()
    if row is None:
        return util.output('error', msg='没有订阅图表')

    if recv_rules == 'all':
        row.recv_warning = True
        row.recv_rules = 'all'
    else:
        tmp = []
        for i in recv_rules.split(','):
            try:
                tmp.append(int(i))
            except Exception:
                pass
        row.recv_warning = bool(tmp)
        row.recv_rules = ','.join(str(i) for i in tmp)

    sakuya_db.commit()
    return util.output('ok')

@app.get('/chart/data')
def chart_data(sakuya_db):

    try:
        id_list = [int(i) for i in request.params['id_list'].split(',')]
        delta_list = [int(i) for i in request.params['delta_list'].split(',')]
        if len(id_list) != len(delta_list):
            raise ValueError

        dt_start = datetime.datetime.strptime(request.params['start'], '%Y-%m-%d %H:%M')
        dt_end = datetime.datetime.strptime(request.params['end'], '%Y-%m-%d %H:%M')
        if dt_end - dt_start < datetime.timedelta(minutes=5):
            dt_end = dt_start + datetime.timedelta(minutes=5)

        daily = request.params.get('daily') == 'true'
        if daily and dt_end - dt_start < datetime.timedelta(days=7):
            dt_end = dt_start + datetime.timedelta(days=7)

    except Exception, e:
        return util.output('error', msg='参数不正确')

    chart_list = []
    for index, id in enumerate(id_list):
        chart_list.append([id, datetime.timedelta(days=delta_list[index])])

    data = libchart.get_chart_data(sakuya_db, dt_start, dt_end, chart_list, daily=daily)

    result = []
    for dt_key, series in data.iteritems():
        dt = datetime.datetime.strptime(dt_key, '%Y%m%d%H%M')
        item = [int(time.mktime(dt.timetuple())) * 1000]
        #series = [1,2,4,5]
        item.extend(series)
        result.append(item)
    
    return json.dumps(result)

@app.post('/chart/ack/<id:int>')
def ack(sakuya_db, id):

    def error(msg):
        return {'status': 'error', 'msg': msg}

    def log(chart, category):
        with open(get_config('webapp')['chart_ack_log'], 'a') as f:
            l = u'[%s] user: %s, chart: %d-%s, category: %d-%s\n' %\
                (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 auth.get_user()['username'],
                 chart.id, chart.name,
                 category.id, category.name)
            f.write(l.encode('utf-8'))

    chart = sakuya_db.query(Charts).get(id)
    if chart is None:
        return error('图表不存在')

    if haopan.is_haopan(chart.cate_id):
        return error('栏目不正确')

    if 'cl2' in request.params: # create category and move into it
        cl2 = sakuya_db.query(Categories).get(request.params['cl2'])
        if cl2 is None:
            return error('参数不正确')

        cl3_name = request.params.get('cl3')
        if not cl3_name:
            return error('栏目名称不能为空')

        cl3_exists = sakuya_db.query(Categories).\
                     filter_by(parent_cate_id=cl2.id, name=cl3_name).\
                     count() > 0
        if cl3_exists:
            return error('栏目已存在')

        cl3 = Categories()
        cl3.name = cl3_name
        cl3.parent_cate_id = cl2.id
        cl3.is_parent = False
        sakuya_db.add(cl3)
        sakuya_db.commit()

        chart.cate_id = cl3.id
        chart.owner = auth.get_user()['username']
        sakuya_db.commit()

    else: # move to category
        cl3 = sakuya_db.query(Categories).get(request.params.get('cl3'))
        if cl3 is None:
            return error('栏目不存在')

        chart.cate_id = cl3.id
        chart.owner = auth.get_user()['username']
        sakuya_db.commit()

    log(chart, cl3)
    return {'status': 'ok'}
