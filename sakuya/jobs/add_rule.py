# -*- coding: utf-8 -*-

import json
import argparse
import datetime
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, WarnRules

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--chart-id', action='append', type=int, required=True)
    parser.add_argument('-ds', '--duration-start', default='00:00')
    parser.add_argument('-de', '--duration-end', default='23:59')
    parser.add_argument('-t', '--type', choices=('HWM', 'LWM', 'RANGE'), required=True)
    parser.add_argument('-hw', '--hwm-warning', type=int)
    parser.add_argument('-hc', '--hwm-critical', type=int)
    parser.add_argument('-lw', '--lwm-warning', type=int)
    parser.add_argument('-lc', '--lwm-critical', type=int)
    parser.add_argument('-l', '--latency', type=int, default=5)
    parser.add_argument('-i', '--interval', type=int, default=5)
    args = parser.parse_args()

    try:
        duration_start = datetime.datetime.strptime(args.duration_start, '%H:%M')
        duration_end = datetime.datetime.strptime(args.duration_end, '%H:%M')
    except Exception:
        print 'duration start/end error (HH:MM)'
        return

    if args.type == 'HWM' and (args.hwm_warning is None or args.hwm_critical is None):
        print 'hwm warning/critical error'
        return
    elif args.type == 'LWM' and (args.lwm_warning is None or args.lwm_critical is None):
        print 'lwm warning/critical error'
        return
    elif args.type == 'RANGE' and (args.hwm_warning is None or args.hwm_critical is None
                                   or args.lwm_warning is None or args.lwm_critical is None):
        print 'lwm/hwm warning/critical error'
        return

    if args.latency <= 0 or args.interval <= 0:
        print 'latency or interval not positive.'
        return

    content = {
        'duration_start': args.duration_start,
        'duration_end': args.duration_end,
        'type': args.type,
        'hwm_warning': args.hwm_warning,
        'hwm_critical': args.hwm_critical,
        'lwm_warning': args.lwm_warning,
        'lwm_critical': args.lwm_critical,
        'latency': args.latency,
        'interval': args.interval
    }

    session = sessionmaker(bind=engine_sakuya_db)()
    cnt = 0
    for chart_id in args.chart_id:
        chart = session.query(Charts).get(chart_id)
        if chart is None:
            print 'chart %d not found' % chart_id
            continue
        chart.alert_enable = 1

        row = WarnRules()
        row.chart_id = chart_id
        row.content = json.dumps(content)
        session.add(row)
        cnt += 1
    session.commit()
    print 'added %d rules' % cnt

if __name__ == '__main__':
    main()
