# -*- coding: utf-8 -*-

import json
import datetime
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, ChartdataTmpl

def main():

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    Chartdata = ChartdataTmpl.gen(yesterday.strftime('%Y%m%d'))

    start_time = yesterday.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=10, minute=59, second=59, microsecond=999)

    session = sessionmaker(bind=engine_sakuya_db)()

    total = {'access_log': 0, 'soj': 0}
    useless = {'access_log': [], 'soj': []}

    for chart in session.query(Charts).order_by(Charts.id):
        ext = chart.get_ext()

        if 'rule' not in ext:
            continue

        datasource = ext['rule']['datasource']
        total[datasource] += 1

        if chart.cate_id == 200:
            continue

        peak_sum = session.query(func.sum(Chartdata.data)).\
                   filter_by(ds_id=chart.id).\
                   filter(Chartdata.time >= start_time, Chartdata.time <= end_time).\
                   scalar()

        if peak_sum is None:
            peak_sum = 0

        if peak_sum < 50:
            useless[datasource].append((chart.id, chart.name, peak_sum))

    print 'Total - access_log: %d, soj: %d' % (total['access_log'], total['soj'])
    for datasource, charts in useless.iteritems():
        print 'Useless Charts - %s:' % datasource
        for chart in charts:
            print '%7d, %s, %d' % (chart[0], chart[1].encode('utf-8'), chart[2])


if __name__ == '__main__':
    main()
