# -*- coding: utf-8 -*-

import datetime
import msgpack
from collections import OrderedDict
from bottle import abort, request
from sakuya import app, view
from sakuya.config import get_config
from sakuya.lib import util, haopan
from sakuya.models.sakuya_db import Categories

MONITOR_PID = 2
ANJUKE_CID = 11

@app.get('/monitor/haopan/<prod:int>')
@view('haopan')
def monitor(sakuya_db, prod):

    if prod not in haopan.D_PRODS:
        abort(404)

    rt = {
        'prod': prod,
        'cities': haopan.CITIES,
        'channels': haopan.CHANNELS,
        'entries': haopan.ENTRIES
    }

    lv1_list = OrderedDict()
    for row in sakuya_db.\
               query(Categories).\
               filter_by(parent_cate_id=MONITOR_PID).\
               order_by(Categories.id):

        lv1_list[row.id] = {
            'id': row.id,
            'name': row.name
        }

    rt['cate1'] = lv1_list[ANJUKE_CID]
    rt['lv1_list'] = lv1_list.values()

    lv2_list = OrderedDict()
    for row in sakuya_db.\
               query(Categories).\
               filter_by(parent_cate_id=rt['cate1']['id']).\
               order_by(Categories.id):

        lv2_list[row.id] = {
            'id': row.id,
            'name': row.name
        }

    rt['lv2_list'] = lv2_list.values()
    rt['anjuke_cid'] = ANJUKE_CID

    return rt

@app.get('/monitor/haopan/charts')
def haopan_charts(sakuya_db):

    try:
        prod = int(request.params['prod'])
        cities = [int(i) for i in request.params['cities'].split(',')]
        channels = [int(i) for i in request.params['channels'].split(',')]
        entries = [int(i) for i in request.params['entries'].split(',')]
        charts = [int(i) for i in request.params['charts'].split(',')]

    except Exception:
        return util.output('error', msg='Invalid parameters.')

    d_charts = haopan.get_charts()
    chart_list = []
    for k, v in d_charts.iteritems():
        if k[0] == prod\
                and k[1] in charts\
                and k[2] in cities\
                and k[3] in channels\
                and k[4] in entries:

            titles = []
            if k[2]:
                titles.append(haopan.D_CITIES[k[2]])
            if k[3]:
                titles.append(haopan.D_CHANNELS[k[3]])
            if k[4]:
                titles.append(haopan.D_ENTRIES[k[4]])
            titles.append(haopan.D_CHARTS_DISPLAY[k[1]])

            if k[1] == 2:
                k_ = list(k); k_[1] = 3; k_ = tuple(k_)
                if k_ in d_charts:
                    chart_list.append((' - '.join(titles), '%d/%d' % (v, d_charts[k_])))
                else:
                    chart_list.append((' - '.join(titles), v))
            else:
                chart_list.append((' - '.join(titles), v))

    return util.output('ok', charts=chart_list)
