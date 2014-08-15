#!/usr/bin/python

import os, time
import socket
import struct

INTERVAL = 2

IP = '114.212.85.7'
PORT = 12345

def sendInfo(info):
    S = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    S.sendto("12345",(IP,PORT))

    S.close()

while True:
    sendInfo("")
    print 'send'
    time.sleep(INTERVAL)
