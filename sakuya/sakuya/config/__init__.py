# -*- coding: utf-8 -*-

import os
import threading
import yaml
from sakuya import APP_ROOT

_env = os.environ.get('BOTTLE_ENV', 'development')
_lock = threading.Lock()
_config = {}

def get_config(name):
    if name in _config:
        return _config[name]

    with _lock:
        if name not in _config:
            try:
                with open('%s/config/%s.yml' % (APP_ROOT, name)) as f:
                    _config[name] = yaml.load(f.read())[_env]
            except Exception:
                raise
                _config[name] = {}

        return _config[name]
