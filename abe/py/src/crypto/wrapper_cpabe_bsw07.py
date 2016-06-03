'''
Created on 15.06.2015

@author: al
'''
from pip._vendor.requests.compat import basestring
if __name__ == "__main__":
    import sys, os    
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    
from crypto.wrapper import Wrapper 
from charm.adapters.abenc_adapt_hybrid import HybridABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup,G1,ZR,pair #,G1,G2,GT
from charm.core.engine.util import objectToBytes,bytesToObject
from charm.core.math.pairing import hashPair as sha1

class WrapperCpabeBSW07(Wrapper):
    '''
    wrapper implementation class to call cp-ABE BSW07 with object-to-bytes keys
    '''
    curve = None 
    
    __debug = 4
    """int: debug"""
    
    groupObj = None
    """PairingGroup: groupObj"""
    cpabe = None
    """HybridABEnc: cpabe"""
    
    def __init__(self, curve):
        global DEBUG
        try:                               
            self.__debug = DEBUG
        except:
            pass
        
        self.curve = curve
        self.groupObj = PairingGroup(self.curve)
        cpabe = CPabe_BSW07(self.groupObj)
        self.cpabe = HybridABEnc(cpabe, self.groupObj)
            
    #@list(str, str)            
    def setup(self):
        (PK, MK) = self.cpabe.setup()
        
        serPK = objectToBytes(PK, self.groupObj)
        serMK = objectToBytes(MK, self.groupObj)
        
        return (serPK, serMK)

#    @Input(pk_t, sk_t, ct_t)
#    @Output(serPK, serMK)            
    def keygen(self, serPK, serMK, attributeList):
        if attributeList is None \
        or not(isinstance( attributeList, list)):
            raise Exception("attributeList must be set and a list!")

        PK = bytesToObject(serPK, self.groupObj)
        MK = bytesToObject(serMK, self.groupObj)
        
        SK = self.cpabe.keygen(PK, MK, attributeList)

        serSK = objectToBytes(SK, self.groupObj)
        
        return serSK

    def encrypt(self, serPK, M, accessStructure):
        PK = bytesToObject(serPK, self.groupObj)
        
        return self.cpabe.encrypt(PK, M, accessStructure)
        

    def decrypt(self, serPK, serSK, CT):
        PK = bytesToObject(serPK, self.groupObj)
        SK = bytesToObject(serSK, self.groupObj) 
        
        return self.cpabe.decrypt(PK, SK, CT)
    
    def getDEK(self):
        """selects a new DEK from G1"""        
        return sha1(self.groupObj.random(G1))
    
    def refresh(self, serPK, serMK):
        """
        return tupel: (serPK', serMK', conversionFactor)
        """
        PK = bytesToObject(serPK, self.groupObj)
        MK = bytesToObject(serMK, self.groupObj)
        
        newAlpha = self.groupObj.random(ZR)
        PK['e_gg_alpha'] = pair(PK['g'], PK['g2'] ** newAlpha)
        g2_newAlpha = PK['g2'] ** newAlpha
        conversionFactor = ((g2_newAlpha / MK['g2_alpha']) ** ~(MK['beta'])) 
        MK['g2_alpha'] =g2_newAlpha 
        
        newSerPK = objectToBytes(PK, self.groupObj)
        newSerMK = objectToBytes(MK, self.groupObj)
        
        return (newSerPK, newSerMK, conversionFactor)

    def refreshSK(self, serSK, conversionFactor):
        '''
        refreshes the SK by the conversion_factor
        return newSerSK
        '''
        #{ 'D':D, 'Dj':D_j, 'Djp':D_j_pr, 'S':S }
        
        SK = bytesToObject(serSK, self.groupObj) 
        SK['D'] = SK['D'] *  conversionFactor
        
        return objectToBytes(SK, self.groupObj)
        
    
if __name__ == "__main__":
    #-------- ABE - test
    attributes = ['ONE', 'TWO', 'THREE']
    attributes_1 = ['ONE', 'TWO', 'THREE', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
    message = b"plaintext message"
    access_policy = '((four or three) and (two or one))'
    
    W = WrapperCpabeBSW07('SS512')
    (serPK, serMK) = W.setup()
    
    serSK = W.keygen(serPK, serMK, attributes)
    CT = W.encrypt(serPK, message, access_policy)
    mdec = W.decrypt(serPK, serSK, CT)
        
    print (len(serSK), len(W.keygen(serPK, serMK, attributes_1)))    
    assert mdec == message, "Failed Decryption!!!"
    print("done: ABE")
    
    #-------- the ratchet - test
    (serPKr, serMKr, conversionFactor) = W.refresh(serPK, serMK)
    #refresh one more time :)
    print(conversionFactor)
    (serPKr, serMKr, conversionFactor) = W.refresh(serPK, serMK)
    print(conversionFactor)
    (serPKr, serMKr, conversionFactor) = W.refresh(serPK, serMK)
    print(conversionFactor)
    (serPKr, serMKr, conversionFactor) = W.refresh(serPK, serMK)
    print(conversionFactor)
    serSKr = W.refreshSK(serSK, conversionFactor)
    newCT = W.encrypt(serPKr, message, access_policy)
    print("ratchat applied and the message is encrypted by conversed SK")
    try:
        mdec = W.decrypt(serPK, serSK, newCT)
    except ValueError as e:
        print("good: got ValueError, when trying to decrypt with the old key: " + repr(e))
        
    newMdec = W.decrypt(serPKr, serSKr, newCT)
    assert mdec == message, "Failed Decryption!!!"
    print("done: ABE - ratchet")
    
    #--------
    DEK = W.getDEK()
    
    from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
    a = AuthenticatedCryptoAbstraction(DEK)
    CT_AES = a.encrypt(message)
    mdec = a.decrypt(CT_AES)
    assert mdec == message, "Failed Decryption!!!"
    print("done: AES")
    