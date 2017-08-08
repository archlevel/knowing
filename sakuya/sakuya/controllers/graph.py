# -*- coding: utf-8 -*-

import datetime
from collections import OrderedDict
from bottle import request, response, abort
from sakuya import app
from sakuya.models.sakuya_db import Charts, ChartdataTmpl, ChartdataWeekly, ChartdataMonthly, ChartdataQuarterly
from sakuya.lib import graph as libgraph

@app.get('/graph/<id>')
def graph(sakuya_db, id):
    chart_info = sakuya_db.query(Charts).filter_by(id=id).first()

    date_start = request.params.get('date_start')
    date_end = request.params.get('date_end')

    dt_start = datetime.datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
    dt_end = datetime.datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")

    # TODO determin tabletime accroding to timespan

    timedelta = dt_end - dt_start

    if timedelta.seconds <= 86400:
        # in a day
        td = datetime.date.today()
        tablename = 't_chartdata_%s' % dt_start.strftime('%Y%m%d')

    x = []
    y = []
    d = sakuya_db.execute("select f_time, f_data from %s where \
f_ds_id = :ds_id and f_time >= :start and f_time <= :end order by f_time" %
tablename, {"ds_id": chart_info.id, "start": date_start, "end": date_end})
    for r in d:
        x.append(r[0])
        y.append(r[1])

    # TODO auto adjust x axis unit and image size
    image = libgraph.draw_chart(x, y, size=(934, 297), xlim=(dt_start, dt_end))
    response.content_type = 'image/png'
    return image

@app.get('/graph/haopan/list/<id:int>')
@app.get('/graph/haopan/list/<id:int>/<id2:int>')
def haopan_list(sakuya_db, id, id2=None):

    def get_data(id, model, data, k, start, end, delta=None):

        for row in sakuya_db.\
                   query(model).\
                   filter_by(ds_id=id).\
                   filter(model.time >= start).\
                   filter(model.time <= end):

            if delta is None:
                tmp_time = row.time
            else:
                tmp_time = row.time + delta
            dtstr = tmp_time.strftime('%Y%m%d%H%M')
            if dtstr in data:
                data[dtstr][k] = row.data

    # parse start and end date
    try:
        dt_start = datetime.datetime.strptime(request.params['start'], '%Y-%m-%d %H:%M')
        dt_end = datetime.datetime.strptime(request.params['end'], '%Y-%m-%d %H:%M')
        if dt_start >= dt_end:
            raise ValueError
    except Exception:
        now = datetime.datetime.now()
        dt_end = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
        dt_start = dt_end - datetime.timedelta(hours=1)
        dt_end += datetime.timedelta(minutes=5)

    data = OrderedDict()

    delta = datetime.timedelta(days=7)
    dt_start_prev = dt_start - delta
    dt_end_prev = dt_end - delta

    dt_delta = dt_end - dt_start
    if dt_delta <= datetime.timedelta(days=1):

        curdt = dt_start
        while curdt <= dt_end:
            dt_key = curdt.strftime('%Y%m%d%H%M')
            init_num = 2 if id2 is None else 4
            if request.params.get('compzero') == '1':
                data[dt_key] = [0] * init_num
            else:
                data[dt_key] = [None] * init_num
            curdt += datetime.timedelta(minutes=1)

        # current data
        get_data(id, ChartdataTmpl.gen(dt_start.strftime('%Y%m%d')), data, 0, dt_start, dt_end)
        get_data(id, ChartdataTmpl.gen(dt_end.strftime('%Y%m%d')), data, 0, dt_start, dt_end)
        if id2 is not None:
            get_data(id2, ChartdataTmpl.gen(dt_start.strftime('%Y%m%d')), data, 2, dt_start, dt_end)
            get_data(id2, ChartdataTmpl.gen(dt_end.strftime('%Y%m%d')), data, 2, dt_start, dt_end)

        get_data(id, ChartdataTmpl.gen(dt_start_prev.strftime('%Y%m%d')), data, 1, dt_start_prev, dt_end_prev, delta)
        get_data(id, ChartdataTmpl.gen(dt_end_prev.strftime('%Y%m%d')), data, 1, dt_start_prev, dt_end_prev, delta)
        if id2 is not None:
            get_data(id2, ChartdataTmpl.gen(dt_start_prev.strftime('%Y%m%d')), data, 3, dt_start_prev, dt_end_prev, delta)
            get_data(id2, ChartdataTmpl.gen(dt_end_prev.strftime('%Y%m%d')), data, 3, dt_start_prev, dt_end_prev, delta)

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
            abort(400)

        curdt = dt_start
        while curdt.minute % minutes != 0:
            curdt += datetime.timedelta(minutes=1)
        while curdt <= dt_end:
            data[curdt.strftime('%Y%m%d%H%M')] = [0, 0] if id2 is None else [0, 0, 0, 0]
            curdt += datetime.timedelta(minutes=minutes)
        get_data(id, model, data, 0, dt_start, dt_end)
        get_data(id, model, data, 1, dt_start_prev, dt_end_prev, delta)
        if id2 is not None:
            get_data(id2, model, data, 2, dt_start, dt_end)
            get_data(id2, model, data, 3, dt_start_prev, dt_end_prev, delta)

    # cleanup newest data
    for k in reversed(data.keys()):
        if data[k][0] == 0:
            data[k][0] = None
        else:
            break

    if id2 is not None:
        for k in reversed(data.keys()):
            if data[k][2] == 0:
                data[k][2] = None
            else:
                break

    # gen data
    ys = [[y[0] for y in data.values()], [y[1] for y in data.values()]]
    if id2 is not None:
        ys.extend([[y[2] for y in data.values()], [y[3] for y in data.values()]])

    # size
    try:
        size = (int(request.params['width']), int(request.params['height']))
        if size <= (0, 0) or size > (1200, 500):
            raise ValueError
    except Exception:
        size = (300, 180)

    # ylim
    ylim_min, ylim_max = None, None
    if 'ylim_min' in request.params:
        try:
            ylim_min = int(request.params['ylim_min'])
        except Exception:
            pass
    if 'ylim_max' in request.params:
        try:
            ylim_max = int(request.params['ylim_max'])
        except Exception:
            pass

    # auto date formatter
    autodt = bool(request.params.get('autodt'))

    image = libgraph.draw_list([datetime.datetime.strptime(x, '%Y%m%d%H%M') for x in data.keys()],
                                ys, xlim=(dt_start, dt_end), size=size, ylim=(ylim_min, ylim_max), autodt=autodt)
    response.content_type = 'image/png'
    return image
