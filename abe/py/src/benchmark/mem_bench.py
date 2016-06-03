import resource
import time

if __name__ == "__main__":
    import sys, os    
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from benchmark.stoppable_thread import StoppableThread

from crypto.rouselakis.ucpabe_rw12 import CPABE_RW12
from charm.toolbox.pairinggroup import *

class MemBench(StoppableThread):
    def __init__(self, target_lib_call, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        super(MemBench, self).__init__()
        self.target_function = target_lib_call
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4
        self.arg5 = arg5
        self.results = None

    def startup(self):
        # Overload the startup function
        #print ("Calling the Target Library Function...")
        pass

    def cleanup(self):
        # Overload the cleanup function
        #print ("Library Call Complete")
        pass

    def mainloop(self):
        # Start the library Call
        if self.arg5 is not None:
            self.results = self.target_function(self.arg1, self.arg2, self.arg3, self.arg4, self.arg5)
        elif self.arg4 is not None:
            self.results = self.target_function(self.arg1, self.arg2, self.arg3, self.arg4)
        elif self.arg3 is not None:
            self.results = self.target_function(self.arg1, self.arg2, self.arg3)
        elif self.arg2 is not None:
            self.results = self.target_function(self.arg1, self.arg2)
        elif self.arg1 is not None:
            self.results = self.target_function(self.arg1)
        else:
            self.results = self.target_function()

        # Kill the thread when complete
        self.stop()

def callSetup():
    curve = 'MNT224'
    groupObj = PairingGroup(curve)
    scheme = CPABE_RW12(groupObj)
    print("Setup(",curve,")", end="")
    (pp, mk) = scheme.setup()

    return (scheme, pp, mk)

def callKeyGen(scheme, pp, mk, max):
    return scheme.keygen(pp,mk,p_attr(max))
    
def p_attr(max):
    ret = []
    for i in range (0, max):
         ret.append(str(i))
    return ret

def p_and(max, i = 0):
    if i > max: return "attr" + str(i)
    else: return "attr" + str(i) + " and " + p_and(max, i+1)

def p_or(max, i = 0):
    if i > max: return "attr" + str(i)
    else: return "attr" + str(i) + " or " + p_or(max, i+1)

def p_complex(max, i = 0):
    if i > max: return "attr" + str(i)
    else: return "(attr" + str(i) + " and (attr"  + str(i+1) + " or attr" + str(i+2) + ")) and " + p_complex(max, i+3)
           
def handleCall(myThread):           
    myThread.start()

    start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    delta_mem = 0
    max_memory = 0
    memory_usage_refresh = .005 # Seconds

    while(1):
        time.sleep(memory_usage_refresh)
        delta_mem = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) - start_mem
        if delta_mem > max_memory:
            max_memory = delta_mem

        # Uncomment this line to see the memory usuage during run-time 
        #print ("Memory Usage During Call: %d MB" % (delta_mem / 1000000.0))

        # Check to see if the library call is complete
        if myThread.isShutdown():
            #print ("done")
            #print( myThread.results)
            break;

    print( "MAX Memory Usage |" + str(max_memory) + "|KB, in |" + str(round(max_memory / 1024.0, 3)) + "|MB") 
    
if __name__ == "__main__":
    print ("setup: ", end="")
    myThread = MemBench(callSetup)
    handleCall(myThread)
    (scheme, pp,mk) = myThread.results

    
    for i in [10,100,500,1000]:
        print ("callkeygen " + str(i) + ": ", end="")
        handleCall(MemBench(callKeyGen, scheme, pp, mk, i))

    print ('--time--')
    t0 = time.clock()
    (scheme, pp,mk) = callSetup()
    print("Setup-time: |" + str(time.clock() - t0) + "|")
    
    for i in [10,100,500,1000]:
        print ("keygen " + str(i) + ": ", end="")
        t0 = time.clock()
        callKeyGen(scheme, pp, mk, i)
        print("-time: |" + str(time.clock() - t0) + "|")
        