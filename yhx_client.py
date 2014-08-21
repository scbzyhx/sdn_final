#!/usr/bin/env python
# coding=utf-8
from scipy import stats
import numpy as np

import struct
from array import *
import socket
import thread
import time
import signal
import sys
import net_stat
IP="192.168.56.101"
PORT=12345
basicSpeed=10000
THRESHHOLD = 3

INTERVAL = 6

def ipstr_to_int(a):
    octets = a.split('.')
    return int(octets[0]) << 24 |\
           int(octets[1]) << 16 |\
           int(octets[2]) <<  8 |\
           int(octets[3]);
info = []
global_count = 0
links_history ={}  #[src][dst][global_count] = val
def graph(links,reverse=False):
    g = {}
    for link in links:
        try:
            if not reverse:
                g[link[0]][link[1]] = link[2]
            else:
                g[link[1]][link[0]] = link[2]

        except:
            if not reverse:
                g[link[0]] ={}
                g[link[0]][link[1]] = link[2]
            else:
                g[link[1]] ={}
                g[link[1]][link[0]] = link[2]
    return g

#---------------------------
#already under attack
#links are link from REPLY msg
#--------------------------a
def getResult(links):
    global info
    #global links_history
    #global global_count
    result = []
    #history 
    new = graph(links)
    reverse_new = graph(links,True)
    #
    #store links_history
    #
    #for k in new.keys():
    #    for kk in new[k].keys():
    #        if links_history.has_key(k) and links_history[k].has_key(kk):
    #            links_history[k][kk][global_count] = new[k][kk]
    #        else:
    #            links_history[k] = {}
    #            links_history[k][kk] = {}
    #            links_history[k][kk][global_count] = new[k][kk]

    #global_count + =1
    ##########################################################

    if len(info) == 0:
        info.append(new)
        return result                
    else:
        "First find burst flow"
        last = info[-1]
        new_burst = []
        for kk in new.keys():
            for k in new[kk].keys():
                if last.has_key(kk) and last[kk].has_key(k):
                    pass
                else:
                    new_burst.append((kk,k,new[kk][k]))
        result = findsrc(new_burst)
        #info.append(new)
        if len(result) != 0:
            info.append(new)
            return result
        #else
        "Get the link speed increases fastest"
        
        overlist =[]
        for kk in new.keys():
            for k in new[kk].keys():
                try:
                    #The First
                    if (new[kk][k] - last[kk][k] )/last[kk][k] > THRESHHOLD:
                        overlist.append((kk,k,new[kk][k]))
                    
                    #The second
                    #if
                except:
                    continue

        result = findsrc(overlist)
        
        if len(result) >0:
            info.append(new)
            return result

        #choose the links that increase fastest
        start = 0
        if True:
            for kk in new.keys():
                for k in new[kk].keys():
                    try:
                        #if (new[kk][k] - last[kk][k]) / INTERVAL > start:
                        #    overlist = []
                        x = []
                        y = []
                        for l in links_history[kk][k].keys():
                            x.append(l)
                            y.append(links_history[kk][k][l])
                        slope,intercept,r_value,p_value,slope_std_error =\
                        stats.linregress(x,y)
                        if slope > start:
                            overlist = []
                            overlist.append((kk,k,new[kk][k]))
                    except:
                        continue
            with open("fastest",'a') as f:
                f.write(overlist[0][0])
                f.close()
            return findsrc(overlist)

               
#-------------------------------
#links is a list of tuples
#graph is a reverse graph,[dst][src]
#=-----------------------------

def findsrc(links):
    blocklink =[]
    #fist convert links to a dict
    tmpdict = {}
    for link in links:
        if not tmpdict.has_key(link[1]):
            tmpdict[link[1]] = {}
        tmpdict[link[1]][link[0]] = link[2]
        #else:
        #    tmpdict[link[1]][link[0]] = link[2]
    
    #then find the src
    for link in links:
        if link[0] == '000000000000':
            blocklink.append(link)
            continue

        if tmpdict.has_key(link[0]):
            continue
        else:
            blocklink.append(link)
    return blocklink
            #elif graphs[dst] == '000000000000':
                
    

