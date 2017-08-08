# -*- coding: utf-8 -*-

import json
import datetime
import msgpack
import traceback
from bottle import static_file, redirect
from sakuya import app, view
from sakuya import APP_ROOT
from sakuya.lib import util, auth, haopan
from sakuya.models import plugin_sakuya_db, plugin_db_monitor
from sakuya.models.db_monitor import SlowDaily, MysqlDaily
from sakuya.models.sakuya_db import Charts, Follows, Users, Events
from sakuya.config import get_config

@app.route('/assets/<filepath:path>')
def assets(filepath):
    return static_file(filepath, root='%s/assets' % APP_ROOT)

@app.error(403)
@view('error')
def error403(error):
    return {
        'title': '403 禁止访问',
        'msg': '很抱歉，您没有访问本页面的权限。请尝试<a href="/login">登录</a>，或<a href="/logout">切换</a>至授权用户。谢谢。'
    }

@app.get('/')
@view('index')
def index(sakuya_db):

    rt = {}
    rt['stats'] = {
        'charts': sakuya_db.query(Charts).count(),
        'users': sakuya_db.query(Users).count(),
        'follows': sakuya_db.query(Follows).count()
    }

    rt['events'] = []
    for row in sakuya_db.\
               query(Events).\
               order_by(Events.id.desc()).\
               limit(7):

        if row.type == Events.CONST_TYPE_CRITICAL:
            type_text = 'Critical'
        else:
            type_text = 'Warning'

        rt['events'].append({
            'cid': row.cid,
            'info': row.info,
            'time': row.time.strftime('%H:%M'),
            'type': type_text
        })

    rt['top_monitor'] = []
    for row in sakuya_db.\
               query(Charts).\
               filter_by(root_category=2).\
               order_by(Charts.followers.desc(), Charts.id).\
               limit(7):

        rt['top_monitor'].append({
            'id': row.id,
            'name': haopan.format_title(row.name),
            'num': row.followers
        })

    rt['top_speed'] = []
    for row in sakuya_db.\
               query(Charts).\
               filter_by(root_category=3).\
               order_by(Charts.followers.desc(), Charts.id).\
               limit(7):

        rt['top_speed'].append({
            'id': row.id,
            'name': row.name,
            'num': row.followers
        })

    user = auth.get_user()
    if user is None:
        rt['login_info'] = auth.get_login_info()

    else:
        rt['my_follows'] = []
        for row in sakuya_db.\
                   query(Follows).\
                   filter_by(follower=user['userid']).\
                   limit(8):

            chart = sakuya_db.query(Charts).get(row.cid)
            if chart is None:
                continue
            rt['my_follows'].append({
                'id': chart.id,
                'name': haopan.format_title(chart.name)
            })

        rt['my_charts'] = []
        for row in sakuya_db.\
                   query(Charts).\
                   filter_by(owner=user['username']).\
                   limit(8):

            rt['my_charts'].append({
                'id': row.id,
                'name': row.name
            })

    return rt

@app.get('/login')
def login(sakuya_db):

    if auth.is_authenticated():
        return redirect('/')

    if auth.authenticate_from_oauth(sakuya_db):
        return redirect('/')

    return auth.redirect_to_oauth()

@app.get('/logout')
def logout():
    auth.clear_authentication()
    return redirect('/')

@app.get('/slowbook', apply=[plugin_db_monitor], skip=[plugin_sakuya_db])
@view('slowbook')
def slowbook(db_monitor):

    data = []
    for row in db_monitor.\
               query(SlowDaily).\
               filter(SlowDaily.date >= (datetime.datetime.now() - datetime.timedelta(days=30)).date()).\
               order_by(SlowDaily.date):
        data.append({
            'date': row.date.strftime('%m-%d'),
            'slow': row.slow,
            'query': row.query
        })

    return {'data': json.dumps(data)}

@app.get('/dbmo', apply=[plugin_db_monitor], skip=[plugin_sakuya_db])
@view('dbmo')
def dbmo(db_monitor):

    data = []
    for row in db_monitor.\
               query(MysqlDaily).\
               filter(MysqlDaily.date >= (datetime.datetime.now() - datetime.timedelta(days=30)).date()).\
               order_by(MysqlDaily.date):
        data.append({
            'date': row.date.strftime('%m-%d'),
            'read': round(float(row.read) / 10 ** 8, 2),
            'write': round(float(row.write) / 10 ** 8, 2)
        })

    return {'data': json.dumps(data)}
