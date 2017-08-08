# -*- coding: utf-8 -*-

import json
import traceback
from collections import deque
from bottle import abort, request, redirect
from sakuya import app, view
from sakuya.models.sakuya_db import Categories, Charts
from sakuya.lib import util, auth

@app.get('/admin')
@app.get('/admin/category')
@app.get('/admin/category/<id:int>')
@view('admin/category')
@auth.role('sa')
def category(sakuya_db, id=1):

    cat = sakuya_db.query(Categories).get(id)
    if cat is None:
        return abort(404)

    rt = {
        'breadcrumbs': make_breadcrumbs(sakuya_db, id),
        'cat': {'id': cat.id, 'name': cat.name, 'isp': cat.is_parent}
    }

    if cat.is_parent:

        category_list = []
        for row in sakuya_db.\
                   query(Categories).\
                   filter_by(parent_cate_id=cat.id).\
                   order_by(Categories.id):

            item = {
                'id': row.id,
                'name': row.name,
                'isp': row.is_parent
            }

            if row.is_parent:
                item['num_subcategories'] = sakuya_db.query(Categories).filter_by(parent_cate_id=row.id).count()
                item['num_charts'] = '-'
                item['show_delete'] = item['num_subcategories'] == 0
            else:
                item['num_subcategories'] = '-'
                item['num_charts'] = sakuya_db.query(Charts).filter_by(cate_id=row.id).count()
                item['show_delete'] = item['num_charts'] == 0

            category_list.append(item)

        rt['category_list'] = category_list

    else:

        chart_list = []
        for row in sakuya_db.\
                   query(Charts).\
                   filter_by(cate_id=cat.id).\
                   order_by(Charts.id):

            try:
                ext = json.loads(row.ext_info)
            except Exception:
                ext = {}

            chart_list.append({
                'id': row.id,
                'name': row.name,
                'powered_by': ('Storm', 'info') if ext.get('rule') else ('WebAPI', 'success'),
                'num_followers': row.followers
            })

        rt['chart_list'] = chart_list

    return rt

def make_breadcrumbs(sakuya_db, id):

    breadcrumbs = deque()

    _id = id
    while _id > 0:
        row = sakuya_db.query(Categories).get(_id)
        if row is None:
            abort(404)
        breadcrumbs.appendleft({
            'link': '/admin/category/%d' % row.id,
            'name': row.name,
            'active': row.id == id
        })
        _id = row.parent_cate_id

    return breadcrumbs

@app.post('/admin/category/add/<pid:int>')
@auth.role('sa')
def add_category(sakuya_db, pid):

    if not request.forms.name:
        return abort(400)

    parent = sakuya_db.query(Categories).get(pid)
    if parent is None or not parent.is_parent:
        return abort(404)

    row = Categories()
    row.name = request.forms.name
    row.parent_cate_id = pid
    row.is_parent = request.forms.isp == '1'
    sakuya_db.add(row)
    sakuya_db.commit()

    return redirect('/admin/category/%d' % pid)

@app.get('/admin/category/delete/<id:int>')
@auth.role('sa')
def delete_category(sakuya_db, id):

    row = sakuya_db.query(Categories).get(id)
    if row is None:
        return abort(404)

    if (row.is_parent and sakuya_db.query(Categories).filter_by(parent_cate_id=id).count() > 0)\
            or ((not row.is_parent) and sakuya_db.query(Charts).filter_by(cate_id=id).count() > 0):
        return abort(400)

    pid = row.parent_cate_id
    sakuya_db.delete(row)
    sakuya_db.commit()

    return redirect('/admin/category/%d' % pid)

@app.post('/admin/category/edit/<id:int>')
@auth.role('sa')
def edit_category(sakuya_db, id):

    if not request.forms.name:
        return util.output('error', msg='Invalid parameter.')

    try:
        row = sakuya_db.query(Categories).get(id)
        if row is None:
            return util.output('error', msg='Category not found.')
        row.name = request.forms.name
        sakuya_db.commit()
        return util.output('ok')

    except Exception:
        traceback.print_exc()
        sakuya_db.rollback()
        return util.output('error', msg='Fail to edit category.')
