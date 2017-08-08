# -*- coding: utf-8 -*-

import time
from bottle import request
from sakuya import app, view
from sakuya.models.sakuya_db import Charts

@app.get('/search')
@view('search')
def index(sakuya_db):

    kw = request.params.get('kw', '')

    rt = {'kw': kw}

    if kw:
        chart_list = []
        for row in sakuya_db.\
                   query(Charts).\
                   filter(Charts.name.like('%%%s%%' % kw)).\
                   order_by(Charts.id.desc()):
            chart_list.append({
                'id': row.id,
                'name': row.name
            })

        rt['chart_list'] = chart_list
        rt['millitime'] = int(round(time.time() * 1000))

    return rt
