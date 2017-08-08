# -*- coding: utf-8 -*-

charts_yaml = '''
---
AnjukeAPI:
  request: 207
  speed: 137
  host: api.anjuke.com
  api:
    - admin.writeAppLog
    - property.getDescription
    - property.searchV3
    - haopantong.click
    - community.searchMap
    - community.get
    - city.get
    - admin.writeCrashLog
    - location.getCity
    - property.searchV2
    - community.autoComplete
    - city.getFilters
    - property.view
    - admin.recordaction
    - property.home
    - broker.getevaluate
    - favorites.history
    - city.getList

HaozuAPI:
  request: 208
  speed: 147
  host: api.haozu.com
  api:
    - /2.0/property.get
    - /2.0/recommend.getAction
    - /2.0/property.searchByLngLat
    - /2.0/community.searchMapByLngLat
    - /2.0/property.searchByComm
    - /2.0/property.searchByArea
    - /1.0/property.searchDetailV2
    - /2.0/community.autocomplete
    - /1.0/property.get
    - /2.0/recommend.getProperty
    - /1.0/community.searchMapV2
    - /2.0/property.searchByMetro
    - /2.0/community.get
    - /1.0/city.getList
    - /1.0/community.autocompleteV2
    - /1.0/keywords.autocomplete
    - /2.0/auth.signin
    - /2.0/favorite.getList
    - /1.0/community.get
    - /2.0/favorite.add

AifangAPI:
  request: 209
  speed: 154
  host: api.aifang.com
  api:
    - /loupan/list
    - /loupan/view
    - /props/searchList
    - /housetype/view
    - /tese/list
    - /loupan/DetailView
    - /props/view
    - /loupan/propsList
    - /suggest
    - /dongtai/view
    - /loupan/traffic
    - /housetype/list
    - /props/mapList
    - /props/dics
'''

import yaml
import datetime
import json
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, Follows
from sakuya.lib import storm

session = sessionmaker(bind=engine_sakuya_db)()

def main():
    for dprt, info in yaml.load(charts_yaml).iteritems():
        for api in info['api']:
            add_chart(info['request'], '%s %s Request' % (dprt, api), 'count', info['host'], api)
            add_chart(info['speed'], '%s %s 90%% Speed' % (dprt, api), 'ninety', info['host'], api)

def add_chart(cate_id, title, rule_type, host, api):

    if session.query(Charts).filter_by(name=title).count():
        print title, 'exists'
        return

    # make rule
    rule = {
        'datasource': 'access_log',
        'logging': False,
        'filters': [
            ['host', 'equals', False, host],
            ['request_url', 'regex', False, '.*?%s.*' % api]
        ]
    }
    if rule_type == 'count':
        rule['rule_type'] = 'count'
        rule['field'] = None
    elif rule_type == 'ninety':
        rule['rule_type'] = 'ninety'
        rule['field'] = 'upstream_response_time'
    else:
        assert False

    # make warn
    warn = [
        ["00:00", "08:59", "RANGE", "200", "400", "30", "50", "60", "5"],
        ["09:00", "20:59", "RANGE", "200", "400", "30", "50", "5", "2"],
        ["21:00", "23:59", "RANGE", "200", "400", "30", "50", "60", "5"]
    ]

    # add chart
    row = Charts()
    row.name = title
    row.cate_id = cate_id
    row.owner = 'mingshi'
    row.ext_info = json.dumps({'rule': rule})
    row.alert_enable = 0
    row.createtime = datetime.datetime.now()
    session.add(row)
    session.flush()
    rowid = row.id

    # add follow
    follow = Follows()
    follow.cid = rowid
    follow.follower = 19
    follow.recv_warning = True
    session.add(follow)

    session.commit()

    # storm
    storm.set_rule(rowid, json.dumps(rule))

    print title, 'added'

if __name__ == '__main__':
    main()
