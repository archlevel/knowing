# -*- coding: utf-8 -*-

import fcntl
import os
import json
import logging
import logging.handlers
import time
import datetime
from bottle import request, response
from sakuya.config import get_config

COOKIE_SECRET = get_config('webapp')['cookie_secret']

def millitime():
    return int(round(time.time() * 1000))

def timestamp(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    return int(round(time.mktime(dt.timetuple())))

def output(status, **kwargs):
    return json.dumps(dict(status=status, **kwargs))

def get_cookie(key):
    return request.get_cookie(key, secret=COOKIE_SECRET)

def set_cookie(key, value):
    return response.set_cookie(key, value, secret=COOKIE_SECRET, path="/")

def setup_logging(job, daemon=False, verbose=False):

    log_folder = '%s/%s' % (get_config('webapp')['job_logs_directory'], job)
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    log_filename = '%s/log' % log_folder

    logger = logging.getLogger()

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handlers = []

    if daemon:
        handlers.append(logging.handlers.
                        TimedRotatingFileHandler(filename=log_filename, when='midnight'))
    else:
        handlers.append(logging.FileHandler(filename='%s.%s' % (log_filename, time.strftime('%Y-%m-%d'))))

    handlers.append(logging.StreamHandler())

    for handler in handlers:
        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)

def unique(l):
    tmp = []
    for i in l:
        i = i.strip()
        if i and i not in tmp:
            tmp.append(i)
    return tmp

def process_exists(name):
    fullpath = '%s/%s' % (get_config('webapp')['flocks_dir'], name)
    f = open(fullpath, 'w')
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        logging.error('Process exists: cannot lock file %s' % fullpath)
        exit(2)
    else:
        globals()['_process_exists_flock'] = f

def current_minute():
    return datetime.datetime.now().replace(second=0, microsecond=0)

def ip2long(s):
  return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def long2ip(ip):
  return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

def invert_dict(d):
    return dict([(v, k) for k, v in d.iteritems()])
