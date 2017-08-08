# -*- coding: utf-8 -*-

import json
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, WarnRules, Follows

def main():
    session = sessionmaker(bind=engine_sakuya_db)()

    for row in session.\
               query(Charts).\
               filter_by(alert_enable=1):

        warn = row.get_ext().get('warn')
        if not warn:
            row.alert_enable = 0
            continue

        for item in warn:
            r = WarnRules()
            r.chart_id = row.id
            r.content = json.dumps({
                'duration_start': item[0],
                'duration_end': item[1],
                'type': item[2],
                'hwm_warning': item[3],
                'hwm_critical': item[4],
                'lwm_warning': item[5],
                'lwm_critical': item[6],
                'latency': item[7],
                'interval': item[8]
            })
            session.add(r)

        print row.id, len(warn)

    session.commit()

    cnt = 0
    for row in session.\
               query(Follows).\
               filter_by(recv_warning=1):
        row.recv_rules = 'all'
        cnt += 1
    session.commit()
    print 'update %d follows' % cnt

if __name__ == '__main__':
    main()
