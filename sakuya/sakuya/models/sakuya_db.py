# -*- coding: utf-8 -*-

import json
import threading
from bottle.ext import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Charts(Base):
    __tablename__ = 't_charts'

    id = Column('id', Integer, primary_key=True)
    name = Column('f_name', String(200))
    owner = Column('f_owner', String(100))
    cate_id = Column('f_cate_id', Integer, ForeignKey('t_categories.id'))
    createtime = Column('f_createtime', DateTime)

    ds_id = Column('f_ds_id', Integer, default=0)
    ds_tbl_name = Column('f_ds_tbl_name', String(255), default='')
    ext_info = Column('f_ext_info', Text, default='')
    followers = Column('f_followers', Integer, default=0)
    alert_enable = Column('f_alert_enable', Integer, default=0)

    warnings = Column('f_alert_hwm_warning', Integer, default=0)
    criticals = Column('f_alert_hwm_critical', Integer, default=0)

    api_ip = Column('f_alert_lwm_warning', Integer, default=0)
    api_ts = Column('f_alert_lwm_critical', Integer, default=0)

    root_category = Column('f_alert_latency', Integer, default=0)

    status = Column('f_status', Integer, default=1)

    def get_ext(self):
        if not self.ext_info:
            return {}
        try:
            ext = json.loads(self.ext_info)
            if not isinstance(ext, dict):
                raise ValueError
        except Exception, e:
            return {}
        return ext

class WarnRules(Base):
    __tablename__ = 't_warn_rules'

    id = Column('id', Integer, primary_key=True)
    chart_id = Column('f_chart_id', Integer)
    content = Column('f_content', String(255))

class Categories(Base):
    __tablename__ = 't_categories'

    id= Column('id', Integer, primary_key=True)
    name = Column('f_name', String(50))
    parent_cate_id= Column('f_parent_cate_id', Integer)
    is_parent = Column('f_is_parent', Boolean)
    order = Column('f_order', Integer, default=0)

    charts = relationship('Charts', backref='category', lazy='dynamic')

class Follows(Base):
    __tablename__ = 't_follows'

    id = Column('id', Integer, primary_key=True)
    cid = Column('f_cid', Integer)
    follower = Column('f_follower', Integer)
    recv_warning = Column('f_recv_warning', Boolean)
    recv_rules = Column('f_recv_rules', String(255))

    def get_recv_rules(self):
        if not self.recv_rules:
            return []
        elif self.recv_rules == 'all':
            return self.recv_rules
        recv_rules = []
        for i in self.recv_rules.split(','):
            try:
                recv_rules.append(int(i))
            except Exception:
                continue
        return recv_rules

class Events(Base):
    __tablename__ = 't_events'

    CONST_TYPE_OK = 0
    CONST_TYPE_WARNING = 1
    CONST_TYPE_CRITICAL = 2

    CONST_STATUS_UNDEALT = 0
    CONST_STATUS_DEALT = 1

    id = Column('id', Integer, primary_key=True)
    cid = Column('f_cid', Integer)
    info = Column('f_info', String(255))
    time = Column('f_time', DateTime)
    type = Column('f_type', Integer) # 0:ok 1:warning 2:critical
    deal_status = Column('f_deal_status', Integer) # 0:not yet 1:solved

class Users(Base):
    __tablename__  = 't_users'

    id = Column('id', Integer, primary_key=True)
    username = Column('f_username', String(255), unique=True)
    truename = Column('f_truename', String(255))
    email = Column('f_email', String(255))
    mobile = Column('f_mobile', String(11))

class ChartdataTmpl(object):

    _lock = threading.Lock()
    _tmpl = {}

    @classmethod
    def gen(cls, date):

        name = 't_chartdata_%s' % date

        if name in cls._tmpl:
            return cls._tmpl[name]

        with cls._lock:
            if name not in cls._tmpl:
                cls._tmpl[name] = type(name, (Base,), {'__tablename__': name,
                                                       'id': Column('id', Integer, primary_key=True),
                                                       'ds_id': Column('f_ds_id', Integer),
                                                       'time': Column('f_time', DateTime),
                                                       'data': Column('f_data', Integer)
                                                       })
            return cls._tmpl[name]

class ChartdataWeekly(Base):
    __tablename__ = 't_chartdata_weekly'
    id = Column('id', Integer, primary_key=True)
    ds_id = Column('f_ds_id', Integer)
    time = Column('f_time', DateTime)
    data = Column('f_data', Integer)

class ChartdataMonthly(Base):
    __tablename__ = 't_chartdata_monthly'
    id = Column('id', Integer, primary_key=True)
    ds_id = Column('f_ds_id', Integer)
    time = Column('f_time', DateTime)
    data = Column('f_data', Integer)

class ChartdataQuarterly(Base):
    __tablename__ = 't_chartdata_quarterly'
    id = Column('id', Integer, primary_key=True)
    ds_id = Column('f_ds_id', Integer)
    time = Column('f_time', DateTime)
    data = Column('f_data', Integer)

class ChartdataDaily(Base):
    __tablename__ = 't_chartdata_daily'
    id = Column('id', Integer, primary_key=True)
    ds_id = Column('f_ds_id', Integer)
    time = Column('f_time', DateTime)
    data = Column('f_data', Integer)

class LogstuffTmpl(object):

    _lock = threading.Lock()
    _tmpl = {}

    @classmethod
    def gen(cls, date):

        name = 't_logstuff_%s' % date

        if name in cls._tmpl:
            return cls._tmpl[name]

        with cls._lock:
            if name not in cls._tmpl:
                cls._tmpl[name] = type(name, (Base,), {'__tablename__': name,
                                                       'id': Column('id', Integer, primary_key=True),
                                                       'ds_id': Column('f_ds_id', Integer),
                                                       'time': Column('f_time', DateTime),
                                                       'detail': Column('f_detail', Text)
                                                       })
            return cls._tmpl[name]
