# -*- coding: utf-8 -*-

import re

filenames = (
    'knowing.log-20130625',
    'knowing.log-20130626',
    'knowing.log-20130627',
    'knowing.log-20130628',
    'knowing.log-20130629',
    'knowing.log-20130630',
    'knowing.log-20130701'
)

ptrn = re.compile('GET /(monitor|speed|security)/?([0-9]+)?/?([0-9]+)?')
cate_mapper = {
    'monitor': 2,
    'speed': 3,
    'security': 4
}
charts = {}
def inc_chart(id):
    id = int(id)
    if id not in charts:
        charts[id] = 0
    charts[id] += 1

for filename in filenames:
    with open(filename) as f:
        for l in f:
            mo = ptrn.search(l)
            if mo is None:
                continue
            if mo.group(3) is not None:
                inc_chart(mo.group(3))
                continue
            if mo.group(2) is not None:
                inc_chart(mo.group(2))
                continue
            if mo.group(1) == 'monitor' and 'GET /monitoring' in l:
                continue
            inc_chart(cate_mapper[mo.group(1)])

for id, count in charts.iteritems():
    print '%d\t%d' % (id, count)

