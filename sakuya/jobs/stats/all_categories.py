# -*- coding: utf-8 -*-

import datetime
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Categories
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

def main():
    d = {}
    with open('/home/jizhang/knowing.log/cate.log') as f:
        for l in f:
            cols = l.split('\t')
            d[int(cols[0])] = int(cols[1])

    for id, count in d.iteritems():
        category = get_category(id)
        if not category:
            continue
        print '%d\t%s\t%d' % (id, get_category(id), count)

if __name__ == '__main__':
    main()
