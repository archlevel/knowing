# -*- coding: utf-8 -*-

import json
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts
from sakuya.lib import storm

def main():
    session = sessionmaker(bind=engine_sakuya_db)()

    for row in session.query(Charts):
        if 'spider' in row.name:
            ext = row.get_ext()
            if 'rule' in ext:
                storm.set_rule(row.id, json.dumps(ext['rule']))
                print row.id, row.name

if __name__ == '__main__':
    main()
