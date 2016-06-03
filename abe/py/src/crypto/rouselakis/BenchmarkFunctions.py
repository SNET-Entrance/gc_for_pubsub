'''
Class to print in a good looking box the benchmark results
'''
from charm.core.math.integer import * #InitBenchmark,StartBenchmark,EndBenchmark,GetBenchmark,GetGeneralBenchmarks,ClearBenchmark
from charm.toolbox.pairinggroup import *
#from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

	

def startAll(groupObj):
	groupObj.StartBenchmark(["CpuTime", "RealTime", "Add", "Sub", "Mul", "Div", "Exp", "NativeTime", "Pair", "Granular"])#
						#RealTime, CpuTime, Mul, Div, Add, Sub, Exp, Pair, Granular
	#StartBenchmark(ID, [CpuTime, RealTime, Add, Sub, Mul, Div, Exp])#NativeTime, Pair, Granular
	#ID.StartBenchmark([CpuTime, RealTime, Add, Sub, Mul, Div, Exp, 'Granular'])#NativeTime, Pair
	#ID.StartBenchmark(["CpuTime", "RealTime", "Add", "Sub", "Mul", "Exp", "Pair", "Granular"]) 
	#ID.StartBenchmark([CpuTime, RealTime, Add, Sub, Mul, Div, Exp, 'Granular'])#NativeTime, Pair
	
def getResAndClear(groupObj, header, footer):
	box = getRes(groupObj, header, footer)
	#ClearBenchmark(ID)
	return box

def getRes(groupObj, header, footer):
	res = ""
	
	#result1 = GetGeneralBenchmarks(ID)
	result1 = groupObj.GetGeneralBenchmarks()
	#result2 = GetGranularBenchmarks(ID)
	result2 = groupObj.GetGranularBenchmarks()
	["RealTime", "CpuTime", "Mul", "Div", "Add", "Sub", "Exp", "Pair", "Granular"]
	#result2 = groupObj.GetBenchmark("Granular")

	print (result1, result2, result2[Exp][ZR])
	return
	#result1 = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0}

	res += "\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510\n"
	
	#PRINTING THE HEADER
	res += "\u2502" + header[0:min(len(header),27)]
	for i in range(0, 29 - min(len(header),27)):
		res += " "
	res += "\u2502\n"
	
	#res += "\u2502 CpuTime:    " + ft(result1[CpuTime]*1000) + " ms          \u2502\n"
	#res += "\u2502 RealTime:   " + ft(result1[RealTime]*1000) + " ms          \u2502\n"
	#res += "\u2502 NativeTime: " + ft(result1[NativeTime]*1000)+" ms          \u2502\n"
	#res += "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524\n"
	#res += "\u2502                                       \u2502\n"
	res += "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524\n"
	res += "\u2502" + f("") + f("Gop") +  f("Exp") +  f("Rest") + "         \u2502\n"
	#res += "\u2502" + f("Tot: ") +  f(result1[Add] + result1[Sub]) +  f(result1[Mul] + result1[Div]) +  f(result1[Exp]) + "         \u2502\n"
	#res += "\u2502                             \u2502\n"
	res += "\u2502" + f("ZR:  ") +  f(result2[Add][ZR] + result2[Sub][ZR]) +  f(result2[Mul][ZR] + result2[Div][ZR]) +  f(result2[Exp][ZR]) + "         \u2502\n"
	res += "\u2502" + f("G1:  ") +  f(result2[Mul][G1] + result2[Div][G1]) +  f(result2[Exp][G1]) + f(result2[Add][G1] + result2[Sub][G1]) +"         \u2502\n"
	res += "\u2502" + f("G2:  ") +  f(result2[Mul][G2] + result2[Div][G2]) +  f(result2[Exp][G2]) + f(result2[Add][G2] + result2[Sub][G2]) +"         \u2502\n"
	res += "\u2502" + f("GT:  ") +  f(result2[Mul][GT] + result2[Div][GT]) +  f(result2[Exp][GT]) + f(result2[Add][GT] + result2[Sub][GT]) +"         \u2502\n"
	res += "\u2502 Pairings: " + f(result1[Pair]) + "             \u2502\n"
	#PRINTING THE FOOTER
	res += "\u2502" + footer
	for i in range(0, 29 - len(footer)):
		res += " "
	res += "\u2502\n"
	
	res += "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n"
	
	return res

#formatting functions
def f(inp):
	if (type(inp) != str):
		string = str(inp)
	else:
		string = inp
	spcs = 5 - len(string)
	tmp = ""
	for i in range(spcs):
		tmp += " "
	return tmp + string
	
def ft(timeReal):
	string = str(timeReal)
	ind = string.find(".")
	spcs = 8 - ind
	tmp = ""
	for i in range(spcs):
		tmp += " "
	string = tmp + string
	
	spcs = 13 - len(string)
	tmp = ""
	for i in range(spcs):
		tmp += " "
		
	return string + tmp
	
def formatNice(box1, box2, box3, box4):
	numLines = box1.count("\n")
	
	hugeStr = ""
	start = 0
	for i in range(0,numLines):
		ind = box1.find("\n",start)
		hugeStr += box1[start:ind]
		hugeStr += box2[start:ind]
		hugeStr += box3[start:ind]
		hugeStr += box4[start:ind]
		hugeStr += "\n"
		start = ind + 1
		
	return hugeStr
