'''
Created on 12.06.2015

@author: al
'''
from configparser import ConfigParser
import os,string

class Config(object):
    '''
    classdocs
    '''
    __cfg = {}

    def __init__(self, fName='../../conf/config.ini'):
        if not(os.path.isfile(fName)):
            fName = os.path.join(os.path.dirname(__file__), fName)   
        parser = ConfigParser()   
        parser.read(fName)
        
        for s in  parser.sections():
            items = parser.items(s)
            for i in items:
                if not(s in self.__cfg):
                    self.__cfg[s] = {}                    
                self.__cfg[s][i[0]] = i[1]
    
    def getConfig(self, key=None):
        if key is not None:
            if key not in self.__cfg:
                raise Exception("key not found in config! " + key + " " + ','.join(self.__cfg.keys()))            
            return self.__cfg[key]
        return self.__cfg
        
if __name__ == '__main__':
    cfg = Config('../conf/gm_config.ini')
    print(cfg.getConfig(), cfg.getConfig('mysql'))        