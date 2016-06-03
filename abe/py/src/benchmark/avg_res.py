#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
if __name__ == "__main__":    
	sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import resource
import time
import psutil
import pickle
from argparse import ArgumentParser

#from memory_profiler import memory_usage

from charm.toolbox.pairinggroup import *
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.schemes.abenc.abenc_lsw08 import KPabe
from charm.schemes.abenc.abenc_waters09 import CPabe09
from crypto.rouselakis.ucpabe_rw12 import CPABE_RW12
from crypto.rouselakis.ucpabe_ot12 import CPABE_OT12
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha1
from benchmark.mem_bench import MemBench 
from charm.core.engine.util import objectToBytes,bytesToObject
    

curves = [ 'SS512', 'MNT159', 'MNT201', 'MNT224']#not working on OSX, 'SS1024'
types = ['AESCBC', 'bsw07', 'lw08', 'waters09', 'ot12', 'rw12']
steps = [1, 10, 50, 100,500,1000]
dataPath = os.path.join(os.path.dirname(__file__), '../data')

if __name__ == "__main__":	
	try:        
		parser = ArgumentParser()
		parser.add_argument(dest="curve", choices=curves, help="{ 'SS512', 'MNT159' ('SS1024', 'MNT201', 'MNT224') }", nargs=1, metavar="curve")
		parser.add_argument(dest="type", choices=types, help="{ 'bsw07', 'lw08', 'waters09', 'rw12', 'ot12' }", nargs=1, metavar="type")
		parser.add_argument("-s", "--number-steps", help="if set only this septs will be exex, must be: 1,100,500,1000", nargs=1, type=int)
		
		args = parser.parse_args()	
		curve = args.curve[0]
		tp = args.type[0]		
		try:
			newSteps = args.number_steps[0]
		except:
			newSteps = None
			
		if newSteps is not None:
			if newSteps!=1:
				steps = [1, newSteps]
			else:
				steps = [1]
		
	except KeyboardInterrupt:
		### handle keyboard interrupt ###
		exit()
										
#formatting function for time
def ft(timeReal):
	if timeReal>0 and timeReal < 0.1:
		string = "{:10.6f}".format(timeReal)
	else:
		string = str(timeReal)
	ind = string.find(".")
	spcs = 5 - ind
	tmp = ""
	for i in range(spcs):
		tmp += " "
	string = tmp + string
	
	spcs = 13 - len(string)
	tmp = ""
	for i in range(spcs):
		tmp += " "
		
	return string + tmp

#number of iterations (BE CAREFUL WITH THIS!)
N = 1

def getAESCBC(groupObj):
	pp = sha1(groupObj.random(G1))
	mk = groupObj.random(G1)
	scheme = AuthenticatedCryptoAbstraction(pp)
	return (scheme, pp, mk)
	
def callSetup(groupObj, schemeName):
	#calling a new groupObj somehow destroys the benchmark module
	#groupObj = PairingGroup(curve)
	if schemeName == 'bsw07':
		scheme = CPabe_BSW07(groupObj)
	elif schemeName == 'lw08':
		scheme = KPabe(groupObj)
	elif schemeName == 'waters09':
		scheme = CPabe09(groupObj)
	elif schemeName == 'rw12':
		scheme = CPABE_RW12(groupObj)
	elif schemeName == 'ot12':
		scheme = CPABE_OT12(groupObj)
	elif schemeName == 'AESCBC':
		return getAESCBC(groupObj)
		
	print("Setup(",curve,",", schemeName, ") ", end="")
	if schemeName == 'waters09':#great implementation! :)
		(mk, pp) = scheme.setup()
	else:
		(pp, mk) = scheme.setup()

	return (scheme, pp, mk)


def callKeyGen(scheme, pp, mk, N, tp):
	if (tp=='lw08'):
		return scheme.keygen(pp,mk,p_complex(N))
	elif tp == 'AESCBC':
		return sha1(mk)
	else:
		return scheme.keygen(pp,mk,p_attr(N))

def callEnc(scheme, pp, m, N, tp):
	if (tp=='lw08'):
		return scheme.encrypt(pp,m,p_attr(N))
	elif tp == 'AESCBC':
		return scheme.encrypt(m)
	else:
		return scheme.encrypt(pp,m,p_complex(N))

