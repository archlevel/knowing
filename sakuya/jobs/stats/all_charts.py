# -*- coding: utf-8 -*-

import datetime
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, Categories, Users, Follows
from sakuya.lib import haopan

session = sessionmaker(bind=engine_sakuya_db)()

def get_category(id):
    cates = []
    while id > 1:
        cate = session.query(Categories).get(id)
        if cate is None:
            break
        cates.append(cate.name.encode('utf-8'))
        id = cate.parent_cate_id
    return ' / '.join(reversed(cates))

def get_truename(username):
    user = session.query(Users).filter_by(username=username).first()
    if user is not None:
        return user.truename.encode('utf-8')
    else:
        return '系统'

def load_file(filename):
    d = {}
    with open(filename) as f:
        for l in f:
            cols = l.split('\t')
            if len(cols) == 2:
                d[int(cols[0])] = int(cols[1])
            else:
                d[int(cols[0])] = [int(i) for i in cols[1:]]
    return d

def main():

    chart_count = load_file('/home/jizhang/knowing.log/chart.log')
    dt_count = dict((id, count[0]) for id, count in chart_count.iteritems())
    vp_count = dict((id, count[1]) for id, count in chart_count.iteritems())

    event_count = load_file('/home/jizhang/knowing.log/event.log')
    follow_count = load_file('/home/jizhang/knowing.log/follow.log')
    warning_count = load_file('/home/jizhang/knowing.log/warning.log')

    print 'ID\t栏目\t标题\t创建人\t单页访问次数\t数据调用次数\t报警开启\t报警次数\t订阅人数\t接警人数'
    for chart in session.query(Charts):
        category = get_category(chart.cate_id)
        title = chart.name.encode('utf-8')
        if not category or category.startswith('Solr') or category.startswith('Suite'):
            continue
        if category.startswith('Haopan'):
            category = '监控 / 二手房 / 好盘'
            title = haopan.format_title(title)
            if title.startswith('hp'):
                continue

        if chart.alert_enable:
            alert_enable = 1
        else:
            alert_enable = 0

        info = [chart.id, category, title, get_truename(chart.owner),
                vp_count.get(chart.id, 0), dt_count.get(chart.id, 0),
                alert_enable, event_count.get(chart.id, 0),
                follow_count.get(chart.id, 0), warning_count.get(chart.id, 0)]
        print '\t'.join((str(s) for s in info))

if __name__ == '__main__':
    main()
