'''
Created on 15.06.2015

@author: al
'''

class CharmAbe():
    '''
    this class is used to delegate the abe operations to Charm ABE implementations
    the Charm ABE implementations are "wrapped" to abe_mqtt, because the
    abe_mqtt core is i.e. only dealing with byte-objects for PK, MK, SK
    '''
    __abeWrapper = None
    """Wrapper: current ABE type"""
    __debug = 4
    """int: debug"""
    abeTypes = ('CPabe_BSW07',)
    """tupel: of suported types """
    curveTypes = ('SS512', 'MNT224')

    def __init__(self):
        global DEBUG
        try:
            self.__debug = DEBUG
        except:
            pass

    def setAbeCurveAndType(self, curve, abeType):
        """
    	returns (serPK, serMK)
    	"""
        if not(curve in self.curveTypes):
            raise Exception("curve not known: " + curve  + " allowed curves: " + ", ".join(self.curveTypes))

        if not(abeType in self.abeTypes):
            raise Exception("abeType not known: " + abeType + " allowed types: " + ", ".join(self.abeTypes))

        if abeType == "CPabe_BSW07":
            from crypto.wrapper_cpabe_bsw07 import WrapperCpabeBSW07
            self.__abeWrapper = WrapperCpabeBSW07(curve)


    def setup(self):
        '''
        calls setup on the actual scheme and returns pk and mk in ObjectBytes
        '''
        if self.__abeWrapper is None:
            raise Exception("you must set the abeType")

        return self.__abeWrapper.setup()

    def keygen(self, pk, mk, object):
        '''
        calls keygen on the actual scheme and returns sk in ObjectBytes
        '''
        if self.__abeWrapper is None:
            raise Exception("you must set the abeType")

        return self.__abeWrapper.keygen(pk, mk, object)

    def encrypt(self, pk, M, object):
        '''
        calls encrypt on the actual scheme and returns CT
        '''

        raise self.__abeWrapper.encrypt(pk, M, object)

    def decrypt(self, pk, sk, ct):
        '''
        calls decrypt on the actual scheme and returns M
        '''

        raise self.__abeWrapper.decrypt(pk, sk, ct)

    def getDEK(self):
        """selects a new DEK from G1"""
        return self.__abeWrapper.getDEK()

    def refresh(self, serPK, serMK):
        """
        alters mk, pk and 
        return (newSerPK, newSerMK, conversion_factor)
        """
        return self.__abeWrapper.refresh(serPK, serMK)
    
    def refreshSK(self, serSK, conversionFactor):
        """
        alters SK
        return: newSK
        """
        return self.__abeWrapper.refreshSK(serSK, conversionFactor)
