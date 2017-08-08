# -*- coding: utf-8 -*-

from collections import OrderedDict
from bottle import abort, redirect
from sakuya import app, view
from sakuya.models.sakuya_db import Charts, Categories, Follows
from sakuya.lib import auth,util, chart as libchart

ANJUKE_CID = 11 # for haopan

MONITOR_PID = 2
SPEED_PID = 3
SECURITY_PID = 4

TAB_PID_D = {
    'monitor': MONITOR_PID,
    'speed': SPEED_PID,
    'security': SECURITY_PID
}
PID_TAB_D = util.invert_dict(TAB_PID_D)

TAB_PID_PREFIX = '/<tab:re:(%s)>' % '|'.join(TAB_PID_D.keys())

@app.get(TAB_PID_PREFIX)
@app.get(TAB_PID_PREFIX + '/<cate1:int>')
@app.get(TAB_PID_PREFIX + '/<cate1:int>/<cate2:int>')
@view('monitor')
def monitor(sakuya_db, tab, cate1=None, cate2=None):

    lv1_list = OrderedDict()
    for row in sakuya_db.\
               query(Categories).\
               filter_by(parent_cate_id=TAB_PID_D[tab]).\
               order_by(Categories.id):

        lv1_list[row.id] = {
            'id': row.id,
            'name': row.name
        }

    if not lv1_list:
        redirect('/')

    if cate1 is None:
        cate1 = lv1_list.keys()[0]
    elif cate1 not in lv1_list:
        return abort(404)

    rt = {
        'lv1_list': lv1_list.values(),
        'cate1': lv1_list[cate1]
    }

    lv2_list = OrderedDict()
    for row in sakuya_db.\
               query(Categories).\
               filter_by(parent_cate_id=cate1).\
               order_by(Categories.id):

        lv2_list[row.id] = {
            'id': row.id,
            'name': row.name
        }

    if not lv2_list:
        redirect('/')

    if cate2 is None:
        cate2 = lv2_list.keys()[0]
    elif cate2 not in lv2_list:
        return abort(404)

    rt['lv2_list'] = lv2_list.values()
    rt['cate2'] = lv2_list[cate2]

    chart_list = []
    is_admin = auth.is_role('admin')

    if is_admin:
        rows = sakuya_db.query(Charts).filter_by(cate_id=cate2).order_by(Charts.id)
    else:
        rows = sakuya_db.query(Charts).filter_by(cate_id=cate2,status=1).order_by(Charts.id)

    for row in rows:

        chart_list.append({
            'id': row.id,
            'name': row.name
        })

    rt['chart_list'] = chart_list
    rt['millitime'] = util.millitime()
    rt['anjuke_cid'] = ANJUKE_CID
    rt['tab'] = tab

    if cate1 == libchart.OPS_PID:
        _, rt['ops_list'] = libchart.get_category_tab(sakuya_db, [libchart.SUITE_PID], 1)

    return rt
