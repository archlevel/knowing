# -*- coding: utf-8 -*-

from bottle import abort, request, redirect
from sakuya import app, view
from sakuya.models.sakuya_db import Events
from sakuya.lib import util

EVENTS_PER_PAGE = 10

@app.get('/alert')
@view('alert')
def index(sakuya_db):

    try:
        level = int(request.params.get('level', -1))
        status = int(request.params.get('status', Events.CONST_STATUS_UNDEALT))
        page = int(request.params.get('page', 1))

        if level not in (-1, Events.CONST_TYPE_WARNING, Events.CONST_TYPE_CRITICAL):
            raise ValueError
        if status not in (-1, Events.CONST_STATUS_UNDEALT, Events.CONST_STATUS_DEALT):
            raise ValueError
        if page < 1:
            raise ValueError

    except Exception, e:
        redirect('/alert')

    query = sakuya_db.query(Events)
    if level != -1:
        query = query.filter_by(type=level)
    if status != -1:
        query = query.filter_by(deal_status=status)
    query = query.\
            order_by(Events.id.desc()).\
            offset((page - 1) * EVENTS_PER_PAGE).\
            limit(EVENTS_PER_PAGE)

    ret = []
    for i in query:
        _level = "OK"
        if i.type == Events.CONST_TYPE_WARNING:
            _level = "warning"
        elif i.type == Events.CONST_TYPE_CRITICAL:
            _level = "critical"

        ret.append({
                    "id": i.id,
                    "cid": i.cid,
                    "time": i.time,
                    "level": _level,
                    "message": i.info,
                    "status": i.deal_status
                   })

    if page == 1:
        prev_page = 1
        next_page = 2
    else:
        prev_page = page - 1
        next_page = page + 1

    return {"events": ret, "prev_page": prev_page, "next_page": next_page,
            'page': page, 'level': level, 'status': status}

