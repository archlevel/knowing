# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import traceback
import datetime
from collections import OrderedDict
from bottle import abort, redirect, request
from sakuya import app, view
from sakuya.controllers.admin.category import make_breadcrumbs
from sakuya.models.sakuya_db import Categories, Charts, WarnRules, Follows, Users
from sakuya.lib import auth, storm, haopan, warn, chart as libchart
from sakuya.config import get_config

_storm = {
    'datasources': storm.datasources,
    'datasource_list': storm.datasources.keys(),
    'datasource_field_list': dict(((k, v.keys()) for (k, v) in storm.datasources.iteritems())),
    'rule_types': storm.rule_types,
    'rule_type_list': storm.rule_types.keys(),
    'operators': storm.operators,
    'operator_list': dict(((k, v[0].keys()) for (k, v) in storm.operators.iteritems()))
}
_storm_json = json.dumps(_storm)

def _rt(sakuya_db):

    users = []
    for row in sakuya_db.\
               query(Users).\
               order_by(Users.id):
        users.append({
            'username': row.username,
            'truename': row.truename
        })

    return {
        'users': users,
        'users_json': json.dumps(users),
        'storm': _storm,
        'storm_json': _storm_json,
        'categories': libchart.get_category_list(sakuya_db)
    }

@app.get('/admin/chart/new')
@app.get('/admin/chart/new/<cid:int>')
@view('admin/chart_edit')
@auth.role('sa')
def new(sakuya_db, cid=None):

    if cid is not None\
            and not sakuya_db.query(Categories).filter_by(id=cid, is_parent=False).count():
        abort(404)

    rt = _rt(sakuya_db)
    rt['forms'] = {
        'name': '',
        'cid': cid,
        'owner': auth.get_user()['username'],
        'owner_name': auth.get_user()['truename'],
        'rule': {},
        'warn': [],
        'alert_enable': 0
    }
    rt['warn_only'] = False
    rt['is_haopan'] = False

    return rt

@app.post('/admin/chart/add')
@view('admin/chart_edit')
@auth.role('sa')
def add(sakuya_db):

    rule = None
    warn = None

    def error(msg):
        rt = _rt(sakuya_db)
        rt['forms'] = request.forms
        rt['forms']['rule'] = dump_rule(rule)
        rt['forms']['warn'] = dump_warn(warn)
        rt['error_msg'] = msg
        rt['warn_only'] = False
        rt['is_haopan'] = False
        return rt

    try:
        use_storm = request.forms['use_storm'] == '1'
        if use_storm:
            rule = make_rule()
            if not rule['datasource'] or not rule['filters']:
                raise ValueError

        alert_enable = request.forms['alert_enable'] == '1'
        warn = make_warn()
        if alert_enable and not warn:
            raise ValueError

        name = request.forms['name']
        if not name:
            raise ValueError

        cid = int(request.forms['cid'])
        if not sakuya_db.\
               query(Categories).\
               filter_by(id=cid, is_parent=False).\
               count():
            raise ValueError

        owner = request.forms['owner']
        if not sakuya_db.\
               query(Users).\
               filter_by(username=owner).\
               count():
            raise ValueError

    except Exception:
        return error('参数错误。')

    # add chart
    try:
        row = Charts()
        row.name = name
        row.owner = owner
        row.cate_id = cid
        row.root_category = get_parent_category(sakuya_db, cid)
        row.ds_id = 0
        row.ds_tbl_name = ''
        row.ext_info = ''
        row.followers = 0
        row.createtime = datetime.datetime.now()
        row.alert_enable = int(alert_enable)

        ext = {}
        if use_storm:
            ext['rule'] = rule
        row.ext_info = json.dumps(ext)

        sakuya_db.add(row)
        sakuya_db.flush()
        rowid = row.id
        sakuya_db.commit()

    except Exception:
        traceback.print_exc()
        sakuya_db.rollback()
        return error('图表添加失败。')

    process_warn_rules(sakuya_db, rowid, warn)

    if use_storm:
        storm.set_rule(rowid, json.dumps(rule))
        redirect('/admin/category/%d' % cid)
    else:
        redirect('/admin/chart/success/%d' % rowid)

def get_parent_category(sakuya_db, id):
    pids = [id]
    while pids[-1] > 1:
        cate = sakuya_db.query(Categories).get(pids[-1])
        if cate is None:
            break
        pids.append(cate.parent_cate_id)

    if len(pids) > 1:
        return pids[-2]
    else:
        return 0

