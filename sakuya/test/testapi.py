# -*- coding: utf-8 -*-

import urllib2
import json
import time

def main():

    data = {
        'category': ['基础监控', '好租App', 'app10-003'],
        'data': {'load': 1},
        'datetime': time.strftime('%Y-%m-%d %H:%M')
    }
    req = urllib2.Request(url='http://knowing.local.dev.anjuke.com/api/suite-data',
                          data=json.dumps(data))
    f = urllib2.urlopen(req)
    print json.loads(f.read())

if __name__ == '__main__':
    main()
