'''
Created on 12.06.2015

@author: al
'''
import sys
import os, sqlalchemy
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy import func,select
from model.db.sqlalchemy_declarative.gc import Base,AbeGroupGm,AbeGroupGc,AbeAttribute
from sqlalchemy.ext.declarative import DeclarativeMeta

class DataAccess(object):
    '''
    classdocs
    Keyword arguments:    
    '''
        
    __session = None
    """DBSession"""
    __debug = 0
    """int """
    sqlAlchemyModel = None
    """Base"""

    def __init__(self):
        global DEBUG
        try:                               
            self.__debug = DEBUG
        except:
            pass
    
    def getSession(self):
        if self.__session is None:
            raise Exception("no dbSession is set!")
        return self.__session
            
    def setSession(self, dbSession):
        if isinstance(dbSession, Session):
            self.__session = dbSession
        else:
            raise Exception("session not set")

    def setSQLAlchemyModel(self, sqlAlchemyModel):
        if isinstance(sqlAlchemyModel, DeclarativeMeta):
            self.sqlAlchemyModel = sqlAlchemyModel
        else:
            raise Exception("not a base model")
           

    #groupCfg.getConfig('mysql')
    def connect(self, db):
        if self.__session is not None:
            return
        
        dbsn = 'mysql+mysqlconnector://' + db['user'] + ':' + db['password'] + '@' + db['host'] + '/' + db['database']
        engine = sqlalchemy.create_engine(dbsn)
        
        if self.__debug & 2:
            engine.echo = True  
                                
        Base.metadata.bind = engine

        DBSession = sessionmaker()
        DBSession.bind = engine
        self.__session = DBSession()
        return self

    def __assertEmptySQLAlchemyModel(self):
        if not(isinstance(self.sqlAlchemyModel, Base)):
            raise Exception('model is not set')

    #@Output(BOOLEAN)
    def isExists(self, colId, colName = 'id'):
        if not hasattr(self.sqlAlchemyModel, colName):
            raise Exception('model has no key: ' + colName)

        nr = self.__session.query(func.count(self.sqlAlchemyModel.id)).filter(getattr(self.sqlAlchemyModel, colName) == colId).scalar()
        return (nr > 0)

    #@list
    def getAll(self):
        return self.__session.query(self.sqlAlchemyModel).all()
    
    #@list
    def get(self, colVal, colName = 'id'):
        '''
        get's the matching items to the given sqlAlchemyModel and returns it as a list
        return list
        '''
        if not hasattr(self.sqlAlchemyModel, colName):
            raise Exception('model has no key: ' + colName)
        
        return self.__session.query(self.sqlAlchemyModel).filter(getattr(self.sqlAlchemyModel, colName) == colVal).all()
                
    def row2dict(self, row):
        #d = lambda row: {c.name: str(getattr(row, c.name)) for c in row.__table__.columns}
        return dict((col, str(getattr(row, col))) for col in row.__table__.columns.keys())

    def row2str(self, row, glue="\n", filter = []):
        if (len(filter) > 0):
            return glue.join(
                list((col + ": " + str(getattr(row, col))) for col in row.__table__.columns.keys() if col not in filter)
                            )
        else:
            return glue.join(list((col + ": " + str(getattr(row, col))) for col in row.__table__.columns.keys()))
        
    def updateGM(self, newGM):
        """ 
        set's at least the sk to the GM
        """
        if newGM.dek is None \
        or newGM.sk is None \
        or newGM.gc_id < 0:
            print("GM is not correct, missing gm_key or gc_id < 1", newGM)
            raise Exception("GM is not correct, missing gm_key sk or gc_id < 1")        
        self.__session.add(newGM)
        self.__session.commit()
        
    #@AbeAttribute
    def addGMwithNoSK(self, newGM):
        """ 
        adds a new AbeGroupGm to the group-controller
        the GM is not init, gm_key and sk must be set additionally!!
        GM.gm_key, GM.sk, must be set
        adds a gm to the abe - group. asserts if the gm_key or sk are empty
        return AbeAttribute
        """        
        if newGM.dek is None \
        or newGM.gc_id < 0:
#        or newGm.sn_abe_type is None \
#        or newGm.sn_abe_curve is None\
#        or newGm.sn_pk is None:
            print("GM is not correct, missing gm_key or gc_id < 1", newGM)
            raise Exception("GM is not correct, missing gm_key sk or gc_id < 1")
        
        self.__session.add(newGM)
        self.__session.commit()
        newGM.gm_key = str(newGM.id)
        self.__session.add(newGM)
        
        newAttr = AbeAttribute(value=newGM.gm_key, gc_id=newGM.gc_id)
        newAttr.gms.append(newGM)
        self.__session.add(newAttr)
        self.__session.commit()
        
        return newAttr 
                
    def addGroup(self, AbeGroupGc):
        """ 
        adds a new abe-chat-group to the db. 
        """
        if AbeGroupGc.dek is None \
        or AbeGroupGc.abe_type is None \
        or AbeGroupGc.abe_curve is None \
        or AbeGroupGc.pk is None \
        or AbeGroupGc.mk is None:
            print ("AbeGroupGc is not correctly init", AbeGroupGc)
            raise Exception("AbeGroupGc is not correctly init")
        self.__session.add(AbeGroupGc)
        self.__session.commit()            
