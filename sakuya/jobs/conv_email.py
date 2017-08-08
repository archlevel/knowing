# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Users

def main():
    session = sessionmaker(bind=engine_sakuya_db)()
    for row in session.query(Users):
        if row.mobile:
            row.email = '%s@139.com' % row.mobile
    session.commit()

if __name__ == '__main__':
    main()
