import sys
from logHandler import logHandler

def fileReceiver():
    print('receiver program starts...')
    logProc = logHandler()
    
    throughput = 0.0
    
    #########################
    
    #Write your Code here
    logProc.startLogging("testRecvLogFile.txt")
    
    logProc.writePkt(0, "Use your log file Processor")
    logProc.writeAck(1, "Like this")
    logProc.writeEnd(throughput)
    #########################


if __name__=='__main__':
    fileReceiver()
