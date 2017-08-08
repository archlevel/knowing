# -*- coding: utf-8 -*-

import zmq
import signal
import argparse
import msgpack
import logging
import datetime
import errno
import re
from sakuya.lib import util, asset
from sakuya.config import get_config
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import LogstuffTmpl

METHODS = { # method name => [rule id or datasource name]
    'UniqueUpstreamAddr': ['access_log']
}

STATS_INTERVAL = 60 # 60 secs

class Job(object):

    interrupted = False

    def __init__(self, args):
        self.args = args

    def signal_handler(self, signum, frame):
        if signum == signal.SIGTERM or signum == signal.SIGINT:
            self.interrupted = True

    def init_rule_methods(self):
        self.rule_methods = {}
        for method, rules in METHODS.iteritems():
            for rule_id in set(rules):
                if rule_id not in self.rule_methods:
                    self.rule_methods[rule_id] = []
                self.rule_methods[rule_id].append(globals()[method])

    def calc_next_time(self, log_time):
        return log_time - log_time % STATS_INTERVAL + STATS_INTERVAL

    def run(self):

        util.setup_logging('rule_logger', True, self.args.verbose)

        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.socket = zmq.Socket(zmq.Context.instance(), zmq.PULL)
        self.socket.bind(get_config('webapp')['rule_logger_endpoint'])

        self.sakuya_db = sessionmaker(bind=engine_sakuya_db)()

        self.init_rule_methods()
        self.datasource_rules = {}
        self.next_time = {}

        logging.info('Start looping...')
        self.loop()

        self.socket.close()

    def loop(self):

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        while not self.interrupted:

            try:
                events = poller.poll(500)
            except zmq.ZMQError as e:
                if e.errno == errno.EINTR:
                    continue

            for socket, flags in events:
                if socket == self.socket:
                    self.handle_message()

    def handle_message(self):

        try:
            msg = msgpack.unpackb(self.socket.recv())
            log_time = int(round(msg['time'] / 1000.0))

            if msg['datasource'] not in self.datasource_rules:
                self.datasource_rules[msg['datasource']] = {}
                self.next_time[msg['datasource']] = self.calc_next_time(log_time)

            elif log_time >= self.next_time[msg['datasource']]:
                self.stats(msg['datasource'])
                self.next_time[msg['datasource']] = self.calc_next_time(log_time)

            for rule_id in msg['rules']:

                if rule_id not in self.datasource_rules[msg['datasource']]:
                    self.datasource_rules[msg['datasource']][rule_id] = []

                    if rule_id in self.rule_methods:
                        methods = self.rule_methods[rule_id]
                    elif msg['datasource'] in self.rule_methods:
                        methods = self.rule_methods[msg['datasource']]
                    else:
                        logging.debug('Unkown datasource %s' % msg['datasource'])
                        continue

                    for method in methods:
                        self.datasource_rules[msg['datasource']][rule_id].append(method())

                for method in self.datasource_rules[msg['datasource']][rule_id]:
                    try:
                        method.handle(msg['event'])
                    except Exception, e:
                        logging.exception('Fail to handle.')

        except Exception, e:
            logging.exception('Fail to handle message.')

    def stats(self, datasource):

        stats_time = datetime.datetime.fromtimestamp(self.next_time[datasource])
        LogStuff = LogstuffTmpl.gen(stats_time.strftime('%Y%m%d'))

        num_rows = 0
        for ds, rules in self.datasource_rules.iteritems():
            if ds != datasource:
                continue
            for rule_id in rules.keys():
                result = []
                for method in rules[rule_id]:
                    try:
                        detail = method.stats()
                    except Exception, e:
                        logging.exception('Fail to stats.')
                        continue
                    if detail:
                        result.append(detail)

                if not result:
                    del rules[rule_id]
                    continue

                row = LogStuff()
                row.ds_id = rule_id
                row.time = stats_time
                row.detail = "\n\n".join(result)
                self.sakuya_db.add(row)
                num_rows += 1

        self.sakuya_db.commit()
        logging.info('%d rows inserted' % num_rows)


class Method(object):

    def handle(self, log):
        raise NotImplementedError

    def stats(self):
        raise NotImplementedError


class UniqueUpstreamAddr(Method):

    ptrn_ip = re.compile('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

    def __init__(self):
        self.addrs = {}

    def handle(self, log):
        addr = log['upstream_addr']
        if addr not in self.addrs:
            self.addrs[addr] = 0
        self.addrs[addr] += 1

    def stats(self):

        sorted_items = sorted(self.addrs.iteritems(), key=lambda x: x[1], reverse=True)
        self.addrs.clear()

        result = []
        for addr, cnt in sorted_items:
            mo = self.ptrn_ip.search(addr)
            if mo is None:
                continue
            ip = mo.group(0)
            belongto = asset.get_belongto(ip)
            if belongto:
                result.append('%s（%s）: %d' % (addr, belongto, cnt))
            else:
                result.append('%s: %d' % (addr, cnt))

        return "\n".join(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    Job(args).run()
