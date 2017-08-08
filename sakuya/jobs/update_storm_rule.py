# -*- coding: utf-8 -*-

import json
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts
from sakuya.lib import storm

def main():
    session = sessionmaker(bind=engine_sakuya_db)()

    for row in session.query(Charts).filter_by(cate_id=200):

        ext = row.get_ext()

        if 'rule' not in ext:
            print chart.id, 'rule not found'
            continue

        if ext['rule']['field'] == 'upstream_response_time':
            ext['rule']['field'] = 'request_time'

        for filter in ext['rule']['filters']:
            if filter[0] == 'upstream_response_time':
                filter[0] = 'request_time'

        row.ext_info = json.dumps(ext)
        session.commit()
        storm.set_rule(row.id, json.dumps(ext['rule']))
        print row.id, 'updated'

if __name__ == '__main__':
    main()
