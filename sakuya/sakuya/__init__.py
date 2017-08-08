# -*- coding: utf-8 -*-

import os
import bottle

# init app
app = bottle.Bottle()
APP_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
bottle.TEMPLATE_PATH.insert(0, APP_ROOT + '/views')

# the import order is necessary
from bottle import template
from sakuya.config import get_config

# init db
from sakuya.models import plugin_sakuya_db
app.install(plugin_sakuya_db)

# init auth
import sakuya.lib.auth

# replace the 'view' decorator to inject extra information
def view(tpl):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            d = fn(*args, **kwargs)
            d['auth'] = sakuya.lib.auth
            d['user'] = sakuya.lib.auth.get_user()
            return template(tpl, d)
        return wrapper
    return decorator

# init zookeeper
from kazoo.client import KazooClient
_zk = None
def get_zk():
    global _zk
    if _zk is None:
        _zk = KazooClient(get_config('webapp')['zookeeper_hosts'])
        _zk.start()
    return _zk

# controllers
import sakuya.controllers.home
import sakuya.controllers.category
import sakuya.controllers.chart
import sakuya.controllers.graph
import sakuya.controllers.admin
import sakuya.controllers.custom
import sakuya.controllers.api
import sakuya.controllers.haopan
import sakuya.controllers.ajax
import sakuya.controllers.alert
import sakuya.controllers.monitoring
import sakuya.controllers.search
import sakuya.controllers.suite
