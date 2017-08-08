# -*- coding: utf-8 -*-

from bottle import request
from sakuya import app, view
from sakuya.lib import auth, haopan, util
from sakuya.models.sakuya_db import Follows, Charts, Users

@app.get('/custom')
@app.get('/custom/follow')
@view('custom/follow')
@auth.login
def follow(sakuya_db):

    user = auth.get_user()

    chart_list = []
    invalids = []
    for row in sakuya_db.\
               query(Follows).\
               filter_by(follower=user['userid']).\
               order_by(Follows.id.desc()):

        chart = sakuya_db.query(Charts).get(row.cid)
        if chart is None:
            invalids.append(row)
            continue

        if haopan.is_haopan(chart.cate_id):
            title = haopan.format_title(chart.name)
        else:
            title = chart.name

        chart_list.append({
            'id': chart.id,
            'name': title,
            'recv_warning': row.recv_rules == 'all'
        })

    if invalids:
        for row in invalids:
            sakuya_db.delete(row)
        sakuya_db.commit()

    return {
        'chart_list': chart_list
    }

@app.route('/custom/profile', method=['GET', 'POST'])
@view('custom/profile')
@auth.login
def profile(sakuya_db):

    user = auth.get_user()
    row = sakuya_db.query(Users).get(user['userid'])

    rt = {}

    msg = (None, False)
    if request.method == 'POST':

        rt['forms'] = request.forms

        try:
            # parse email list
            email = request.forms.get('email', '')
            email_list = util.unique(email.split('\n'))
            if not email_list:
                raise ValueError('接警邮箱不能为空')
            email = '\n'.join(email_list)

        except Exception, e:
            msg = (str(e), True)

        else:
            row.email = email
            rt['forms']['email'] = row.email

            sakuya_db.commit()
            msg = ('修改成功', False)

    else:
        rt['forms'] = {
            'email': row.email
        }

    rt['forms']['username'] = row.username
    rt['forms']['truename'] = row.truename

    rt['msg'] = msg

    return rt