def algo(links):
    
    global links_history
    global global_count
    #store links' history
    added = False
    for link in links:
        added = True
        if links_history.has_key(link[0]):
            if links_history[link[0]].has_key(link[1]):
                links_history[link[0]][link[1]][global_count] = link[2]
            else:
                links_history[link[0]][link[1]] = {}
                links_history[link[0]][link[1]][global_count] = link[2]
        else:
            links_history[link[0]] = {}
            links_history[link[0]][link[1]] = {}
            links_history[link[0]][link[1]][global_count] = link[2]
    if added:
        global_count = global_count + 1

    #print "global_count", global_count
    #with open('result3','w') as ff:
    #    ff.write(str(links_history))
    #    ff.close()




    if victim("h1-eth0") == 1:
        return getResult(links)
    else:
        return []


   
def victim(eth):
    speed=net_stat.getInterfaceSpeed(eth)
    if speed[1]>basicSpeed:
        return 1
    else :
        return 0

#for ele in algo():
#    print 'answer:'
#    print ele.dstid
class MSG:
    INIT=0x01
    ACK=0x02
    QUERY=0x03
    REPLY=0x04
    CONTROL=0x05
    RESET=0x06
    def __init__(self,arr):
        self.arr = arr
        self.links=[]
        if type(arr) == type(1):
            self.msg_type = arr
        elif type(arr) == type(''):
            self.unpack_msg()

        #self.arr=arr
    
    def set_ip(self,ip):
        self.ip=ip    
    def pack_msg(self):
        if self.msg_type==MSG.INIT:
            buf=struct.pack('!B',self.msg_type)
            buf+=struct.pack('!I',self.ip)
        elif self.msg_type==MSG.ACK or self.msg_type==MSG.RESET:
            buf=struct.pack('!B',self.msg_type)
        elif self.msg_type==MSG.QUERY:
            buf=struct.pack('!B',self.msg_type)
            buf+=struct.pack('!I',self.ip)
        elif self.msg_type==MSG.REPLY:
            buf=struct.pack('!BI',self.msg_type,len(self.links))
            for link in self.links:
                if link[0]==None:
                    src='000000000000'
                    buf+=src
                    buf+=link[1]
                else: 
                    buf+=link[0]+link[1]
                buf+=struct.pack('!I',link[2])
        elif self.msg_type==MSG.CONTROL:
            buf=struct.pack('!BII',self.msg_type,self.ip,len(self.links))
            for link in self.links:
                if link[1]==None:
                    src='000000000000'
                    buf+=struct.pack('!I',link[0])
                    buf+=src
                    buf+=link[2]
                else:
                    buf+=struct.pack('!I',link[0])
                    buf+=link[1]+link[2]
                buf+=struct.pack('!B',link[3])
        else: 
            print 'error msg type'
        return buf
    def unpack_msg(self):
        (self.msg_type,)=struct.unpack('!B',self.arr[:1])
        print str(self.msg_type)
        if self.msg_type==MSG.INIT or self.msg_type==MSG.QUERY:
            (self.ip,)=struct.unpack('!I',self.arr[1:5])
        elif self.msg_type==MSG.REPLY:
            (num,)=struct.unpack('!I',self.arr[1:5])
            for i in range(num):
                (arr_reply,)=struct.unpack('!I',self.arr[(29+28*i):(33+28*i)])
                self.links.append((self.arr[(5+28*i):(17+28*i)],\
                                  self.arr[(17+28*i):(29+28*i)],\
                                  arr_reply))
        elif self.msg_type==MSG.CONTROL:
            (self.ip,num,)=struct.unpack('!II',self.arr[1:9])
            for i in range(num):
                (srcip,)=struct.unpack('!I',self.arr[(29*i+9):(29*i+13)])
                (control_type,)=struct.unpack('!B',self.arr[(29*i+37):(29*i+38)])
                self.links.append((srcip,self.arr[(29*i+13):(29*i+25)],\
					  self.arr[(29*i+25):(29*i+37)],\
					  control_type))
    def add_reply(self,src,dst,arr_reply):
        if src==None:
            src='000000000000'
        if dst==None:
            dst='000000000000'
        self.links.append((src,dst,arr_reply))
    def add_control(self,destip,src,dst,control_type):
        if destip==None:
            destip=0
        if src==None:
            src='000000000000'
        if dst==None:
            dst='000000000000'
        self.links.append((destip,src,dst,control_type))
        
    def __str__(self):
        s=''
        if self.msg_type==MSG.INIT:
            s='INIT!!! '
        elif self.msg_type==MSG.ACK:
            s='ACK!!!'
        elif self.msg_type==MSG.QUERY:
            s='QUERY!!! '
        elif self.msg_type==MSG.REPLY:
            s='REPLY!!! '
            for link in self.links:
                s+=link[0]+' > '+link[1]+' : '+str(link[2])+' | '
        elif self.msg_type==MSG.CONTROL:
            s='CONTROL!!! '
            for link in self.links:
                s+=str(link[0])+' '+link[1]+' > '+link[2]+' : '+str(link[3])+' | '
        elif self.msg_type==MSG.RESET:
            s='RESET!!!'
        else: 
            print 'str error\n'
        return s

