import sys
from logHandler import logHandler

def fileSender():
    print('sender program starts...')#remove this
    logProc = logHandler()
    
    throughput = 0.0
    avgRTT = 10.0
    ##########################
    
    #Write your Code here
    logProc.startLogging("testSendLogFile.txt")
    
    logProc.writePkt(0, "Use your log file Processor")
    logProc.writeAck(1, "Like this")
    logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name

    fileSender()