def callDec(scheme, pp, sk, ct, tp):
	if (tp=='lw08'):
		return scheme.decrypt(ct, sk)
	elif tp == 'AESCBC':
		return scheme.decrypt(ct)
	else:
		return scheme.decrypt(pp, sk, ct)
		
def p_message(m, N):
	ret = b''				
	for i in range (1, N):
		ret += m
	return ret

def p_attr(N):
	ret = []
	for i in range (1, N+1):
		ret.append(str(i))
	return ret

def p_and(N, i = 1):
	if i >= N: return str(i)
	else: return str(i) + " and " + p_and(N, i+1)

def p_or(N, i = 1):
	if i >= N: return str(i)
	else: return str(i) + " or " + p_or(N, i+1)

def p_complex(N, i = 1):
	if i >= N-2: return str(i)
	else: return "(" + str(i) + " and ("  + str(i+1) + " or " + str(i+2) + ")) and " + p_complex(N, i+3)

def handleCall(myThread, turn=0):   
	turn = turn + 1        
	myThread.start()

	try:
		process = psutil.Process(os.getpid())
		start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
		psStartMem = process.memory_info()[0]	
	except:
		raise Exception('in handle-call')

	
	delta_mem = 0
	max_memory = 0
	
	psDelta = 0
	psMax = 0
	memory_usage_refresh = .001 # Seconds

	while(1):
		time.sleep(memory_usage_refresh)
		delta_mem = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) - start_mem
		if delta_mem > max_memory:
			max_memory = delta_mem
			
		psDelta = process.memory_info()[0] - psStartMem
		if psDelta > psMax:
			psMax = psDelta

		# Uncomment this line to see the memory usuage during run-time 
		#print ("Memory Usage During Call: %d MB" % (delta_mem / 1000000.0))

		# Check to see if the library call is complete
		if myThread.isShutdown():
			#print ("done")
			#print( myThread.results)
			break;

	print( "MAX Memory Usage |" + str(max_memory) + "|Byte, in |" + str(round(max_memory / 1000.0, 3)) + "|KB "
		+ str(psMax) + " Byte"
		)

	#return (max_memory, round(max_memory / 1024.0, 3));
	return (psMax, round(psMax / 1000.0, 3));

