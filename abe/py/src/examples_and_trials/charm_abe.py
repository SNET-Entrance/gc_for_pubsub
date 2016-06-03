#!/opt/local/bin/python3.4 -d

#from pprint import pprint as pp
import json

from charm.adapters.abenc_adapt_hybrid import HybridABEnc as HybridABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup #,GT

#from charm.schemes.pkenc.pkenc_cs98 import CS98
#from charm.toolbox.eccurve import prime192v1
#from charm.toolbox.ecgroup import ECGroup


groupObj = PairingGroup('SS512')

cpabe = CPabe_BSW07(groupObj)
hyb_abe = HybridABEnc(cpabe, groupObj)
access_policy = '((four or three) and (two or one))'
message = b"this is my text"

# G1, G2 bilinear groups, e_gg_alpha: generator
#pk = { 'g':g, 'g2':gp, 'h':h, 'f':f, 'e_gg_alpha':e_gg_alpha }
#mk = {'beta':beta, 'g2_alpha':gp ** alpha }
(pk, mk) = hyb_abe.setup()

print ("g: ", type(pk['g']), 'g in real', pk['g'], "\n\n")

#print(json.dumps(pk['g'], cls='pairingElement'))
print(json.dumps({'g' : 1}, cls='pairingElement'))

exit()
#print("pk => ",  pk, "\n")
#print ("\n\n",pk["g"], "\n", pk["g2"], "\n",pk["h"], "\n",pk["f"], "\n",pk["e_gg_alpha"], "\n" )
#print ("\n\n---\n")
print("mk => ", mk, "\n")

sk = hyb_abe.keygen(pk, mk, ['ONE', 'TWO', 'THREE'])
#print("sk => ", sk, "\n")

ct = hyb_abe.encrypt(pk, message, access_policy)
#print("ct => ", ct, "\n")

mdec = hyb_abe.decrypt(pk, sk, ct)
assert mdec == message, "Failed Decryption!!!"

print("Successful Decryption!!!", "\n")

print('end')

    
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
