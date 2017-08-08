# -*- coding: utf-8 -*-

import zmq
import json
import time
import random
import sys

sites = ('tower', 'aifang', 'haozu', 'jinpu')
ps = ('Index', 'Listing', 'Property')

def rand_ip():
    def rand_255():
        return int(random.random() * 255)
    return '192.168.200.%d' % (rand_255())

socket = zmq.Socket(zmq.Context.instance(), zmq.PUSH)
socket.bind('ipc:///tmp/soj.ipc')

if len(sys.argv) > 1:
    interval = float(sys.argv[1])
else:
    interval = 0.1

while True:
    try:
        soj = {
            'stamp': str(int(time.time() * 1000)),
            'site': sites[int(random.random() * len(sites))],
            'cip': rand_ip()
        }
        line = 'tracker.site.%s:%s' % (ps[int(random.random() * len(ps))], json.dumps(soj))
        print line
        socket.send(line)
        time.sleep(interval)

    except KeyboardInterrupt:
        break
