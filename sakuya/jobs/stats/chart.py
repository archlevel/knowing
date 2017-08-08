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

ptrn1 = re.compile('GET /graph/haopan/list/([0-9]+)(?:/([0-9]+))?')
ptrn2 = re.compile('GET /chart/data\?id_list=([0-9]+)(?:%2C([0-9]+)%2C)?')
ptrn3 = re.compile('GET /chart/([0-9]+)(?:/([0-9]+))?')

charts = {}
def inc_chart(id, i):
    id = int(id)
    if id not in charts:
        charts[id] = [0, 0]
    charts[id][i] += 1

for filename in filenames:
    with open(filename) as f:
        for l in f:

            mo1 = ptrn1.search(l)
            if mo1 is not None:
                #if '/monitoring' in l:
                #    continue
                inc_chart(mo1.group(1), 0)
                if mo1.group(2) is not None:
                    inc_chart(mo1.group(2), 0)
                continue

            mo2 = ptrn2.search(l)
            if mo2 is not None:
                inc_chart(mo2.group(1), 0)
                if mo2.group(2) is not None:
                    inc_chart(mo2.group(2), 0)
                continue

            mo3 = ptrn3.search(l)
            if mo3 is not None:
                inc_chart(mo3.group(1), 1)
                if mo3.group(2) is not None:
                    inc_chart(mo3.group(2), 1)
                continue

for id, count in charts.iteritems():
    print '%d\t%d\t%d' % (id, count[0], count[1])

