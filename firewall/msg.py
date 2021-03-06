#!/usr/bin/env python
# coding=utf-8
import struct
from array import *
import socket
import thread
import time
import signal
import sys
IP="192.168.56.101"
PORT=12345
basicSpeed=1000

def ipstr_to_int(a):
    octets = a.split('.')
    return int(octets[0]) << 24 |\
           int(octets[1]) << 16 |\
           int(octets[2]) <<  8 |\
           int(octets[3]);

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
                s+=link[0]+' > '+link[1]+' : '+str(link[2])+' | '
        elif self.msg_type==MSG.RESET:
            s='RESET!!!'
        else: 
            print 'str error\n'
        return s
#msg is a binary string packed py MSG
def send_packet(msg):
    S= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    S.sendto(str(msg),(IP,PORT))
    S.close()

def recv_packet():
    S=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    S.bind(("127.0.0.1",250))
    #S.settimeout(2.5)
    link=[]
    while True:
        #try:
        data=S.recv(1024)
        msg=MSG(data)
        #here is check the data and reply control msg
        #print str(msg) 
        if len(link)==0:
            link=msg.links
            continue
        else:
            link_new=msg.links
            #from here is checking
            for i in len(link_new):
                link_new[i][2]=link_new[i][2]-link[i][2]
            link=msg.links
            msg_reply=MSG(MSG.CONTROL)
            for j in range(len(link_new)):
                if abs(link_new[i][2])>basicSpeed:
                    msg_reply.add_control(link_new[i][0],link_new[i][1],1)
            if len(msg_reply.links)>0:
                send_packet(msg_reply.pack_msg())
            #except timeout as e:
            #    pass
    S.close()

#re=thread.start_new_thread(recv_packet,())

#dict to switch
STATE = MSG.INIT
IP_CONTROL = "192.168.0.51"
def init_function(sock):
    global STATE
    msg = MSG(MSG.INIT)
    msg.set_ip(ipstr_to_int(IP_CONTROL))
    sock.sendto(msg.pack_msg(),(IP,PORT))
    data,addr = sock.recvfrom(1024)
    m = MSG(data)
    if m.msg_type == MSG.ACK:
        STATE = MSG.QUERY
    return
def query_function(sock):
    global STATE
    msg_query = MSG(MSG.QUERY)
    msg_query.set_ip(ipstr_to_int(IP_CONTROL))
    sock.sendto(msg_query.pack_msg(),(IP,PORT))
    data,addr = sock.recvfrom(1024)
    #save state and 
    msg = MSG(data)
    if msg.msg_type  == MSG.RESET:
        STATE = MSG.INIT
    elif msg.msg_type == MSG.REPLY:
        "call a function here"
        with open('a.txt','a') as f:
            f.write(str(msg))
            f.write('\n')
            f.close()
        pass
    "otherwise do nothing"

def decide_control(sock):
    pass
#state_function ={}

if False:#__name__ == '__main__':
    #S= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #S.connect((IP,12345))
    #S.settimeout(10)
    #S.setblocking(0)
    while True:
        if STATE == MSG.INIT:
            init_function(S)
        elif STATE == MSG.QUERY:
            query_function(S)
        sleep(2)
    S.close()

