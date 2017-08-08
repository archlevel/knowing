# -*- coding: utf-8 -*-

import signal
import time
import logging
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import ChartdataTmpl
from sakuya.lib import util

class Job(object):

    interrupted = False

    def __init__(self):

        util.setup_logging('check_logtime', True)

        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        if signum == signal.SIGTERM or signum == signal.SIGINT:
            self.interrupted = True

    def run(self):

        self.session = sessionmaker(bind=engine_sakuya_db)()

        while not self.interrupted:
            try:
                self.check()
            except Exception, e:
                logging.exception('fail to check')

            time.sleep(5)

    def check(self):

        Chartdata = ChartdataTmpl.gen(time.strftime('%Y%m%d'))

        for id in (839, 981, 3503, 4426):
            row = self.session.\
                       query(Chartdata).\
                       filter_by(ds_id=id).\
                       order_by(Chartdata.time.desc()).\
                       first()

            if row is None:
                logging.info('id %d row is none' % id)
            else:
                logging.info('id %d time is %s' % (id, row.time.strftime('%Y-%m-%d %H:%M:%S')))

        self.session.close()

if __name__ == '__main__':
    Job().run()
