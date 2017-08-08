# -*- coding: utf-8 -*-

import datetime
from collections import OrderedDict, deque
from bottle import abort
from sakuya.models.sakuya_db import Categories, ChartdataTmpl, ChartdataDaily
from sakuya.models.sakuya_db import ChartdataWeekly, ChartdataMonthly, ChartdataQuarterly

MONITOR_PID = 2
OPS_PID = 125

SUITE_PID = 300

def get_category_path(sakuya_db, id):

    category_path = deque()

    _id = id
    while _id > 0:
        row = sakuya_db.query(Categories).get(_id)
        if row is None:
            break
        category_path.appendleft((row.id, row.name))
        _id = row.parent_cate_id

    return category_path

def get_category_tab(sakuya_db, id_path, level):

    pid = id_path[0]
    lv_list = deque()
    cate = deque()

    for lv in xrange(level):

        lv_list.append(OrderedDict())

        for row in sakuya_db.\
                   query(Categories).\
                   filter_by(parent_cate_id=pid).\
                   order_by(Categories.order).\
                   order_by(Categories.id):

            lv_list[lv][row.id] = {
                'id': row.id,
                'name': row.name
            }

        if not lv_list[lv]:
            break

        if len(id_path) > lv + 1 and id_path[lv + 1] is not None:
            pid = id_path[lv + 1]
            if pid not in lv_list[lv]:
                break
        else:
            pid = lv_list[lv][lv_list[lv].keys()[0]]['id']

        cate.append(lv_list[lv][pid])

    cate.appendleft(None)
    lv_list.appendleft(None)

    return cate, lv_list

def get_category_list(sakuya_db):

    categories = []
    st = []

    def dig(id):
        row = sakuya_db.query(Categories).get(id)

        if id > 1:
            st.append(row.name)

        if row.is_parent:
            for child in sakuya_db.query(Categories).filter_by(parent_cate_id=row.id):
                dig(child.id)
        else:
            categories.append((row.id, ' / '.join(st)))

        if id > 1:
            st.pop()

    dig(1)

    return categories

def get_chart_data(sakuya_db, dt_start, dt_end, charts, compzero=False, daily=False):
    '''
    charts:
      - [id, delta]

    return:
      - OrderedDict('%Y-%m-%d %H:%M'=[series1, series2, ...])
    '''

    # fill data into datetime bucket
    def get_data(id, model, data, index, start, end, delta=None):

        for row in sakuya_db.\
                   query(model).\
                   filter_by(ds_id=id).\
                   filter(model.time >= start).\
                   filter(model.time <= end):

            if delta is None:
                tmp_time = row.time
            else:
                tmp_time = row.time - delta

            dt_key = tmp_time.strftime('%Y%m%d%H%M')
            if dt_key in data:
                data[dt_key][index] = row.data

    # datetime bucket
    data = OrderedDict()

    # based on different time delta
    if daily:
        dt_delta = datetime.timedelta(days=31)
    else:
        dt_delta = dt_end - dt_start

    if dt_delta <= datetime.timedelta(days=1):

        # fill datatime bucket
        curdt = dt_start
        while curdt <= dt_end:
            dt_key = curdt.strftime('%Y%m%d%H%M')
            if compzero:
                data[dt_key] = [0] * len(charts)
            else:
                data[dt_key] = [None] * len(charts)
            curdt += datetime.timedelta(minutes=1)

        # fill data
        for index, chart in enumerate(charts):

            if chart[1] is None:
                tmp_dt_start = dt_start
                tmp_dt_end = dt_end
            else:
                tmp_dt_start = dt_start + chart[1]
                tmp_dt_end = dt_end + chart[1]

            get_data(chart[0], ChartdataTmpl.gen(tmp_dt_start.strftime('%Y%m%d')), data, index, tmp_dt_start, tmp_dt_end, chart[1])
            get_data(chart[0], ChartdataTmpl.gen(tmp_dt_end.strftime('%Y%m%d')), data, index, tmp_dt_start, tmp_dt_end, chart[1])

    else:

        if dt_delta <= datetime.timedelta(days=5):
            minutes = 5
            model = ChartdataWeekly
        elif dt_delta <= datetime.timedelta(days=15):
            minutes = 15
            model = ChartdataMonthly
        elif dt_delta <= datetime.timedelta(days=30):
            minutes = 30
            model = ChartdataQuarterly
        else:
            minutes = 1440
            model = ChartdataDaily

        curdt = dt_start
        if minutes < 60:
            adjust_min = curdt.minute % minutes
            if adjust_min > 0:
                curdt -= datetime.timedelta(minutes=adjust_min)
        else:
            curdt = curdt.replace(hour=0, minute=0, second=0, microsecond=0)

        while curdt <= dt_end:
            dt_key = curdt.strftime('%Y%m%d%H%M')
            if compzero:
                data[dt_key] = [0] * len(charts)
            else:
                data[dt_key] = [None] * len(charts)
            curdt += datetime.timedelta(minutes=minutes)

        for index, chart in enumerate(charts):

            if chart[1] is None:
                tmp_dt_start = dt_start
                tmp_dt_end = dt_end
            else:
                tmp_dt_start = dt_start + chart[1]
                tmp_dt_end = dt_end + chart[1]

            get_data(chart[0], model, data, index, tmp_dt_start, tmp_dt_end, chart[1])

    # cleanup newest data
    for index in xrange(len(charts)):
        for dt_key in reversed(data.keys()):
            if data[dt_key][index] == 0:
                data[dt_key][index] = None
            else:
                break

    return data
