#!/usr/bin/python
from SocketServer import *
from time import ctime
import traceback

TIMES = 10000000
class Server(StreamRequestHandler):
    def handle(self):
        i = TIMES
        while i>1:
            try:
                data = self.rfile.readline().strip()
                self.wfile.write(data.upper()+'\n')
            except:
                print 'except'
                return
            i = i-1

if __name__ == "__main__":
    ADDR = ("192.168.0.51",23456)
    s = ThreadingTCPServer(ADDR,Server)
    s.serve_forever()


