# -*- coding: utf-8 -*-

import re
import logging
import datetime
import msgpack
from sakuya.config import get_config

PRODS = [(1, '竞价'), (2, '定价')]
CHARTS = [(1, '曝光量'), (2, '有效点击量'), (3, '无效点击量'), (4, '扣费量')]
CITIES = [(11, '上海'), (14, '北京'), (1000, 'OTH'), (1001, 'DB04')]
CHANNELS = [(1, '网站'), (2, '手机'),(7, 'Touchweb'),(13, 'Pad')]
ENTRIES = [(1, '地图小区页'),
           (2, '房源单页底部推荐'),
           (3, '二手房列表小区关键字页面'),
           (4, '精选房源页面'),
           (5, '小区房源'),
           (6, '小区精选房源'),
           (7, '小区热门房源'),
           (8, '小区单价房源'),
           (9, '小区房源右面'),
           (10, '房贷计算器'),
           (11, '列表第一'),
           (12, '列表第三'),
           (13, '列表第五'),
           (14, '城市首页推荐位'),
           (30, '店铺二手房列表页'),
           (31, '店铺租房列表页'),
           (32, '店铺首页'),
           (50, '二手房筛选'),
           (80, '租房筛选列表页'),
           (81, '租房搜索列表页'),
           (82, '小区租房列表页'),
           (96, '经纪人姓名关键字'),
           (97, '经纪人手机关键字'),
           (98, '其他'),
           (99, '不收费点击'),
           (123, 'Pad')]

CHARTS_DISPLAY = [(1, '曝光量'), (2, '点击量'), (4, '扣费量')]

D_PRODS = dict(PRODS)
D_CHARTS = dict(CHARTS)
D_CITIES = dict(CITIES)
D_CHANNELS = dict(CHANNELS)
D_ENTRIES = dict(ENTRIES)

D_CHARTS_DISPLAY = dict(CHARTS_DISPLAY)

def fill_data(data):

    rows = {}
    for item in data:

        if len(item) < 6:
            logging.info('malformed %s' % str(item))
            continue

        key = item[1:6]

        if key[0] not in D_PRODS\
                or key[1] not in D_CHARTS\
                or key[2] not in D_CITIES\
                or key[3] not in D_CHANNELS\
                or key[4] not in D_ENTRIES:
            logging.info('unrecognized %s' % str(item))
            continue

        if key not in rows:
            rows[key] = 0
        rows[key] += item[0]

        for i in xrange(1, 8):
            key_ = list(key)
            if i & 1 == 1:
                key_[4] = 0
            if i & 2 == 2:
                key_[3] = 0
            if i & 4 == 4:
                key_[2] = 0
            key_ = tuple(key_)
            if key_ not in rows:
                rows[key_] = 0
            rows[key_] += item[0]

    return rows

_charts = None
_charts_expiry = datetime.datetime.now()

def get_charts(no_cache=False):
    global _charts, _charts_expiry
    #now = datetime.datetime.now()
    #if now > _charts_expiry or no_cache:
    #    _charts_expiry = now + datetime.timedelta(minutes=5)

    try:
        with file(get_config('webapp')['hp_aggregate_charts']) as f:
            _charts = msgpack.unpackb(f.read())
    except Exception:
        pass

    if not isinstance(_charts, dict):
        _charts = {}

    return _charts

def get_id2(id):
    d_charts = get_charts()
    chart_key = None
    for k, v in d_charts.iteritems():
        if v == id:
            chart_key = k
            break

    if chart_key is None:
        return None

    id2 = None
    if chart_key[1] == 2: # effective clicks
        key2 = list(chart_key); key2[1] = 3; key2 = tuple(key2)
        if key2 not in d_charts:
            return None
        return d_charts[key2]

PTRN_TITLE = re.compile('^hp-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+$')
HAOPAN_CATEGORIES = (100, 204, 212, 213)

def is_haopan(cid):
    return cid in HAOPAN_CATEGORIES

def format_title(title):

    try:
        if PTRN_TITLE.match(title) is None:
            return title

        chart_key = tuple(int(i) for i in title.split('-')[1:6])
        titles = []
        titles.append(D_PRODS[chart_key[0]])
        if chart_key[2]:
            titles.append(D_CITIES[chart_key[2]])
        if chart_key[3]:
            titles.append(D_CHANNELS[chart_key[3]])
        if chart_key[4]:
            titles.append(D_ENTRIES[chart_key[4]])
        titles.append(D_CHARTS_DISPLAY[chart_key[1]])
        return ' - '.join(titles)

    except Exception, e:
        return title
