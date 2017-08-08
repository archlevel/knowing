# -*- coding: utf-8 -*-

import msgpack
import zmq
import json
import traceback
import datetime
from bottle import request
from sakuya import app
from sakuya.lib import util, storm, chart as libchart
from sakuya.config import get_config
from sakuya.models.sakuya_db import ChartdataTmpl, LogstuffTmpl, Charts, Categories

SOLR_CATE_ID = 200

@app.post('/api/add-data')
def add_data(sakuya_db):

    try:
        tid = int(request.forms['tid'])
        chart = sakuya_db.query(Charts).get(tid)
        if chart is None:
            raise ValueError

        dt = datetime.datetime.strptime(request.forms['dt'], '%Y-%m-%d %H:%M')

        data = request.forms.get('data', None)
        detail = request.forms.get('detail', None)
        if data is None and detail is None:
            raise ValueError

        if data is not None:
            data = int(data)

        if detail is not None and len(detail) == 0:
            detail = None

    except Exception, e:
        return util.output('error', msg='Invalid params.')

    try:
        if data is not None:
            row = ChartdataTmpl.gen(dt.strftime('%Y%m%d'))()
            row.ds_id = tid
            row.time = dt
            row.data = data
            sakuya_db.add(row)

        if detail is not None:
            row = LogstuffTmpl.gen(dt.strftime('%Y%m%d'))()
            row.ds_id = tid
            row.time = dt
            row.detail = detail
            sakuya_db.add(row)

        sakuya_db.commit()

    except Exception, e:
        sakuya_db.rollback()
        traceback.print_exc()
        return util.output('error', msg='Internal error.')

    try:
        chart.api_ip = util.ip2long(request['REMOTE_ADDR'])
        chart.api_ts = util.timestamp()
        sakuya_db.commit()

    except Exception, e:
        sakuya_db.rollback()

    return util.output('ok')

socket = zmq.Socket(zmq.Context.instance(), zmq.PUSH)
socket.connect(get_config('webapp')['hp_aggregate_connect'])

@app.post('/api/haopan')
def haopan(sakuya_db):

    try:
        dt = datetime.datetime.strptime(request.forms['time'], '%Y-%m-%d %H:%M')
        data = json.loads(request.forms['data'])
        if not isinstance(data[0], list) or len(data[0]) < 6:
            raise ValueError
    except Exception:
        return util.output('error', msg='Invalid parameters.')

    dtstr = dt.strftime('%Y-%m-%d %H:%M')

    with open(get_config('webapp')['hp_raw_data'], 'a') as f:
        f.write('time: %s\n' % dtstr)
        f.write('data:\n')
        for item in data:
            f.write('%s\n' % str(item))
        f.write('\n')

    socket.send(msgpack.packb({
        'time': dtstr,
        'data': data
    }))

    return util.output('ok', msg='%s, %d items received.' % (dtstr, len(data)))

@app.post('/api/solr/add')
def solr_add(sakuya_db):

    # parse parameters
    try:
        title = request.forms['title']
        if not title:
            raise ValueError

        rule_type = request.forms['type']
        if rule_type not in ('count', 'ninety'):
            raise ValueError

        filters = []
        datasource = storm.datasources['access_log']
        for filter in json.loads(request.forms['filters']):
            if filter[0] not in datasource:
                raise ValueError

            field_type = datasource[filter[0]][0]

            if filter[1] not in storm.operators[field_type][0]:
                raise ValueError

            if not filter[2]:
                raise ValueError

            if field_type == 'string':
                if filter[1] == 'in':
                    if not isinstance(filter[2], list):
                        raise ValueError
                    filter[2] = [str(i) for i in filter[2]]
                else:
                    filter[2] = str(filter[2])

            elif field_type == 'numeric':
                if filter[1] in ('in', 'nin'):
                    if not isinstance(filter[2], list):
                        raise ValueError
                    tmp_filter2 = []
                    for i in filter[2]:
                        i = float(i)
                        if i.is_integer():
                            i = int(i)
                        tmp_filter2.append(i)
                    filter[2] = tmp_filter2
                else:
                    filter[2] = float(filter[2])
                    if filter[2].is_integer():
                        filter[2] = int(filter[2])

            else:
                assert False

            filters.append(filter[:3])

        if not filters:
            raise ValueError

    except Exception, e:
        return util.output('error', msg='Invalid parameters.')

    # make rule
    rule = {
        'datasource': 'access_log',
        'rule_type': rule_type
    }
    if rule_type == 'ninety':
        rule['field'] = 'upstream_response_time'
    else:
        rule['field'] = None
    rule['filters'] = []
    for filter in filters:
        rule['filters'].append([filter[0], filter[1], False, filter[2]])

    # add to database
    row = Charts()
    row.name = title
    row.owner = '系统'
    row.cate_id = SOLR_CATE_ID
    row.ext_info = json.dumps({'rule': rule})
    row.createtime = datetime.datetime.now()
    sakuya_db.add(row)
    sakuya_db.flush()
    id = row.id
    sakuya_db.commit()

    # set storm
    storm.set_rule(id, json.dumps(rule))

    # return id
    return util.output('ok', id=id)

