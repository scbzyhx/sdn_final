#!/usr/bin/python
from scapy.all import *


if __name__ == "__main__":
    data =''
    for i in range(1):
        data += "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        
    #data = struct.pack('III',0x12,20,1000)
    pkt = Ether(dst="08:00:27:fe:a7:d1")/\
          IP(dst="192.168.0.51")/UDP(sport=54321,dport=12345)/data
 #for i in range(100):
 #sendp(pkt,loop=True)
    interval = 0.09
    for i in range(9):
        #global interval
        sendp(pkt,inter=interval,count=10000)
        #inteval = interval - 0.05

