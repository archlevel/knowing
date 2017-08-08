# -*- coding: utf-8 -*-

import time
import random
import json
import amqplib.client_0_8 as amqp

PREFIX = 'sojourner.log.tracker'
sites = ['tower', 'aifang', 'haozu', 'jinpu']
alphabet = 'abcdefghijklmnopqrstuvwxyz'

def random_string(num=10):
    return ''.join(random.sample(alphabet, num))

def millitime():
    return int(round(time.time() * 1000))

class Job():

    def run(self):

        while True:
            try:
                self.loop()
            except KeyboardInterrupt:
                break
            except Exception, e:
                print e
                time.sleep(1)

    def loop(self):

        with amqp.Connection() as conn:
            with conn.channel() as ch:

                site = sites[int(random.random() * len(sites))]
                routing_key = '%s.%s.%s' % (PREFIX, site, random_string())
                body = json.dumps({'site': site, 'stamp': str(millitime())})

                msg = amqp.Message(body)
                ch.basic_publish(msg, 'amq.topic', routing_key)

                print '%s:%s' % (routing_key, body)
                time.sleep(0.3)


if __name__ == '__main__':
    Job().run()
