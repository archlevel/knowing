# -*- coding: utf-8 -*-

import json
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts

def main():
    session = sessionmaker(bind=engine_sakuya_db)()

    for row in session.query(Charts):
        ext = row.get_ext()
        if 'rule' not in ext:
            continue
        if ext['rule'].get('logging', False):
            if 'spider' in row.name:
                ext['rule']['logging'] = False
                row.ext_info = json.dumps(ext)
                print row.id, row.name
    session.commit()

if __name__ == '__main__':
    main()
