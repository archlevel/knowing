# -*- coding: utf-8 -*-

import logging
import argparse
import datetime
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, ChartdataTmpl, ChartdataDaily
from sakuya.lib import util

PER_FETCH = 100

class Job(object):

    def __init__(self, args):
        self.args = args

    def run(self):

        util.setup_logging('aggregate_daily', False, self.args.verbose)

        logging.info('Aggregating chart data of %s.' % self.args.date.strftime('%Y-%m-%d'))

        self.session = sessionmaker(bind=engine_sakuya_db)()
        self.Chartdata = ChartdataTmpl.gen(self.args.date.strftime('%Y%m%d'))

        last_id = 0
        while True:
            charts = self.session.\
                     query(Charts).\
                     filter(Charts.id > last_id).\
                     order_by(Charts.id).\
                     limit(PER_FETCH).\
                     all()
            self.session.expunge_all()

            for chart in charts:
                try:
                    self.process_chart(chart)
                except Exception, e:
                    logging.exception('Fail to process chart %d' % chart.id)
                    self.session.rollback()

            if len(charts) < PER_FETCH:
                break

            last_id = charts[-1].id

        logging.info('Job done.')

    def process_chart(self, chart):

        ext = chart.get_ext()
        if 'rule' in ext and ext['rule']['rule_type'] != 'count':
            logging.debug('Skip non-count storm chart %d' % chart.id)
            return

        result = self.session.\
                 query(func.sum(self.Chartdata.data)).\
                 filter_by(ds_id=chart.id).\
                 scalar()

        if result is None:
            logging.debug('Proccess chart %d, sum is NULL.' % chart.id)
            return

        row = ChartdataDaily()
        row.ds_id = chart.id
        row.time = self.args.date
        row.data = result
        self.session.add(row)
        self.session.commit()

        logging.info('Process chart %d, sum is %d' % (chart.id, result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', help='%%Y-%%m-%%d')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.date:
        try:
            dt = datetime.datetime.strptime(args.date, '%Y-%m-%d')
        except Exception:
            parser.error('Invalid --date argument: %s' % args.date)
        args.date = dt
    else:
        args.date = datetime.datetime.now() - datetime.timedelta(days=1)
        args.date = args.date.replace(hour=0, minute=0, second=0, microsecond=0)

    Job(args).run()