@app.get('/api/solr/delete/<id:int>')
def solr_delete(sakuya_db, id):

    row = sakuya_db.query(Charts).filter_by(id=id, cate_id=SOLR_CATE_ID).first()
    if row is None:
        return util.output('error', msg='Chart not found.')

    sakuya_db.delete(row)
    sakuya_db.commit()

    storm.delete_rule(id)

    return util.output('ok')

@app.post('/api/suite-data')
def suite_data(sakuya_db):

    try:
        body = json.loads(request.body.getvalue())
        category, data, dt = body['category'], body['data'], body['datetime']
        if len(category) < 3 or not data:
            raise ValueError
        dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M')

    except Exception, e:
        return util.output('error', msg='Invalid parameters.')

    pid = libchart.SUITE_PID
    for i in xrange(len(category)):

        cate = sakuya_db.\
               query(Categories).\
               filter_by(parent_cate_id=pid, name=category[i]).\
               first()

        if cate is None:
            cate = Categories()
            cate.name = category[i]
            cate.parent_cate_id = pid
            cate.is_parent = i < 2
            sakuya_db.add(cate)
            sakuya_db.commit()

        pid = cate.id # after loop the pid will be the lowest level category

    dt_date = dt.strftime('%Y%m%d')
    Chartdata = ChartdataTmpl.gen(dt_date)
    Logstuff = LogstuffTmpl.gen(dt_date)
    for k, v in data.iteritems():

        title_segs = list(category)
        title_segs.append(str(k))
        title = '::'.join(title_segs)

        chart = sakuya_db.\
                query(Charts).\
                filter_by(cate_id=pid, name=title).\
                first()

        if chart is None:
            chart = Charts()
            chart.name = title
            chart.owner = '系统 (Suite API)'
            chart.cate_id = pid
            chart.createtime = datetime.datetime.now()
            sakuya_db.add(chart)
            sakuya_db.commit()

        if isinstance(v, list):
            try:
                value, detail = v
            except Exception, e:
                continue

        else:
            value, detail = v, None

        row = Chartdata()
        row.ds_id = chart.id
        row.time = dt
        row.data = value
        sakuya_db.add(row)

        if detail is not None:
            row = Logstuff()
            row.ds_id = chart.id
            row.time = dt
            row.detail = detail
            sakuya_db.add(row)

        sakuya_db.commit()

    return util.output('ok')

def check_api_key():
    if request.forms['api_key'] != 'apirocks':
        raise ValueError('Invalid api_key.')

IAPI_CATE_ID = (335, 336)

@app.post('/api/internal/add')
def internal_add(sakuya_db):

    try:
        check_api_key()

        name = request.forms['name']
        if not name:
            raise ValueError('Name cannot be empty.')

        cate_id = int(request.forms['cate_id'])
        if cate_id not in IAPI_CATE_ID:
            raise ValueError('Invalid cate_id')

    except KeyError, e:
        return util.output('error', msg='Missing parameter %s.' % e)

    except Exception, e:
        return util.output('error', msg=str(e))

    chart = Charts()
    chart.name = name
    chart.cate_id = cate_id
    chart.owner = 'alexzhu'
    chart.createtime = datetime.datetime.now()
    sakuya_db.add(chart)
    sakuya_db.flush()
    id = chart.id
    sakuya_db.commit()

    return json.dumps({'status': 'ok', 'id': id})

@app.post('/api/internal/delete')
def internal_delete(sakuya_db):

    try:
        check_api_key()

        id = int(request.forms['id'])
        chart = sakuya_db.query(Charts).get(id)
        if chart is None:
            raise ValueError('Chart not found.')
        if chart.cate_id not in IAPI_CATE_ID:
            raise ValueError('Authentication failed.')

    except KeyError, e:
        return util.output('error', msg='Missing parameter %s.' % e)

    except Exception, e:
        return util.output('error', msg=str(e))

    sakuya_db.delete(chart)
    sakuya_db.commit()

    return json.dumps({'status': 'ok'})
