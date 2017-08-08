# -*- coding: utf-8 -*-

import amqplib.client_0_8 as amqp
import argparse
import time
import json

def count(ch, args):

    try:
        print ch.queue_declare(args.queue_name, passive=True)[1]
    except Exception, e:
        print e

def last(ch, args):

    try:

        queue_name, _, _ = ch.queue_declare(exclusive=True)
        ch.queue_bind(queue_name, 'amq.topic', args.routing_key)

        while True:

            msg = ch.basic_get(queue_name, True)
            if msg is not None:

                t = None
                try:
                    j = json.loads(msg.body)
                    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(j['stamp']) / 1000))
                except Exception:
                    pass
                print t, msg.body
                break

            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

    except Exception, e:
        print e

def delete(ch, args):

    try:
        ch.queue_delete(args.queue_name)
        print 'delete ok'
    except Exception, e:
        print e


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5672)
    parser.add_argument('--queue-name', default='ops.storm.soj')
    parser.add_argument('--routing-key', default='sojourner.log.tracker.#')
    parser.add_argument('--action', choices=['count', 'last', 'delete'], default='count')
    args = parser.parse_args()

    with amqp.Connection('%s:%d' % (args.host, args.port)) as conn:
        with conn.channel() as ch:
            func = locals()[args.action]
            func(ch, args)
