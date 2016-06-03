'''
Created on 15.06.2015

@author: al
'''
#from charm.toolbox.schemebase import object

class Wrapper():
    cpabe = None
    """ABEnc: the charm cp-ABE object"""
     
    def setup(self):
        raise NotImplementedError

    def keygen(self, serPK, serMK, object):
        raise NotImplementedError

    def encrypt(self, serPK, M, object):
        raise NotImplementedError

    def decrypt(self, serPK, serSK, CT):
        raise NotImplementedError
    
    def getDEC(self):
        raise NotImplementedError    
    
    def refresh(self, serPK, serMK):
        raise NotImplementedError   
    
    def refreshSK(self, serSK, conversionFactor):
        raise NotImplementedError