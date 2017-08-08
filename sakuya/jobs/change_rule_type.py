# -*- coding: utf-8 -*-

import sys
import json
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import WarnRules

def main():
    session = sessionmaker(bind=engine_sakuya_db)()
    for row in session.query(WarnRules).filter(WarnRules.id.in_(sys.argv[1:])):
        content = json.loads(row.content)
        content['type'] = 'LWM'
        content['lwm_warning'] = 0
        content['lwm_critical'] = 0
        row.content = json.dumps(content)
        print row.id
    session.commit()

if __name__ == '__main__':
    main()
