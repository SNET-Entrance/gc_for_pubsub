#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Yamda, Attrapadung, Hanaoka, Kunihiro

| From: "A Framework and Compact Constructions for Non-monotonic Attribute-Based Encryption"
| Published in:  Public-Key Cryptography--PKC 2014
| Pages: 275--292
| Available from:  
| Notes: 

* type:          attribute-based encryption (public key)
* setting:       bilinear pairing group of prime order
* assumption:    complex q-type assumption

:Authors:        al
:Date:          07/15
'''
if __name__ == "__main__":
    import sys, os    
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))


from charm.core.math.integer import * #InitBenchmark,StartBenchmark,EndBenchmark,GetBenchmark,GetGeneralBenchmarks,ClearBenchmark
from charm.toolbox.pairinggroup import *
from charm.core.crypto.cryptobase import *
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import *
#from crypto.rouselakis.BenchmarkFunctions import *


debug = False
class CPABE_YAHK14(ABEnc):
    def __init__(self, groupObj, verbose = False):
        ABEnc.__init__(self)
        global util, group
        group = groupObj
        util = SecretUtil(group, verbose)

    # Defining a function to pick explicit exponents in the group
    def exp(self,value):    
        return group.init(ZR, value)
        
    def setup(self):
        g = group.random(G2)
        g2, u, h, w, v = group.random(G1), group.random(G1), group.random(G1), group.random(G1), group.random(G1)
        alpha, beta = group.random( ), group.random( )#from ZR
        vDot = u ** beta
        egg = pair(g2,g)**alpha
        #print(pair(g2,g), egg, "\n", g)
        #exit()
        pp = {'g':g, 'g2':g2, 'u':u, 'h':h, 'w':w, 'v':v, 'vDot':vDot,'egg':egg}
        mk = {'g2_alpha':g2 ** alpha, 'beta': beta }
        return (pp, mk)
        
    def keygen(self, pp, mk, S):
        # S is a list of attributes written as STRINGS i.e. {'1', '2', '3',...}
        r = group.random( )
        
        D1 = mk['g2_alpha'] * (pp['w']**r)
        D2 = pp['g']**r
         
        vR = pp['v']**(-1*r)
        
        K0, K0Dot, K1, K1Dot = {}, {}, {}, {}
        for i in S:
            ri = group.random( )
            riDot = group.random( )
            omega_i = self.exp(int(i)) #NOTICE THE CONVERSION FROM STRING TO INT
            K0[i] = vR * (pp['u']**omega_i  * pp['h'])**ri  
            K0Dot[i] = (pp['u']**(omega_i * mk['beta']) * pp['h']**mk['beta'])**riDot
            
            K1[i] = pp['g']**ri
            K1Dot[i] = pp['g']**(mk['beta']*riDot)            
        S = [s for s in S] #Have to be an array for util.prune
        
        return { 'S':S, 'D1': D1, 'D2' : D2, 'K0':K0, 'K0Dot':K0Dot, 'K1':K1, 'K1Dot':K1Dot }

    def encrypt(self, pp, message, policy_str):
        s = group.random()    

        policy = util.createPolicy(policy_str)
        a_list = util.getAttributeList(policy)
        #print("\n\n THE A-LIST IS", a_list,"\n\n")
        shares = util.calculateSharesDict(s, policy) #These are correctly set to be exponents in Z_p
        
        C0 = message * (pp['egg']**s)
        C1 = pp['g']**s
        
        C_1, C_2, C_3 = {}, {}, {}
        for i in a_list:
            #inti = int(util.strip_index(i)) #NOTICE THE CONVERSION FROM STRING TO INT
            ti = group.random()            
            if i[0] == '!': 
                inti = int(util.strip_index(i[1:])) #2CHCK
                C_1[i] = pp['w']**shares[i] * pp['vDot']**ti                                  
            else: 
                inti = int(util.strip_index(i))
                C_1[i] = pp['w']**shares[i] * pp['v']**ti    
                            
            C_2[i] = (pp['u']**self.exp(inti) * pp['h'])**(-1*ti)
            C_3[i] = pp['g']**ti
            
            #print('The exponent is ',inti)
                        
        return { 'Policy':policy_str, 'C0':C0, 'C1':C1, 'C_1':C1, 'C_2':C_2, 'C_3':C_3 } 
    
    def decrypt(self, pp, sk, ct):
        policy = util.createPolicy(ct['Policy'])
        z = util.getCoefficients(policy)
        #print("\n\n THE COEFF-LIST IS", z,"\n\n")
        
        pruned_list = util.prune(policy, sk['S'])
        # print("\n\n THE PRUNED-LIST IS", pruned_list,"\n\n")

        if (pruned_list == False):
            return group.init(GT,1)
        
        B = group.init(GT,1)
        for i in range(len(pruned_list)):
            x = pruned_list[i].getAttribute( ) #without the underscore
            y = pruned_list[i].getAttributeAndIndex( ) #with the underscore
            #print(x,y)
            B *= ( pair( ct['C1'][y], sk['K1']) * pair( ct['C2'][y], sk['K2'][x]) / pair(sk['K3'][x], ct['C3'][y]) )**z[y]
            
        return ct['C'] * B / pair(sk['K0'] , ct['C0'])    
        
    def randomMessage(self):
        return group.random(GT)            
            
def main():
    curve = 'MNT224'

    groupObj = PairingGroup(curve)
    scheme = CPABE_YAHK14(groupObj)
    print("Setup(",curve,")")    
    
    groupObj.InitBenchmark()
    
#    startAll(groupObj)
    #startAll(groupObj)
    #groupObj.StartBenchmark(["CpuTime", "RealTime", "Add", "Sub", "Mul", "Exp", "Pair", "Granular"])
    
    (pp, mk) = scheme.setup()
    groupObj.EndBenchmark()
    
    print(groupObj.GetGeneralBenchmarks(), groupObj.GetGranularBenchmarks())
    #print(pp, mk)
    
    s=group.random()
    #policy_str = '(1 and 3) or (2 and (!1 or 3))'
    policy_str = '2 and !1'
    S = {'2'}
    
    pparsed = util.createPolicy(policy_str)
    pruned_list = util.prune(pparsed, S)
    
    print(util.getAttributeList(pparsed), pparsed, pruned_list)
    if (pruned_list == False): 
        print(pruned_list)
        exit()
        
    for i in range(len(pruned_list)):
        x = pruned_list[i].getAttribute( ) #without the underscore
        y = pruned_list[i].getAttributeAndIndex( ) #with the underscore
        print(x, y)
    
    exit()
    a_list = util.getAttributeList(pparsed)
    for i in a_list:
        if i[0] == '!': 
            print(i, end='')
            idx = util.strip_index(i[1:]) 
        else: 
            print ("yo", end='')
            idx = util.strip_index(i)
        print (" sfsdf ", end='')
        print(idx)
    print(pparsed, a_list, util.calculateSharesDict(s, pparsed), util.getCoefficients(pparsed))
    exit()

#    print("The Public Parameters are",pp)
#    print("And the Master Key is",mk)
    print("Done!\n")    
    box1 = getResAndClear(groupObj, "Setup("+curve+")", "Done!")
    
    #--------------------------------------------    
        
    S = {'123', '842',  '231', '384'}
    #print("Keygen(", str(S),")")

    groupObj.InitBenchmark()
    startAll(groupObj)
    sk = scheme.keygen(pp,mk,S)
    groupObj.EndBenchmark()
    
    #print("The secret key is",sk)
    #print("Done!\n")    
    box2 = getResAndClear(groupObj, "Keygen(" + str(S) + ")", "Done!")
    #--------------------------------------------    
            
    m = group.random(GT)
    policy = '(123 or 444) and (231 or 999)'
    print("Encrypt(",policy,")")

    groupObj.InitBenchmark()
    startAll(groupObj)
    ct = scheme.encrypt(pp,m,policy)
    groupObj.EndBenchmark()

    #print("The ciphertext is",ct)
    #print("Done!\n")    
    box3 = getResAndClear(groupObj, "Encrypt("+policy+")", "Done!")
    
    #--------------------------------------------    
                
    print("Decrypt")
    
    groupObj.InitBenchmark()
    startAll(groupObj)
    res = scheme.decrypt(pp, sk, ct)
    groupObj.EndBenchmark()

    #print("The resulting ciphertext is",res)
    if res == m:
        fin = "Successful Decryption :)"
    else:
        fin = "Failed Decryption :("
    box4 = getResAndClear(groupObj, "Decrypt", fin)
    
    #print(formatNice(box1,box2,box3,box4))

if __name__ == '__main__':
    debug = True
    main()
