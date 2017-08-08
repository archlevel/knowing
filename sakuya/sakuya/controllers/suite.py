# -*- coding: utf-8 -*-

import json
import datetime
from collections import OrderedDict
from bottle import abort, request, redirect
from sakuya import app, view
from sakuya.config import get_config
from sakuya.lib import util, chart as libchart
from sakuya.models.sakuya_db import Categories, Charts

@app.get('/monitor/suite')
@app.get('/monitor/suite/<cate1:int>')
@app.get('/monitor/suite/<cate1:int>/<cate2:int>')
@app.get('/monitor/suite/<cate1:int>/<cate2:int>/<cate3:int>')
@view('suite')
def suite(sakuya_db, cate1=None, cate2=None, cate3=None):

    pri_cate, pri_list = libchart.get_category_tab(sakuya_db, [libchart.MONITOR_PID, libchart.OPS_PID], 2)
    sec_cate, sec_list = libchart.get_category_tab(sakuya_db, [libchart.SUITE_PID, cate1, cate2, cate3], 3)

    if len(sec_cate) == 1:
        redirect('/')

    datasources = {}
    for chart in sakuya_db.\
                 query(Charts).\
                 filter_by(cate_id=sec_cate[3]['id']):

        datasources[chart.name.split('::')[3]] = chart.id

    js_charts = []
    js_charts.append({
        'title': '%s - Load & Memory Usage' % sec_cate[3]['name'],
        'series': [['Load', datasources['Load'], 'line'],
                   ['Memory', datasources['Memory'], 'area']]
    })
    js_charts.append({
        'title': '%s - Disk Usage' % sec_cate[3]['name'],
        'series': [['Disk', datasources['Disk'], 'area']]
    })

    return {
        'pri_cate': pri_cate,
        'pri_list': pri_list,
        'sec_cate': sec_cate,
        'sec_list': sec_list,
        'js_charts': json.dumps(js_charts),
        'cur_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'has_detail': sec_cate[3]['name'] == u'汇总'
    }
