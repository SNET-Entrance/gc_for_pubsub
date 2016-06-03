#!/opt/local/bin/python3.4

import json;
from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.adapters.abenc_adapt_hybrid import HybridABEnc as HybridABEnc
from charm.core.engine.util import objectToBytes,bytesToObject

bla = {'u1': [3298552771336315058475964122560955936669014483448543089394, 2492329322382145273721764477046581872194066564018674282002], 'u2': [4386798087328702967628570037820998863857227354892500890225, 2643854894262774539282328524705550500360174676349510382374], 'v': [513927001364049699498717302480791263811303229590715045334, 4123403705144654743269887658478304341858296884697172214022], 'e': [3849146896870141713909280592696755725700337296330388339822, 3315575432157417383040094888351986415172274265058848014909]}

print(bla, "\n\n\n")

print(json.dumps(bla), "\n\n\n", bla['u1'], "\n\n\n")

print(bla['u1'])
#exit()

################
groupObj = PairingGroup('SS512')

cpabe = CPabe_BSW07(groupObj)
hyb_abe = HybridABEnc(cpabe, groupObj)

(pk, mk) = hyb_abe.setup()
print ("-----", pk['f'], "-----")
serPK = objectToBytes(pk, groupObj)
groupObj2 = PairingGroup('SS512')
unserPK = bytesToObject(serPK, groupObj2)
print(pk, "\n\n\n", unserPK)
exit()

class MyObj(object):
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return '<MyObj(%s)>' % self.s

class MyEncoder(json.JSONEncoder):    
    def default(self, obj):
        #print ('default(', repr(obj), ')')
        # Convert objects to a dictionary of their representation
        d = { '__class__':obj.__class__.__name__, 
              #'__module__':obj.__module__,
              }
        #d.update(obj.__dict__)
        return d

obj = MyObj('internal data')
print (obj)
print (MyEncoder().encode(pk),MyEncoder().encode(mk))


###############

class pairingElement(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pairingElement):
#            for i in obj:
#                print(i)            
            obj = "pairingElement"
        else:
            obj = super(pairingElement, self).default(obj)
        #print (obj)
        return obj
