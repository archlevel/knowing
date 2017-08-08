# -*- coding: utf-8 -*-

import zmq
import argparse
import msgpack
import re
import time

def main(args):

    socket = zmq.Socket(zmq.Context.instance(), zmq.PULL)
    socket.connect(args.endpoint)

    ptrn = re.compile(' \[([^\]]+)\] ')

    i = 0
    while True:

        raw = socket.recv()

        i += 1
        if i % 50000 != 0:
            continue

        log = msgpack.unpackb(raw)
        mo = ptrn.search(log)
        ts = mo.group(1)

        dt = time.strptime(ts, '%d/%b/%Y:%H:%M:%S +0800')
        ts = time.mktime(dt)
        delta = time.time() - ts

        if delta < 600:
            print 'catch it'
            break

        print 'delta %d seconds' % int(delta)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', default='ipc:///tmp/storm.ipc')
    args = parser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        pass

