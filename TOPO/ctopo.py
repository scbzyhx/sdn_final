#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel,info
from mininet.node import Controller,RemoteController
from mininet.cli import CLI
from mininet.util import quietRun

DPID_BASE = 100
IP_BASE = "192.168.0."
IP_START = 50
GW = "192.168.0.1"
#class MyController(RemoteController):
#    def __init__(self,name,ip=''114.212.85.170,port=6633,kwargs):
#        RemoteController.__init__(self,name,ip,port,kwargs)

clss CTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        self.sw = self.addSwitch('sc1',dpid='00000000000000111')
        self.con = self.addHost('hc1')
        self.addLink(s,g)
    

class MyTopo(Topo):
    "two switch each one"
    def __init__(self,path = None):
        Topo.__init__(self)
        self.my_hosts = {}
        self.my_switches = {}
        #self.loadTopoFromFile('config.topo')
        self.s = self.addSwitch('s1',dpid = '0000000000000001')

    def loadTopoFromFile(self,path):
        with open(path) as filein:
            for line in filein:
                lines = line.strip('\n').split(',')
                if lines[0] == '@':
                    break
                if lines[1] == 'h':
                    self.my_hosts[lines[0]] = self.addHost("h%d" % int(lines[0]))
                elif lines[1] == 's':
                    #print "%.16d" % (DPID_BASE + int(lines[0]))
                    self.my_switches[lines[0]] = self.addSwitch('s%d' % int(lines[0]),\
                    dpid='%.16d' % (DPID_BASE + int(lines[0])))
            for line in filein:
                print line
                lines = line.strip('\n').split(',')
                if len(lines) < 3:
                    break
                left = None
                right = None
                if lines[0] in self.my_hosts:
                    left = self.my_hosts[lines[0]]
                elif lines[0] in self.my_switches:
                    left = self.my_switches[lines[0]]

                if lines[1] in self.my_hosts:
                    right = self.my_hosts[lines[1]]
                elif lines[1] in self.my_switches:
                    right = self.my_switches[lines[1]]
                if left != None and right != None:
                    self.addLink(left,right)



                    
                    
                

                
                        
    


def starthttp( host ):
    "Start simple Python web server on hosts"
    info( '*** Starting SimpleHTTPServer on host', host, '\n' )
    host.cmd( 'cd ./http_%s/; nohup python2.7 ./webserver.py &' % (host.name) )


def stophttp():
    "Stop simple Python web servers"
    info( '*** Shutting down stale SimpleHTTPServers',
          quietRun( "pkill -9 -f SimpleHTTPServer" ), '\n' )
    info( '*** Shutting down stale webservers',
          quietRun( "pkill -9 -f webserver.py" ), '\n' )


def With
def TurnNet():
    print "start TurnNet"
    topoo  = MyTopo()
    info("** creating network\n")
    net = Mininet(topo = topoo, controller = lambda name : RemoteController(name,ip = '114.212.85.7'))
    net.start()
    print 'after start'
   # server1,client, sw1 = net.get('server1','h1','s1')
    for h in topoo.my_hosts.keys():
        host = net.get('h'+h)
        host.setIP(IP_BASE + "%d" %(IP_START+int(h)),24)
        #print host.intfList()
        #host.cmd('route add 10.0.0.1')
        host.cmd('route add default gw 192.168.0.1')
        host.setARP('192.168.0.1','00:00:00:00:00:01')
   
    #server1.setIP(IP_SETTING["server1"])
   # server2.setIP(IP_SETTING["server2"])
   # client.setIP(IP_SETTING["client"])

   # starthttp(server1)
   # starthttp(server2)
    CLI(net)
  #  stophttp(server1)
    #stophttp()
    net.stop()

if __name__=="__main__":
    setLogLevel("info")
    TurnNet()
    