@app.get('/admin/chart/success/<id:int>')
@view('admin/chart_success')
def success(sakuya_db, id):

    row = sakuya_db.query(Charts).get(id)
    if row is None:
        abort(404)

    breadcrumbs = make_breadcrumbs(sakuya_db, row.cate_id)
    breadcrumbs[len(breadcrumbs) - 1]['active'] = False
    breadcrumbs.append({
        'name': '图表',
        'active': True
    })

    return {
        'id': row.id,
        'cid': row.cate_id,
        'breadcrumbs': breadcrumbs
    }

@app.get('/admin/chart/edit/<id:int>')
@view('admin/chart_edit')
@auth.login
def edit(sakuya_db, id):

    row = sakuya_db.query(Charts).get(id)
    if row is None:
        abort(404)

    is_haopan = haopan.is_haopan(row.cate_id)
    is_copy = request.params.get('copy') == '1'

    if auth.is_role('sa'):
        warn_only = False
    elif auth.is_role('haopan') and is_haopan: # this can be replaced with userid-cid authorization
        warn_only = True
    elif auth.get_user()['username'] == row.owner:
        warn_only = True
    else:
        abort(403)

    if is_copy and (is_haopan or warn_only):
        abort(400)

    rt = _rt(sakuya_db)
    rt['id'] = id
    rt['editing'] = not is_copy
    rt['warn_only'] = warn_only
    rt['is_haopan'] = is_haopan

    forms = {
        'name': haopan.format_title(row.name) if is_haopan else row.name,
        'cid': row.cate_id,
        'owner': row.owner,
        'alert_enable': row.alert_enable
    }

    ext = row.get_ext()
    forms['rule'] = dump_rule(ext.get('rule'))
    forms['warn'] = dump_warn(warn.get_warn(sakuya_db, id))

    forms['owner_name'] = '系统'
    for item in rt['users']:
        if item['username'] == forms['owner']:
            forms['owner_name'] = item['truename']

    rt['forms'] = forms

    return rt

@app.post('/admin/chart/update/<id:int>')
@view('admin/chart_edit')
@auth.login
def update(sakuya_db, id):

    row = sakuya_db.query(Charts).get(id)
    if row is None:
        abort(404)

    is_haopan = haopan.is_haopan(row.cate_id)

    if auth.is_role('sa'):
        warn_only = False
    elif auth.is_role('haopan') and is_haopan:
        warn_only = True
    elif auth.get_user()['username'] == row.owner:
        warn_only = True
    else:
        abort(403)

    rule = None
    warn = None

    def error(msg):
        rt = _rt(sakuya_db)
        rt['id'] = id
        rt['editing'] = True
        rt['warn_only'] = warn_only
        rt['is_haopan'] = is_haopan
        rt['forms'] = request.forms
        rt['forms']['rule'] = dump_rule(rule)
        rt['forms']['warn'] = dump_warn(warn)
        rt['error_msg'] = msg
        return rt

    try:

        alert_enable = request.forms['alert_enable'] == '1'
        warn = make_warn()
        if alert_enable and not warn:
            raise ValueError

        if not warn_only and not is_haopan:

            use_storm = request.forms['use_storm'] == '1'
            if use_storm:
                rule = make_rule()
                if not rule['datasource'] or not rule['filters']:
                    raise ValueError

            name = request.forms['name']
            if not name:
                raise ValueError

            cid = int(request.forms['cid'])
            if not sakuya_db.\
                   query(Categories).\
                   filter_by(id=cid, is_parent=False).\
                   count():
                raise ValueError

            owner = request.forms['owner']
            if not sakuya_db.\
                   query(Users).\
                   filter_by(username=owner).\
                   count():
                raise ValueError

    except Exception:
        return error('参数错误。')

    try:
        row.alert_enable = int(alert_enable)
        row.warnings = 0
        row.criticals = 0
        process_warn_rules(sakuya_db, id, warn)

        if not warn_only and not is_haopan:
            row.name = name
            row.cate_id = cid
            row.root_category = get_parent_category(sakuya_db, cid)
            row.owner = owner

            ext = row.get_ext()
            if use_storm:
                ext['rule'] = rule
                storm.set_rule(id, json.dumps(rule))
            else:
                ext.pop('rule', None)
                storm.delete_rule(id)
            row.ext_info = json.dumps(ext)

        sakuya_db.commit()

    except Exception:
        traceback.print_exc()
        sakuya_db.rollback()
        return error('图表更新失败。')

    if warn_only or is_haopan:
        redirect('/chart/%d' % id)
    redirect('/admin/category/%d' % cid)

