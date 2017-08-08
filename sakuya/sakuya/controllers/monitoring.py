# -*- coding: utf-8 -*-

import json
from sakuya import app, view
from sakuya.lib import auth, haopan

from collections import OrderedDict
from sakuya.models.sakuya_db import Charts, Categories

TAB_PID_PREFIX = '/monitoring'
@app.get(TAB_PID_PREFIX)
@app.get(TAB_PID_PREFIX + '/<cate1:int>')
@app.get(TAB_PID_PREFIX + '/<cate1:int>/<cate2:int>')
@view('monitoring')
def monitoring(sakuya_db, cate1=None, cate2=None):
    cate = ''
    if cate1 is not None:
        cate = '/'+str(cate1)
        if cate2 is not None:
            cate += '/'+str(cate2)
    return {'cate':cate}

TAB_PID_PREFIX = '/monitoring/get_charts'
@app.get(TAB_PID_PREFIX)
@app.get(TAB_PID_PREFIX + '/<cate1:int>')
@app.get(TAB_PID_PREFIX + '/<cate1:int>/<cate2:int>')
def get_charts(sakuya_db, cate1=None, cate2=None):
    lv2_list = OrderedDict()
    if cate1 is not None:
        for row in sakuya_db.\
                   query(Categories).\
                   filter_by(parent_cate_id=cate1).\
                   order_by(Categories.id):

            lv2_list[row.id] = {
                'id': row.id,
                'name': row.name
            }

    if cate2 is None:
        cate2 = lv2_list.keys()
    elif cate2 in lv2_list:
        cate2 = [cate2]
    else:
        cate2 = []

    is_admin = auth.is_role('admin')

    if cate2:
        if is_admin:
            rows = sakuya_db.query(Charts).\
                   filter(Charts.cate_id.in_(cate2)).\
                   order_by(Charts.criticals.desc(), Charts.id)
        else:
            rows = sakuya_db.query(Charts).\
                   filter(Charts.cate_id.in_(cate2), Charts.status==1).\
                   order_by(Charts.criticals.desc(), Charts.id)
    else:
        if is_admin:
            rows = sakuya_db.query(Charts).\
                   filter_by(alert_enable=1).\
                   order_by(Charts.criticals.desc(), Charts.id)
        else:
            rows = sakuya_db.query(Charts).\
                   filter_by(alert_enable=1, status=1).\
                   order_by(Charts.criticals.desc(), Charts.id)

    result = []
    for row in rows:
        if haopan.is_haopan(row.cate_id):
            title = haopan.format_title(row.name)
        else:
            title = row.name

        result.append({
            'id': row.id,
            'name': title,
            'critical': row.criticals > 0
        })
    return json.dumps(result)
