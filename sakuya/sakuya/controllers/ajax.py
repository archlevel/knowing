# -*- coding: utf-8 -*-

import datetime
from bottle import request, response
from sakuya import app
from sakuya.models.sakuya_db import Events, LogstuffTmpl, Charts, Events
from json import JSONEncoder
from sqlalchemy import func

@app.get('/ajax/events')
def events(sakuya_db):
    """
    return the undealed events' count in json
    """

    warning = sakuya_db.\
              query(Charts.id).\
              filter(Charts.warnings > 0).\
              all()

    critical = sakuya_db.\
               query(Charts.id).\
               filter(Charts.criticals > 0).\
               all()

    result = {'warning': len(warning), 'critical': len(critical)}

    if request.params.get('detail') == 'true':

        def get_detail(charts, level):
            detail = []
            for row in charts:
                event = sakuya_db.\
                        query(Events).\
                        filter_by(cid=row.id, type=level).\
                        order_by(Events.id.desc()).\
                        first()
                if event is None:
                    continue
                detail.append({
                    'cid': event.cid,
                    'info': event.info,
                    'time': event.time.strftime('%H:%M')
                })
            return detail

        if warning:
            result['warning_detail'] = get_detail(warning, Events.CONST_TYPE_WARNING)
        if critical:
            result['critical_detail'] = get_detail(critical, Events.CONST_TYPE_CRITICAL)

    return result

@app.post('/ajax/events/solve')
def events_solve(sakuya_db):
    """
    solve the events requested

    return the result
    """

    if not request.params['event_id']:
        return {"status": "error"}

    event_id = request.params['event_id']

    row = sakuya_db.query(Events).filter(Events.id==event_id).first()

    row.deal_status = 1

    sakuya_db.commit()
    return {"status": "ok", "event_id": event_id}

@app.get('/ajax/detail')
def detail(sakuya_db):

    try:
        tid = int(request.params['tid'])
        dt = datetime.datetime.strptime(request.params['dt'], '%Y-%m-%d %H:%M')

    except Exception, e:
        return ''

    Logstuff = LogstuffTmpl.gen(dt.strftime('%Y%m%d'))
    row = sakuya_db.\
          query(Logstuff.detail).\
          filter_by(ds_id=tid, time=dt).\
          order_by(Logstuff.id.desc()).\
          first()

    if row is None or row.detail is None:
        return ''

    return row.detail.replace('\n', '<br>')
