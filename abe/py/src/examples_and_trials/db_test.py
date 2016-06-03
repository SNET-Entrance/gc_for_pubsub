#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on 11.06.2015

@author: al
'''
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
DEBUG=2
    
import sqlalchemy
from sqlalchemy.orm import sessionmaker, create_session
from model.db.sqlalchemy_declarative.gc import Base,AbeGroupGc   
from model.db.mysql_dbconfig import read_db_config

from model.db.data_access import DataAccess

#echeck exists id
if __name__ == '__main__':

    dao = DataAccess()
    dao.connect('gc_config.ini')
    dao.setSQLAlchemyModel(AbeGroupGc)
    print(dao.isExists(1, 'group_id'))
    
#connect
if __name__ == '!__main__':
    db = read_db_config(os.path.join(os.path.dirname(__file__), '..', '..', 'conf', 'gc_config.ini'))
    print(db)
    dbsn = 'mysql+mysqlconnector://' + db['user'] + ':' + db['password'] + '@' + db['host'] + '/' + db['database']
    
    engine = sqlalchemy.create_engine(dbsn)

    engine.echo = True
#    metadata = BoundMetaData(engine)
    
    session = create_session()
      
    Base.metadata.bind = engine 
    
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()
 
    print(session.query(AbeGroupGc).all())
    
    sys.exit(0)