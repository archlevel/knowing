# -*- coding: utf-8 -*-

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, Categories, Follows
from sakuya.controllers.admin import chart as admin_chart_controller

def main():
    session = sessionmaker(bind=engine_sakuya_db)()

    print '### root category'
    for row in session.query(Charts):

        if row.cate_id == 100:
            row.root_category = 2
            continue

        pid = admin_chart_controller.get_parent_category(session, row.cate_id)
        if pid:
            row.root_category = pid
            print row.id, pid
        else:
            print row.id, 'no pid'

    session.commit()

    print '### followers'
    for row in session.query(Follows.cid, func.count('*').label('cnt')).group_by(Follows.cid):
        chart = session.query(Charts).get(row.cid)
        if chart is None:
            print row.cid, 'not found'
            continue
        chart.followers = row.cnt
        print chart.id, row.cnt

    session.commit()

if __name__ == '__main__':
    main()
