# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import os
import shutil
import argparse
import msgpack
import time
import datetime
import logging
from sqlalchemy.orm import sessionmaker
from sakuya.lib import haopan, util
from sakuya.config import get_config
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts

CHARTFILE = get_config('webapp')['hp_aggregate_charts']
CATEGORY_ID = 100

class Job:

    def run(self):

        util.setup_logging('hp_create')

        self.sakuya_db = sessionmaker(bind=engine_sakuya_db)()

        data = []
        for i in haopan.PRODS:
            for j in haopan.CHARTS:
                for k in haopan.CITIES:
                    for l in haopan.CHANNELS:
                        for m in haopan.ENTRIES:
                            data.append((0, i[0], j[0], k[0], l[0], m[0]))

        chart_keys = haopan.fill_data(data).keys()

        charts = None
        try:
            with file(CHARTFILE) as f:
                charts = msgpack.unpackb(f.read())
        except Exception:
            pass

        if not isinstance(charts, dict):
            charts = {}

        stats = [0, 0]
        for key in chart_keys:
            if key not in charts:
                id = self.new_chart(key)
                if id is not None:
                    charts[key] = id
                    stats[0] += 1
                else:
                    stats[1] += 1
            else:
                logging.info('skip %s' % str(key))

        if stats[0]:

            if os.path.isfile(CHARTFILE):
                shutil.copyfile(CHARTFILE, CHARTFILE + '.' + time.strftime('%Y%m%d%H%M%S'))

            with file(CHARTFILE, 'w') as f:
                f.write(msgpack.packb(charts))

        logging.info('%d charts created, %d failed.' % tuple(stats))

    def new_chart(self, k):

        try:
            row = Charts()
            row.name = 'hp-' + '-'.join(str(i) for i in k)
            row.owner = ''
            row.cate_id = CATEGORY_ID
            row.ds_id = 0
            row.ds_tbl_name = ''
            row.ext_info = ''
            row.followers = 0
            row.createtime = datetime.datetime.now()
            self.sakuya_db.add(row)
            self.sakuya_db.commit()

            logging.info('Create chart %d - %s' % (row.id, row.name))

            return row.id

        except Exception:
            self.sakuya_db.rollback()
            logging.exception('Fail to create chart %s' % str(k))
            return None

        finally:
            try:
                f.close()
            except Exception:
                pass

if __name__ == '__main__':
    Job().run()
