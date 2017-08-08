# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import traceback
from bottle import request, redirect, abort
from sakuya import app
from sakuya.config import get_config
from sakuya.lib import util
from sakuya.models.sakuya_db import Users

@app.hook('before_request')
def authenticate():
    user = None
    auth_cookie = util.get_cookie('auth')
    if auth_cookie:
        try:
            userid, username, truename, mobile, email = auth_cookie

            user = {
                'userid': userid,
                'username': username,
                'truename': truename,
                'mobile': mobile,
                'email': email
            }
        except Exception:
            pass
    request.environ['user'] = user

def get_user():
    return request.environ['user']

def is_authenticated():
    return get_user() is not None

def clear_authentication():
    util.set_cookie('auth', None)

def authenticate_from_oauth(sakuya_db):
    oauth_token = request.query.get('access_token')
    if oauth_token is not None:
        oauth_config = get_config('webapp')['oauth']
        try:
            f = urllib2.urlopen(oauth_config['url'] + '/resource.php',
                                urllib.urlencode({'oauth_token': oauth_token, 'getinfo': True}),
                                5)
            user = f.read()
            f.close()

            user = json.loads(user)
            for k in user.keys():
                if isinstance(user[k], unicode):
                    user[k] = user[k].encode('utf-8')

            row = sakuya_db.query(Users).filter_by(username=user['username']).first()
            if row is None:
                row = Users()
                row.username = user['username']
                row.truename = user['chinese_name']
                row.email = user['email']
                sakuya_db.add(row)
                sakuya_db.commit()

            util.set_cookie('auth', (row.id, row.username, row.truename,
                row.mobile, row.email))

            return True

        except Exception, e:
            print 'Fail to login from oauth.'
            traceback.print_exc()

    return False

def get_login_info():
    oauth_config = get_config('webapp')['oauth']
    data = {
        'client_id': oauth_config['client'],
        'response_type': 'code',
        'curl': True
    }

    try:
        f = urllib2.urlopen(oauth_config['url'] + '/authorize.php',
                            urllib.urlencode(data),
                            3)
        code = f.read()
        f.close()
        code = json.loads(code)

    except Exception, e:
        code = {'code':''}

    return {
        'url': oauth_config['url'],
        'client_id': oauth_config['client'],
        'client_secret': oauth_config['secret'],
        'grant_type': 'authorization_code',
        'code': code['code']
    }

def redirect_to_oauth():
    login_info = get_login_info()
    return redirect('%s/token.php?%s' % (login_info.pop('url'), urllib.urlencode(login_info)))

def login(func):
    def wrapper(*args, **kwargs):
        if get_user() is None:
            return abort(403)
        return func(*args, **kwargs)
    return wrapper

_roles = get_config('webapp')['roles']
for k, v in _roles.iteritems():
    if k == 'admin':
        continue
    v.extend(_roles['admin'])

def role(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_role(*roles):
                return abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def is_role(*roles):
    user = get_user()
    if user is None:
        return False
    for role in roles:
        if user['username'] in _roles[role]:
            return True
    return False
