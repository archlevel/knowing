# -*- coding: utf-8 -*-

from bottle.ext import sqlalchemy
from sqlalchemy import create_engine

from sakuya.config import get_config
from sakuya.models import sakuya_db, db_monitor

URI_FORMAT = '%(adapter)s://%(username)s:%(password)s@%(host)s:%(port)d/%(database)s?charset=utf8&use_unicode=1'
db_config = get_config('database')

engine_sakuya_db = create_engine(URI_FORMAT % db_config['sakuya_db'],
                                 echo=db_config['sakuya_db']['echo'],
                                 pool_recycle=3600)
plugin_sakuya_db = sqlalchemy.Plugin(engine_sakuya_db,
                                     sakuya_db.Base.metadata,
                                     keyword='sakuya_db',
                                     use_kwargs=True)

engine_db_monitor = create_engine(URI_FORMAT % db_config['db_monitor'],
                                  echo=db_config['db_monitor']['echo'],
                                  pool_recycle=3600)
plugin_db_monitor = sqlalchemy.Plugin(engine_db_monitor,
                                      db_monitor.Base.metadata,
                                      keyword='db_monitor',
                                      use_kwargs=True)

def init_db():
    sakuya_db.Base.metadata.create_all(bind=engine_sakuya_db)

def drop_db():
    sakuya_db.Base.metadata.drop_all(bind=engine_sakuya_db)
