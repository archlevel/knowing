# -*- coding: utf-8 -*-

import json
from sakuya.models.sakuya_db import WarnRules

def get_warn(sakuya_db, chart_id):

    warn = []
    for row in sakuya_db.\
               query(WarnRules).\
               filter_by(chart_id=chart_id).\
               order_by(WarnRules.id):

        i = json.loads(row.content)
        i['id'] = row.id
        warn.append(i)

    return warn
