import sys
import socket
import time
import pdb
from logHandler import logHandler

def fileSender():
    print('sender program starts...')#remove this
    logProc = logHandler()
    ##########################

    #Write your Code here
    logProc.startLogging("testSendLogFile.txt")
    PKTSIZE = 1400
    BODYSIZE = 1300
    windowStart = 0
    pktCnt = 0
    curSeq = 0
    ackSeq = 0
    ackDup = 0
    isEOF = 0
    tstart = 0
    isFirst = True
    meetEnd = False
    buffer = [b''.join([str(curSeq).encode(), b'\n',
                            b'0', b'\n',
                            str(len(dstFilename)).encode(), b'\n',
                            dstFilename.encode()]).ljust(PKTSIZE, b'\0')]


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 10080))

    file = open(srcFilename, 'rb')
    
    while True:
        if isEOF == 1 or pktCnt >= windowSize:
            tcur = time.time()
            if tcur - tstart >= 1:
                curSeq = windowStart
                pktCnt = 0
                isEOF = 0
                tstart = 0
                continue
            
            else:
                sock.settimeout(2-tcur+tstart)
                try:
                    ack, _ = sock.recvfrom(PKTSIZE)
                    ack = ack.split(b'\n', 1)
                    ackSeq = int(ack[0].decode())
                    ackEOF = int(ack[1].split(b'\n', 1)[0].decode())
                except:
                    curSeq = windowStart
                    pktCnt = 0
                    isEOF = 0
                    tstart = 0
                    continue
            
            logProc.writeAck(1, f'ack {ackSeq} eof {ackEOF}')
            
            if ackEOF == 1:
                break

            #set window start as ack
            if ackSeq >= windowStart:
                newAcked = ackSeq - windowStart + 1
                windowStart = ackSeq + 1
                pktCnt -= newAcked
                ackDup = 1
                
                for _ in range(newAcked):
                    buffer.pop(0)
                

            elif ackSeq == windowStart - 1:
                #pdb.set_trace()
                ackDup += 1
            
            #if ack is redundant, set current seq to ack + 1
            if ackDup >= 3:
                pktCnt = 0
                curSeq = windowStart
                ackDup = 0
                isEOF = 0
                tstart = 0
                continue

        else:
            #fill the buffer
            if not meetEnd and not isFirst and len(buffer) < windowSize:
                data = file.read(BODYSIZE)
                if len(data) < BODYSIZE:
                    logProc.writePkt(0, f'meet EOF')
                    isEOF = 1
                    meetEnd = True
                #build data
                data = b''.join([str(curSeq).encode(), b'\n',
                            str(isEOF).encode(), b'\n',
                            str(len(data)).encode(), b'\n',
                            data]).ljust(PKTSIZE, b'\0')

                buffer.append(data)
            else:
                isFirst = False
            
            if tstart == 0:
                tstart = time.time()

            #send the appropriate date in the buffer
            pkt = buffer[pktCnt]
            test = pkt.split(b'\n', 3)
            testSeq = int(test[0].decode())

            sock.sendto(pkt, (recvAddr, 10080))
            logProc.writePkt(0, f'pkt {testSeq} send {curSeq} index {pktCnt}')
            isEOF = int(pkt.split(b'\n', 2)[1].decode())
            pktCnt += 1
            curSeq += 1

    file.close()
    logProc.writeEnd(10.123)
    ##########################


if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name

    fileSender()
