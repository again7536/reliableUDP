import socket
import time
from logHandler import logHandler

def fileReceiver():
    print('receiver program starts...')
    logProc = logHandler()
    #########################

    #Write your Code here

    PKTSIZE = 1400
    curSeq = -1
    pktSeq = 0
    ackSeq = -1
    isEOF = 0
    bodySize = 0
    file = ''
    torigin = time.time()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 10080))
    
    while True:
        if isEOF == 1:
            sock.settimeout(1)
        
        #if timeout is set, error occur after waiting
        try:
            data, servAddr = sock.recvfrom(PKTSIZE)
        except:
            #if sender stops first, close
            if isEOF == 1:
                break
        
        #parse the packet
        data = data.split(b'\n', 4)
        pktSeq = int(data[0].decode())
        isEOF = int(data[1].decode())
        bodySize = int(data[2].decode())
        timestamp = float(data[3].decode())
        body = data[4][:bodySize]
        
        #if it is the first packet, open file
        if curSeq == -1 and pktSeq == 0:
            filename = body.decode()
            file = open(filename, 'wb')
            logProc.startLogging(f'{filename}_receiving_log.txt')
            curSeq += 1
        #in-order packet accept
        elif curSeq + 1 == pktSeq:
            file.write(body)
            curSeq += 1

        ackSeq = curSeq
        
        if curSeq >= 0:
            logProc.writePkt(pktSeq, 'received')
        
        if curSeq <= pktSeq:
            #duplicated but end of file
            if curSeq == pktSeq and isEOF == 1:
                isEOF = 1
            #duplicated or out-of-order
            else:
                isEOF = 0

            #build ack
            ack = b''.join([str(ackSeq).encode(), b'\n',
                            str(isEOF).encode(), b'\n',
                            str(timestamp).encode(), b'\n']).ljust(1400, b'\0')

            try:
                sock.sendto(ack, servAddr)
                if ackSeq >= 0:
                    logProc.writeAck(ackSeq, 'sent')
            except: #when sender socket is closed
                file.close()
                break
    
    logProc.writeEnd(curSeq / (time.time() - torigin))
    #########################


if __name__=='__main__':
    fileReceiver()
