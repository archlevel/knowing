# -*- coding: utf-8 -*-

import zmq
import msgpack
from sakuya.lib import util
from sakuya.config import get_config

def main():
    socket = zmq.Socket(zmq.Context.instance(), zmq.PUSH)
    socket.connect(get_config('webapp')['rule_logger_endpoint'])
    msg = {
        'time': util.millitime(),
        'datasource': 'access_log',
        'event': {'upstream_addr': '10.10.5.244'},
        'rules': [1, 2]
    }
    socket.send(msgpack.packb(msg))
    msg['rules'] = [1]
    socket.send(msgpack.packb(msg))
    msg['event'] = {'upstream_addr': '1.2.3.5'}
    msg['rules'] = [2]
    socket.send(msgpack.packb(msg))
    socket.send(msgpack.packb(msg))
    msg['time'] += 61000
    socket.send(msgpack.packb(msg))

if __name__ == '__main__':
    main()
