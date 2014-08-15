#!/usr/bin/env python
# coding=utf-8
import time
def net_stat():
    net = []
    f = open("/proc/net/dev")
    lines = f.readlines()
    f.close()
    for line in lines[2:]:
        con = line.split()  
        """ 
        intf = {} 
        intf['interface'] = con[0].lstrip(":") 
        intf['ReceiveBytes'] = int(con[1]) 
        intf['ReceivePackets'] = int(con[2]) 
        intf['ReceiveErrs'] = int(con[3]) 
        intf['ReceiveDrop'] = int(con[4]) 
        intf['ReceiveFifo'] = int(con[5]) 
        intf['ReceiveFrames'] = int(con[6]) 
        intf['ReceiveCompressed'] = int(con[7]) 
        intf['ReceiveMulticast'] = int(con[8]) 
        intf['TransmitBytes'] = int(con[9]) 
        intf['TransmitPackets'] = int(con[10]) 
        intf['TransmitErrs'] = int(con[11]) 
        intf['TransmitDrop'] = int(con[12]) 
        intf['TransmitFifo'] = int(con[13]) 
        intf['TransmitFrames'] = int(con[14]) 
        intf['TransmitCompressed'] = int(con[15]) 
        intf['TransmitMulticast'] = int(con[16]) 
        """  
        intf = dict(  
            zip(  
            ( 'interface','ReceiveBytes','ReceivePackets',  
                'ReceiveErrs','ReceiveDrop','ReceiveFifo',  
                'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',  
                'TransmitBytes','TransmitPackets','TransmitErrs',  
                'TransmitDrop', 'TransmitFifo','TransmitFrames',  
                'TransmitCompressed','TransmitMulticast' ),  
                ( con[0].rstrip(":"),int(con[1]),int(con[2]),  
                int(con[3]),int(con[4]),int(con[5]),  
                int(con[6]),int(con[7]),int(con[8]),  
                int(con[9]),int(con[10]),int(con[11]),  
                int(con[12]),int(con[13]),int(con[14]),  
                int(con[15]),int(con[16]), )  
                )  
            )  
        net.append(intf)  
    return net

def getInterfaceSpeed(interface):
    #while True:
    net = []
    net1=net_stat()
    time.sleep(1)
    net2=net_stat()
    for net_1 in net1:
        for net_2 in net2:
            print net_1['interface']
            if net_1['interface']==interface and net_2['interface']==interface:
                print 'speed of TransmitBytes: '+\
                   str(net_2['TransmitBytes']-net_1['TransmitBytes'])+' B/s'
                print 'speed of ReceiveBytes: '+\
                    str(net_2['ReceiveBytes']-net_1['ReceiveBytes'])+' B/s'
                net.append(net_2['TransmitBytes']-net_1['TransmitBytes'])
                net.append(net_2['ReceiveBytes']-net_1['ReceiveBytes'])
    return net
print getInterfaceSpeed('h1-eth0')
