#!/usr/bin/python
import socket
import sys
import time
TIMES = 10000000
data = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
        bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\
        bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\
        cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\
        nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn\
        jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj\
        uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu\n'
ADDR = ("192.168.0.51",23456)
if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        sock.connect(ADDR)
        for i in range(TIMES):
            sock.sendall(data)
            dataa= sock.recv(1024)
            time.sleep(0.2)
            #sock.recv(1024)
            #print dataa
    except:
        print 'except'
        sock.close()
