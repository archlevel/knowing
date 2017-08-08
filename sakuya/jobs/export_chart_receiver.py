# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, Categories, Users, Follows
from sakuya.lib import haopan

session = sessionmaker(bind=engine_sakuya_db)()

def main():
    top_category(2)
    top_category(3)
    haopan_category()

def top_category(pid):
    cate1 = session.query(Categories).get(pid)
    for cate2 in session.query(Categories).filter_by(parent_cate_id=cate1.id):
        for cate3 in session.query(Categories).filter_by(parent_cate_id=cate2.id):
            for chart in session.query(Charts).filter_by(cate_id=cate3.id):
                line = u'\t'.join((cate1.name, cate2.name, cate3.name, chart.name, get_receivers(chart.id)))
                print line.encode('utf-8')

def haopan_category():
    for chart in session.query(Charts).filter_by(cate_id=100):
        title = haopan.format_title(chart.name)
        if title.startswith('hp-'):
            continue
        line = u'监控\t二手房\t好盘\t%s\t%s' % (title.decode('utf-8'), get_receivers(chart.id))
        print line.encode('utf-8')

def get_receivers(chart_id):
    receivers = []
    for follow in session.query(Follows).filter_by(cid=chart_id):
        if follow.recv_warning:
            user = session.query(Users).get(follow.follower)
            if user is None:
                continue
            receivers.append(user.truename)
    if receivers:
        return u'、'.join(receivers)
    else:
        return u'无'

if __name__ == '__main__':
    main()
