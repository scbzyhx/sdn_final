#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel,info
from mininet.node import Controller,RemoteController
from mininet.cli import CLI
from mininet.util import quietRun

IP_SETTING={
    'server1':'192.168.0.101',
    'server2':'192.168.0.101',
    'client':'192.168.0.5'
    
}
#class MyController(RemoteController):
#    def __init__(self,name,ip=''114.212.85.170,port=6633,kwargs):
#        RemoteController.__init__(self,name,ip,port,kwargs)
                

class TurnTopo(Topo):
    "two switch each one"
    def __init__(self):
        Topo.__init__(self)
        oneSwitch = self.addSwitch("s1")
        #twoSwitch = self.addSwitch("s2")
        #midSwitch = self.addSwitch("s3")
        clientPC = self.addHost("h1")
        serverOne = self.addHost("server1")
        #serverTwo = self.addHost("server2")

	"add link"
    
        self.addLink(oneSwitch, clientPC)
        #self.addLink(oneSwitch, twoSwitch)
        #self.addLink(oneSwitch,midSwitch)
        #self.addLink(midSwitch,twoSwitch)
        #
        #self.addLink(twoSwitch, serverOne)
        self.addLink(oneSwitch, serverOne)

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
def TurnNet():
    print "start TurnNet"
    topoo  = TurnTopo()
    info("** creating network\n")
    net = Mininet(topo = topoo, controller = lambda name : RemoteController(name,ip = '114.212.85.7'))
    net.start()
    print 'after start'
    server1,client, sw1 = net.get('server1','h1','s1')
   
    server1.setIP(IP_SETTING["server1"])
   # server2.setIP(IP_SETTING["server2"])
    client.setIP(IP_SETTING["client"])

   # starthttp(server1)
   # starthttp(server2)
    CLI(net)
  #  stophttp(server1)
    stophttp()
    net.stop()

if __name__=="__main__":
    setLogLevel("info")
    TurnNet()
    
