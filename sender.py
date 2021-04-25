import sys
import socket
import time
from logHandler import logHandler

def fileSender():
    print('sender program starts...')#remove this
    logProc = logHandler()
    ##########################

    #Write your Code here
    logProc.startLogging(f'{srcFilename}_sending_log.txt')
    PKTSIZE = 1400
    MAXBODYSIZE = 1300
    windowStart = 0
    pktCnt = 0
    curSeq = 0
    ackSeq = 0
    ackDup = 0
    ackNum = 0 #number of all acks
    
    #time variables
    torigin = time.time()
    tstart = 0
    rttsum = 0

    #flags
    isEOF = 0
    isRetrans = False
    isFirst = True
    meetEnd = False

    buffer = [b''.join([str(curSeq).encode(), b'\n',
                            b'0', b'\n',
                            str(len(dstFilename)).encode(), b'\n',
                            str(time.time()).encode(), b'\n',
                            dstFilename.encode()]).ljust(PKTSIZE, b'\0')]


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 10080))

    file = open(srcFilename, 'rb')
    
    while True:
        if isEOF == 1 or pktCnt >= windowSize:
            #getting ack only if retransmission ended
            isRetrans = False

            #check the time and handle timeout
            tcur = time.time()

            if ackNum > 0:
                avgrtt = rttsum / float(ackNum)
            else:
                avgrtt = 1.0
            if avgrtt < 0.1:
                avgrtt = 0.1
            
            if tcur - tstart >= avgrtt:
                logProc.writePkt(curSeq, f'timeout since {tstart-torigin:.3f}(timeout value {avgrtt:.3f})')
                curSeq = windowStart
                pktCnt = 0
                isEOF = 0
                tstart = time.time()
                isRetrans = True
                continue
            
            else:
                sock.settimeout(avgrtt - tcur + tstart)
                try:
                    ack, _ = sock.recvfrom(PKTSIZE)
                    ack = ack.split(b'\n', 3)
                    ackSeq = int(ack[0].decode())
                    ackEOF = int(ack[1].decode())
                    timestamp = float(ack[2].decode())
                    rttsum += time.time() - timestamp
                    ackNum += 1
                    logProc.writeAck(ackSeq, f'received')
                except:
                    logProc.writePkt(curSeq, f'timeout since {tstart-torigin:.3f}(timeout value {avgrtt:.3f})')
                    curSeq = windowStart
                    pktCnt = 0
                    isEOF = 0
                    tstart = time.time()
                    isRetrans = True
                    continue
            
            #if final ack comes, exit
            if ackEOF == 1:
                break

            #set window start as ack
            if ackSeq >= windowStart:
                newAcked = ackSeq - windowStart + 1
                windowStart = ackSeq + 1
                pktCnt -= newAcked
                ackDup = 1
                newtstart = time.time()
                tstart = newtstart
                for _ in range(newAcked):
                    buffer.pop(0)

            elif ackSeq == windowStart - 1:
                #pdb.set_trace()
                ackDup += 1
            
            #if ack is redundant, set current seq to ack + 1
            if ackDup >= 3:
                logProc.writePkt(ackSeq, '3 duplicated ACKS')
                pktCnt = 0
                curSeq = windowStart
                ackDup = 0
                isEOF = 0
                tstart = 0
                isRetrans = True
                continue

        else:
            #fill the buffer
            if not meetEnd and not isFirst and len(buffer) < windowSize:
                data = file.read(MAXBODYSIZE)
                if len(data) < MAXBODYSIZE:
                    isEOF = 1
                    meetEnd = True
    
                data = b''.join([str(curSeq).encode(), b'\n',
                            str(isEOF).encode(), b'\n',
                            str(len(data)).encode(), b'\n',
                            str(time.time()).encode(), b'\n',
                            data]).ljust(PKTSIZE, b'\0')
                buffer.append(data)
            else:
                isFirst = False
            
            #restart the time when not set
            if tstart == 0:
                tstart = time.time()

            #send the appropriate data in the buffer
            pkt = buffer[pktCnt]

            sock.sendto(pkt, (recvAddr, 10080))
            if isRetrans:
                logProc.writePkt(curSeq, 'retransmitted')
            else:
                logProc.writePkt(curSeq, 'sent')
            isEOF = int(pkt.split(b'\n', 2)[1].decode())
            pktCnt += 1
            curSeq += 1

    file.close()
    logProc.writeEnd(curSeq / (time.time()-torigin), rttsum/float(ackNum)*1000)
    ##########################


if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name

    fileSender()