#dict to switch
STATE = MSG.INIT
IP_CONTROL = "192.168.0.51"
def init_function(sock):
    global STATE
    msg = MSG(MSG.INIT)
    msg.set_ip(ipstr_to_int(IP_CONTROL))
    sock.sendto(msg.pack_msg(),(IP,PORT))
    #while True:
    try:
        data,addr = sock.recvfrom(1024)
        #break
    except:
    #    print 'herer'
        sock.connect((IP,12345))
        return 
    m = MSG(data)
    if m.msg_type == MSG.ACK:
        STATE = MSG.QUERY
    return
def query_function(sock):
    global STATE
    msg_query = MSG(MSG.QUERY)
    msg_query.set_ip(ipstr_to_int(IP_CONTROL))
    sock.sendto(msg_query.pack_msg(),(IP,PORT))
    try:
        data,addr = sock.recvfrom(1024)
    except:
        STATE = MSG.INIT
        S.connect((IP,12345))
        return 
    #save state and 
    msg = MSG(data)
    if msg.msg_type  == MSG.RESET:
        STATE = MSG.INIT
    elif msg.msg_type == MSG.REPLY:
        "call a function here"
        control_list=algo(msg.links)
        print control_list
        if control_list == None:
            return
        msg_con=MSG(MSG.CONTROL)
        for link in control_list:
            msg_con.add_control(0,link[0],link[1],1)#link.bw)
        msg_con.set_ip(ipstr_to_int(IP_CONTROL))
        sock.sendto(msg_con.pack_msg(),(IP,PORT))
        #with open('result2','w') as ff:
        #    ff.write(str(links_history))
        #    ff.close()
        with open('result','a') as ff:
            ff.write(str(msg))
            ff.write('\n')
            ff.write(str(msg_con))
            ff.write('\n\n')
            ff.flush()
            ff.close()
    "otherwise do nothing"

def decide_control(sock):
    pass
#state_function ={}
S= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#def con():
#    global S
S.connect((IP,12345))
#try:
#    con()
#except :
#    print 'nothing'
f=open('speed.txt','w')
def myhandle_1(a,e):
    global f
    print 'close socked'
    S.close()
    f.close()
    sys.exit(0)
signal.signal(signal.SIGINT, myhandle_1)
signal.signal(signal.SIGTERM, myhandle_1)

def get_speed():
    global f
    while True:
        speed=net_stat.getInterfaceSpeed('h1-eth0')
        f.write(str(speed[1]))
        f.write('\n')
        f.flush()
        time.sleep(0.5)

re=thread.start_new_thread(get_speed,())
if __name__ == '__main__':
    #S= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #S.connect((IP,12345))
    #S.settimeout(10)
    #S.setblocking(0)
    while True:
        if STATE == MSG.INIT:
            init_function(S)
        elif STATE == MSG.QUERY:
            query_function(S)
        time.sleep(6)
    S.close()

