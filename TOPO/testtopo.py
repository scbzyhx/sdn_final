#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel,info
from mininet.node import Controller,RemoteController,Node,OVSController
from mininet.cli import CLI
from mininet.util import quietRun

DPID_BASE = 100
IP_BASE = "192.168.0."
IP_START = 50
GW = "192.168.0.1"
#class MyController(RemoteController):
#    def __init__(self,name,ip=''114.212.85.170,port=6633,kwargs):
#        RemoteController.__init__(self,name,ip,port,kwargs)
                


def fixNetworkManager( root, intf ):
    """Prevent network-manager from messing with our interface,
    by specifying manual configuration in /etc/network/interfaces
    root: a node in the root namespace (for running commands)
    intf: interface name"""
    cfile = '/etc/network/interfaces'
    line = '\niface %s inet manual\n' % intf
    config = open( cfile ).read()
    if line not in config:
        print '*** Adding', line.strip(), 'to', cfile
        with open( cfile, 'a' ) as f:
            f.write( line )
            # Probably need to restart network-manager to be safe -
            # hopefully this won't disconnect you
            root.cmd( 'service network-manager restart' )

def connectToInternet( network,host ):
    #"Start simple Python web server on hosts"
    info( '*** Starting SimpleHTTPServer on host', host, '\n' )
    #host.cmd( 'cd ./http_%s/; nohup python2.7 ./webserver.py &' % (host.name) )
    root = Node('root',inNamespace = False)
    host = network.get(host)
    fixNetworkManager(root,'root-eth0')

    #create link
    link = network.addLink(root,host)
    link.intf1.setIP('10.0.0.254',8)
    link.intf2.setIP('10.0.0.250',8)

    network.start()
    
    startNAT(root)
    setRoute(host)
    return root

def startNAT(root,inetIntf='eth0',subnet='10.0.0.0/8'):
    "Start NAT betweent victim server and Internet"
    localIntf = root.defaultIntf()

    print localIntf

    root.cmd('iptables -F')
    root.cmd('iptables -t nat -F')

    root.cmd('iptables -P INPUT ACCEPT')
    root.cmd('iptables -P OUTPUT ACCEPT')
    root.cmd('iptables -P FORWARD DROP')
    
    #configure NAT

    root.cmd('iptables -I FORWARD -i', localIntf, '-d', subnet,' -j DROP')
    root.cmd('iptables -A FORWARD -i', localIntf, '-s', subnet,' -j ACCEPT' )
    root.cmd('iptables -A FORWARD -i', inetIntf, '-d', subnet, '-j ACCEPT')
    root.cmd('iptables -t nat -A POSTROUTING -o',inetIntf, '-j MASQUERADE')

    root.cmd('sysctl net.ipv4.ip_forward=1')


def stopNAT(root):
    root.cmd('iptables -F')
    root.cmd('iptables -t nat -F')
    root.cmd('sysctl net.ipv4.ip_forward=0')

def setRoute(host,subnet='10.0.0.0/8'):
    host.cmd('ip route flush root 0/0')
    host.cmd('route add -net',subnet,'dev',host.defaultIntf())
    host.cmd('route add default gw','10.0.0.254')

    


def stophttp():
    "Stop simple Python web servers"
    info( '*** Shutting down stale SimpleHTTPServers',
          quietRun( "pkill -9 -f SimpleHTTPServer" ), '\n' )
    info( '*** Shutting down stale webservers',
          quietRun( "pkill -9 -f webserver.py" ), '\n' )
class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        self.addHost('h0')
def TurnNet():
    print "start TurnNet"
    topoo  = MyTopo()
    info("** creating network\n")
    net = Mininet(topo = topoo, controller = OVSController) #lambda name : RemoteController(name,ip = '114.212.85.7'))
    temp = connectToInternet(net,'h0')
    CLI(net)
    stopNAT(temp)
    
  #  stophttp(server1)
    #stophttp()
    net.stop()

if __name__=="__main__":
    setLogLevel("info")
    TurnNet()
    