if __name__ == "__main__":	
	if os.path.isfile(dataPath + '/results.ser.txt'):
		with open(dataPath + '/results.ser.txt', 'rb') as f:
			results = pickle.load(f)
	else:
		results = { curve:{ tp:{} for tp in types } for curve in curves }
		
	#we do this, so new types can be added, without deleting all values
	for t in types:
		if t not in results[curve]:
			results[curve][t] = {}
		
	
	print ("doing type: " + tp + " in curve: " + curve)
	
	groupObj = PairingGroup(curve)	
	#benchmark is not working with AES :( + benchmark has some real dealoc probs!	
	#groupObj.InitBenchmark()
	m = groupObj.random(GT)		
	
	for i in steps:		
		k = 'm' + str(i)
		t = 't' + str(i)		
		results[curve][tp][k] = {}
		results[curve][tp][t] = {}	
		
		if i == 1:
			#we allocate a new one				
			print ("mem: setup: ", end="")
			myThread = MemBench(callSetup, groupObj, tp)						
			results[curve][tp][k]['stp'] = handleCall(myThread)[1]
			(scheme,pp,mk) =myThread.results	
					
			print ("time: setup: ", end="")				
			#groupObj.StartBenchmark(["RealTime"])
			time_start = time.clock()				
			if tp == 'waters09':#great implementation! :)
				(mk, pp) = scheme.setup()
			elif tp == 'AESCBC':
				getAESCBC(groupObj)
			else:
				(pp, mk) = scheme.setup()			
			#groupObj.EndBenchmark()
			#results[curve][tp][t]['stp'] = groupObj.GetBenchmark("RealTime")			
			results[curve][tp][t]['stp'] = time.clock() - time_start
			
			results[curve][tp][k]['pp'] = sys.getsizeof(objectToBytes(pp, groupObj))#sys.getsizeof(pp)
			results[curve][tp][k]['mk'] = sys.getsizeof(objectToBytes(mk, groupObj))
			
						
			print(results[curve][tp][t]['stp'])	
		else:
			results[curve][tp][k]['pp'] = results[curve][tp]['m1']['pp']
			results[curve][tp][k]['mk'] = results[curve][tp]['m1']['mk']			
			results[curve][tp][k]['stp'] = results[curve][tp]['m1']['stp']
			results[curve][tp][t]['stp'] = results[curve][tp]['t1']['stp']

		attr = p_attr(i)			
		policy = p_complex(i)					
		print ("mem: callkeygen " + str(i) + ": ", end="")
		results[curve][tp][k]['kgn'] = handleCall(MemBench(callKeyGen, scheme, pp, mk, i, tp))[1]

		print ("time: callkeygen " + str(i) + ": ", end="")
		#benchmark is not working with AES :(
		#groupObj.StartBenchmark(["RealTime"])
		time_start = time.clock()					
		sk = callKeyGen(scheme, pp, mk, i, tp)
		#groupObj.EndBenchmark()
		#results[curve][tp][t]['kgn'] = groupObj.GetBenchmark("RealTime")
		results[curve][tp][t]['kgn'] = time.clock() - time_start				
		results[curve][tp][k]['sk'] = sys.getsizeof(objectToBytes(sk, groupObj))
		
		print(results[curve][tp][t]['kgn'])
		
		if tp == 'AESCBC':
			mm = p_message(objectToBytes(m, groupObj), i) #creating a long message
		else:
			mm = m
				
		print ("mem: callEnc " + str(i) + ": ", end="")		
		results[curve][tp][k]['enc'] = handleCall(MemBench(callEnc, scheme, pp, mm, i, tp))[1]

		print ("time: callEnc " + str(i) + ": ", end="")			
		#groupObj.StartBenchmark(["RealTime"])
		time_start = time.clock()		
		ct = callEnc(scheme, pp, mm, i, tp)
		#groupObj.EndBenchmark()
		#results[curve][tp][t]['enc'] = groupObj.GetBenchmark("RealTime")
		results[curve][tp][t]['enc'] = time.clock() - time_start		
		results[curve][tp][k]['ct'] = sys.getsizeof(objectToBytes(ct, groupObj))		
		print(results[curve][tp][t]['enc'])
					
		print ("mem: callDec " + str(i) + ": ", end="")
		myThread = MemBench(callDec, scheme, pp, sk, ct, tp)
		results[curve][tp][k]['dec'] = handleCall(myThread)[1]
		res = myThread.results
		
		if res != mm:
			print('Unsuccessful Decryption', res, m)
		
		print ("time: callDec " + str(i) + ": ", end="")
		#groupObj.StartBenchmark(["RealTime"])		
		time_start = time.clock()		
		res = callDec(scheme, pp, sk, ct, tp)
		#groupObj.EndBenchmark()
		#results[curve][tp][t]['dec'] = groupObj.GetBenchmark("RealTime")
		results[curve][tp][t]['dec'] = time.clock() - time_start
		print(results[curve][tp][t]['dec'])
		if res != mm:
			print('Unsuccessful Decryption', res, m)
		print('done: ' + str(i))		
	
	print('done: ' + curve)	
	print(" ")
	#print(results)
				
	for curve in curves:
		if curve not in results:
			results[curve] = { tp:{} for tp in types }	
		for tp in types:
			if tp not in results[curve]:
				results[curve][tp] = {}

			for i in steps:				
				k = 'm' + str(i)				
								
				if k in results[curve][tp]:
					print(k + ": ", tp, 
						' Setup: ', ft(results[curve][tp][k]['stp']), 
						' Keygen: ', ft(results[curve][tp][k]['kgn']), 
						' Encrypt: ', ft(results[curve][tp][k]['enc']), 
						' Decrypt: ', ft(results[curve][tp][k]['dec']),
						' pp: ', ft(results[curve][tp][k]['pp']),
						' mk: ', ft(results[curve][tp][k]['mk']),
						' sk: ', ft(results[curve][tp][k]['sk']),
						' ct: ', ft(results[curve][tp][k]['ct']), 
					)
					t = 't' + str(i)	
					print(t + ": ", tp, ' Setup: ', ft(results[curve][tp][t]['stp']), ' Keygen: ', ft(results[curve][tp][t]['kgn']), ' Encrypt: ', ft(results[curve][tp][t]['enc']), ' Decrypt: ', ft(results[curve][tp][t]['dec']) )		
				else:
					print("missing key: ", curve, tp, k)
	with open(dataPath + '/results.ser.txt', 'wb') as f:
		pickle.dump(results, f)
	
	print("results updated")