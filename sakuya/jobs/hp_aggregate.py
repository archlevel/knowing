# -*- coding: utf-8 -*-

import os
import time
import logging
import zmq
import msgpack
import errno
import signal
import datetime
from sqlalchemy.orm import sessionmaker
from sakuya.config import get_config
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import ChartdataTmpl
from sakuya.lib import util, haopan

TMP_CITIES = {
    '11': 11,
    '14': 14,
    'oth': 1000,
    'db04': 1001
}

class Job:

    interrupted = False

    def signal_handler(self, signum, frame):
        if signum == signal.SIGTERM or signum == signal.SIGINT:
            self.interrupted = True

    def run(self):

        util.setup_logging('hp_aggregate', True)

        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        self.socket = zmq.Socket(zmq.Context.instance(), zmq.PULL)
        self.socket.bind(get_config('webapp')['hp_aggregate_bind'])

        self.sakuya_db = sessionmaker(bind=engine_sakuya_db)()
        self.next_dt = datetime.datetime.now()
        self.data = []

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

        self.stats()

    def handle_message(self):

        try:
            body = msgpack.unpackb(self.socket.recv())
            dt = datetime.datetime.strptime(body['time'], '%Y-%m-%d %H:%M')

            if dt > self.next_dt:
                self.stats()
                self.next_dt = dt
                del self.data[:]

            # convert 'city' param
            cnt = 0
            for item in body['data']:
                item_ = list(item)
                if isinstance(item_[3], basestring):
                    if item_[3] in TMP_CITIES:
                        item_[3] = TMP_CITIES[item_[3]]
                    else:
                        continue
                self.data.append(tuple(item_))
                cnt += 1

            logging.info('%d items received.' % cnt)

        except Exception:
            logging.exception('Fail to handle message.')

    def stats(self):

        if not self.data:
            return

        try:
            rows = haopan.fill_data(self.data)

            logging.info('stats time: %s' % self.next_dt.strftime('%Y-%m-%d %H:%M'))

            d_charts = haopan.get_charts(True)
            stats = [0, 0]
            for k, v in rows.iteritems():

                id = d_charts.get(k)
                if id is None:
                    logging.info('key %s not found.' % str(k))
                    stats[1] += 1
                    continue

                row = ChartdataTmpl.gen(self.next_dt.strftime('%Y%m%d'))()
                row.ds_id = id
                row.time = self.next_dt
                row.data = v
                self.sakuya_db.add(row)
                stats[0] += 1
                logging.info('key: %s, id: %d, data: %d' % (str(k), id, v))

            self.sakuya_db.commit()
            logging.info('%d rows inserted, %d failed.' % tuple(stats))

        except Exception:
            self.sakuya_db.rollback()
            logging.exception('Fail to stats')

        self.stats_extra()

    def stats_extra(self):

        rows = { # prod chart channel
            (1, 1, 3): [0, 4254],
            (1, 2, 3): [0, 4255],
            (1, 1, 4): [0, 4256],
            (1, 2, 4): [0, 4257],
            (2, 2, 3): [0, 4258],
            (2, 2, 4): [0, 4259],

            (2, 2, 5): [0, 4440],
            (2, 2, 6): [0, 4441]
        }

        try:
            for i in self.data:
                k = (i[1], i[2], i[4])
                if k in rows:
                    rows[k][0] += i[0]

            for k, v in rows.iteritems():
                row = ChartdataTmpl.gen(self.next_dt.strftime('%Y%m%d'))()
                row.ds_id = v[1]
                row.time = self.next_dt
                row.data = v[0]
                self.sakuya_db.add(row)
            self.sakuya_db.commit()
            logging.info('%d extra rows inserted.' % len(rows))

        except Exception, e:
            self.sakuya_db.rollback()
            logging.exception('Fail to stats extra.')

if __name__ == '__main__':
    Job().run()