@app.get('/admin/chart/delete/<id:int>')
@auth.role('sa')
def delete(sakuya_db, id):

    row = sakuya_db.query(Charts).get(id)
    if row is None:
        abort(404)

    if haopan.is_haopan(row.cate_id):
        abort(404)

    cid = row.cate_id
    sakuya_db.delete(row)
    sakuya_db.query(Follows).filter_by(cid=id).delete()
    sakuya_db.commit()

    process_warn_rules(sakuya_db, id, [])

    storm.delete_rule(id)

    return redirect('/admin/category/%d' % cid)

def make_rule():

    ruc = {}
    ruc['datasource'] = request.forms.get('storm_datasource')
    ruc['rule_type'] = request.forms.get('storm_rule_type')
    ruc['field'] = request.forms.get('storm_field')
    ruc['logging'] = request.forms.get('storm_logging', '') == '1'

    filters = OrderedDict()

    filter_field = request.forms.getall('storm_filter_field[]')
    filter_operator = request.forms.getall('storm_filter_operator[]')
    filter_content = request.forms.getall('storm_filter_content[]')
    filter_negative = request.forms.getall('storm_filter_negative[]')
    filter_id = request.forms.getall('storm_filter_id[]')

    datasource = storm.datasources[ruc['datasource']]
    for i, id in enumerate(filter_id):

        field = filter_field[i]
        operator = filter_operator[i]
        content = filter_content[i]
        field_type = datasource[field][0]

        if field_type == 'string':
            if operator == 'in':
                content = [ci.strip() for ci in content.split(',')]
        elif field_type == 'numeric':
            if operator in ('in', 'nin'):
                tmp_content = []
                for ci in content.split(','):
                    ci = float(ci.strip())
                    if ci.is_integer():
                        ci = int(ci)
                    tmp_content.append(ci)
                content = tmp_content
            else:
                content = float(content.strip())
                if content.is_integer():
                    content = int(content)

        filters[id] = [field, operator, False, content]

    for id in filter_negative:
        filters[id][2] = True

    ruc['filters'] = filters.values()

    return ruc

def dump_rule(rule):

    if not rule:
        return {}

    try:
        rule['datasource'], rule['rule_type'] # assert exists
        rule['field'] = rule.get('field', '')
        rule['logging'] = rule.get('logging', False)

        filters = []
        for item in rule['filters']:
            filters.append(json.dumps(item)) # convert filter rule to json for js
        rule['filters'] = filters

        return rule

    except Exception:
        return {}

def make_warn():

    ids = request.forms.getall('warn_id[]')
    duration_starts = request.forms.getall('warn_duration_start[]')
    duration_ends = request.forms.getall('warn_duration_end[]')
    types = request.forms.getall('warn_type[]')
    hwm_warnings = request.forms.getall('warn_hwm_warning[]')
    hwm_criticals = request.forms.getall('warn_hwm_critical[]')
    lwm_warnings = request.forms.getall('warn_lwm_warning[]')
    lwm_criticals = request.forms.getall('warn_lwm_critical[]')
    latencies = request.forms.getall('warn_latency[]')
    intervals = request.forms.getall('warn_interval[]')

    warns = []
    for i in xrange(0, len(duration_starts)):
        try:
            # TODO validation
            warns.append({
                'id': int(ids[i]),
                'duration_start': duration_starts[i],
                'duration_end': duration_ends[i],
                'type': types[i],
                'hwm_warning': hwm_warnings[i],
                'hwm_critical': hwm_criticals[i],
                'lwm_warning': lwm_warnings[i],
                'lwm_critical': lwm_criticals[i],
                'latency': latencies[i],
                'interval': intervals[i]
            })

        except Exception, e:
            pass

    return warns

def dump_warn(warn):
    if not warn:
        return []
    return [json.dumps(i) for i in warn]

def process_warn_rules(sakuya_db, chart_id, warns):

    try:
        cur = {}
        for row in sakuya_db.query(WarnRules).filter_by(chart_id=chart_id):
            cur[row.id] = row

        for item in warns:
            id = item.pop('id')
            if id in cur:
                row = cur.pop(id)
                row.content = json.dumps(item)
            else:
                row = WarnRules()
                row.chart_id = chart_id
                row.content = json.dumps(item)
                sakuya_db.add(row)

        for row in cur.values():
            sakuya_db.delete(row)

        sakuya_db.commit()

        for row in sakuya_db.query(Follows).filter_by(cid=chart_id, recv_warning=True):

            if row.recv_rules == 'all':
                continue

            if not row.recv_rules:
                continue

            recv_rules = []
            for i in row.get_recv_rules():
                if i not in cur.keys():
                    recv_rules.append(i)

            row.recv_rules = ','.join(str(i) for i in recv_rules)

        sakuya_db.commit()

    except Exception, e:
        traceback.print_exc()
        sakuya_db.rollback()
