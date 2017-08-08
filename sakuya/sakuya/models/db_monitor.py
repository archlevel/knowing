# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SlowDaily(Base):
    __tablename__ = 't_slow_daily'
    id = Column('f_id', Integer, primary_key=True)
    date = Column('f_date', Date)
    slow = Column('f_slow', Integer)
    query = Column('f_query', Integer)

class MysqlDaily(Base):
    __tablename__ = 't_db_mysql_status_daily'
    id = Column('f_id', Integer, primary_key=True)
    date = Column('f_report_date', Date)
    read = Column('mysql_read', Integer)
    write = Column('mysql_write', Integer)
