
from nox.lib.core import *
import nox.lib.pyopenflow as of
from nox.coreapps.pyrt.pycomponent import *
from nox.netapps.routing import pyrouting
from nox.netapps.topology.pytopology import pytopology
from nox.netapps.monitoring.monitoring import Monitoring
from nox.netapps.discovery.discovery import discovery
from nox.netapps.authenticator.pyflowutil import Flow_in_event
from nox.netapps.firewall.msg import MSG
from nox.lib.packet.ethernet import ethernet
from nox.lib.packet.packet_utils import ipstr_to_int,ip_to_str


from nox.lib.netinet import netinet
from nox.lib.netinet.netinet import c_ntohl
from nox.lib.util import set_match

from nox.lib.netinet import netinet

import simplejson as json
from socket import ntohs,htons

from twisted.python import log
import logging
import socket
import thread

log = logging.getLogger('nox.netapps.firewall.pyfirewall')
INTERVAL = 2
U32_MAX = 0xffffffff
DP_MASK = 0xffffffffffff
PORT_MASK = 0xffff

BROADCAST_TIMEOUT = 2
FLOW_TIMEOUT = 20

#a dict to record xid
xid = 0
PORT = 12345
BUF_MAX_SIZE = 1024
FIREWALL_PRIORITY = of.OFP_DEFAULT_PRIORITY
FIREWALL_TIMEOUT = 180

#def recv_packet)


class pyfirewall(Component):

    def __init__(self, ctxt):
        self.ctxt_ = ctxt
        Component.__init__(self, ctxt)
        self.ip = {}#ipstr_to_int("192.168.0.51"):{}}
        self.dp_stats ={}
        self.pending_routes = []
        #print dir(ctxt)
        self.requests_queue = {}
        
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #------------------------------
        #According to the Host IP
        #------------------------------
        self.sock.bind(('192.168.56.102',PORT))
        
        self.re = thread.start_new_thread(self.process,())
        #self.sock.listen(5)
        #print 'bind success'
        #self.post_callback(INTERVAL,self.process)


        #start a receive thread that listening on port
    def process(self):
    #    data,(addr,port) = self.sock.recvfrom(BUF_MAX_SIZE,2)
    #    print data,addr,port
    #    self.post_callback(INTERVAL,self) 
        while True:
            
            data,addr = self.sock.recvfrom(BUF_MAX_SIZE)
            m = MSG(data)
            #test
            
            #self.add_rule("192.168.0.51",0x105,0x103,'')
            
            #self.add_rule("192.168.0.51",0x106,0x103,'')
            #self.a
            #

            if m.msg_type == MSG.INIT:
                #print type(m.ip)
                #print ip_to_str(m.ip)
                if m.ip in self.ip:
                    pass
                else:
                    self.ip[m.ip] = {}
                #send ACK packet here....
                msg = MSG(MSG.ACK)
                self.sock.sendto(msg.pack_msg(),addr)

            elif m.msg_type == MSG.QUERY:
                'Reply here'
                if not m.ip in self.ip:
                    #send RESET here
                    self.sock.sendto(MSG(MSG.RESET).pack_msg(),addr)
                    continue
                print 'haha, reply here....'
                #print self.ip#[ipstr_to_int(addr[0])].keys()
                reply = self.get_reply(m.ip)
                #print "reply.num",len(reply.links)
                self.sock.sendto(reply.pack_msg(),addr)

                #pass
            elif m.msg_type == MSG.CONTROL:
                'send control command'
                print 'control msg'
                if not m.ip in self.ip:
                    #maybe send RESET
                    self.sock.sendto(MSG(MSG.RESET).pack_msg(),addr)
                    continue
                #parse the packet and add flow control
                dstip = m.ip
                print m.links
                for link in m.links:
                    self.add_rule(m.ip,int(link[1],16),int(link[2],16),1)
                    
                
                
    def get_reply(self,ipaddr):
        """
        form the reply message
        """
        msg = MSG(MSG.REPLY)
        xids = self.ip[ipaddr].keys()
        if len(xids) == 0:
            return msg
        max_xid = max(xids)
        if self.requests_queue.has_key(max_xid):
            xids.remove(max_xid)
            max_xid = max(xids)
        xids.remove(max_xid)
        if len(xids) == 0:
            second_xid = None # no such xid
        else:
            second_xid = max(xids)
        
        for k in self.ip[ipaddr][max_xid].keys():
            for kk in self.ip[ipaddr][max_xid][k].keys():
                if self.ip[ipaddr].has_key(second_xid) and\
                   self.ip[ipaddr][second_xid].has_key(k) and\
                   self.ip[ipaddr][second_xid][k].has_key(kk):
                    speed = (self.ip[ipaddr][max_xid][k][kk] - self.ip[ipaddr][second_xid][k][kk])/INTERVAL
                else:
                    speed = self.ip[ipaddr][max_xid][k][kk] / INTERVAL
                #print 'before msg.add'
                #print '%.12x' % k, '%.12x'  % kk,speed
                if speed == 0 or speed < 0:
                    #print 'speed' , speed
                    pass
                else:
                    msg.add_reply("%.12x" % k,"%.12x" % kk, speed)
                #print 'after msg.add'
        #print msg
        return msg

    #-----------------------------------------------------
    #Add rule to switches,
    #first find in_port, according src dpid and dst dpid
    #in_port is the inport of dst 
    #@src is src datapath, it is an integer
    #@dst is dst datapath, it is an integer too
    #@command is reject by default
    #-----------------------------------------------------
    def add_rule(self,dstip,src,dst,comand,srcip = None):
        "find inport"
        src = netinet.create_datapathid_from_host(src)
        dst = netinet.create_datapathid_from_host(dst)
        in_ports = []
        if src.as_host() == 0:
            ports = self.dp_stats[dst.as_host()]['ports']
            for port in ports:
                if not self.pytop.is_internal(dst,port):
                    in_ports.append(port)
        else:
            alinks = self.pytop.get_outlinks(src,dst)
            for link in alinks:
                in_ports.append(link.dst)
        #
        #test
        for inport in in_ports:
            flow ={}
            flow[core.NW_DST] = dstip
            flow[core.IN_PORT] = inport
            if srcip != None:
                flow[core.NW_SRC] = srcip

            #If no forward actions are present, the packet is dropped
            actions = []
            self.delete_datapath_flow(dst.as_host(),flow)
            self.install_datapath_flow(dst.as_host(),flow,0,FIREWALL_TIMEOUT,actions,None,FIREWALL_PRIORITY,None,None)
            #by the way modify exists flow
            #self.send_openflow_command(dst.as_host(),flow,FIREWALL_PRIORITY,)


    def install(self):
        '''start a thread to receive message from victim servers
           and response to the request
        '''
        
        self.monitoring = self.resolve(Monitoring)
        self.pytop = self.resolve(pytopology)
        self.routing = self.resolve(pyrouting.PyRouting)
        self.discovery = self.resolve(discovery)
        #print self.discovery,self.resolve(discovery)
        self.register_for_flow_stats_in(self.flow_stats_in_handler)
        self.register_for_datapath_join(self.handle_datapath_join_in)
        self.register_for_datapath_leave(self.handle_datapath_leave)
        self.register_handler(Flow_in_event.static_get_name(),self.handle_flow_in)
        self.register_for_barrier_reply(self.handle_barrier_reply)
        self.post_callback(INTERVAL,self.send_flow_stats_requests)

    def handle_datapath_join_in(self,dpid,stats):
        '''datapath_join_in event handler
        '''
        stats['dpid'] = dpid
        self.dp_stats[dpid] = stats
        port_list = self.dp_stats[dpid]['ports']
        self.dp_stats[dpid]['ports'] = []

        for port in port_list:
            if int(port['port_no']) > 1000: #may be local port
                continue
            self.dp_stats[dpid]['ports'].append(int(port['port_no']))
    def handle_datapath_leave(self,dpid):
        if dpid in self.dp_stats.keys():
            del self.dp_stats[dpid]

        

    def getInterface(self):
        return str(pyfirewall)

    def handle_flow_in(self, event):
    
        if not event.active:
            return CONTINUE
        indatapath = netinet.create_datapathid_from_host(event.datapath_id)
        route = pyrouting.Route()
        
        sloc = event.route_source
        if sloc == None:
            sloc = event.src_location['sw']['dp']
            route.id.src = netinet.create_datapathid_from_host(sloc)
            inport = event.src_location['port']
            sloc = sloc | (inport << 48)
        else:
            route.id.src = netinet.create_datapathid_from_host(sloc & DP_MASK)
            inport = (sloc >> 48) & PORT_MASK
        if len(event.route_destinations) > 0:
            dstlist = event.route_destinations
        else:
            dstlist = event.dst_locations
        
        checked = False
        for dst in dstlist:
            if isinstance(dst, dict):
                if not dst['allowed']:
                    continue
                dloc = dst['authed_location']['sw']['dp']
                route.id.dst = netinet.create_datapathid_from_host(dloc & DP_MASK)
                outport = dst['authed_location']['port']
                dloc = dloc | (outport << 48)
            else:
                dloc = dst
                route.id.dst = netinet.create_datapathid_from_host(dloc & DP_MASK)
                outport = (dloc >> 48) & PORT_MASK
            if dloc == 0:
                continue
            if self.routing.get_route(route):
                checked = True
                if self.routing.check_route(route, inport, outport):
                    log.debug('Found route %s.' % hex(route.id.src.as_host())+\
                            ':'+str(inport)+' to '+hex(route.id.dst.as_host())+\
                            ':'+str(outport))
                    if route.id.src == route.id.dst:
                        firstoutport = outport
                    else:
                        firstoutport = route.path[0].outport
                    
                    p = []
                    if route.id.src == route.id.dst:
                        p.append(str(inport))
                        p.append(str(indatapath))
                        p.append(str(firstoutport))
                    else:
                        s2s_links = len(route.path)
                        p.append(str(inport))
                        p.append(str(indatapath))
                        for i in range(0,s2s_links):
                            p.append(str(route.path[i].dst))
                        p.append(str(outport))

                    #print 'unicast'
                    #print type(event.flow)
                    #print dir(event.flow)
                    #print str(event.flow)#.to_string()
                            
                    self.routing.setup_route(event.flow, route, inport, \
                                    outport, FLOW_TIMEOUT, [], True)
                                    
                    # Send Barriers                
                    pending_route = []
                    #log.debug("Sending BARRIER to switches:")
                    # Add barrier xids
                    for dpid in p[1:len(p)-1]:
                        log.debug("Sending barrier to %s", dpid)
                        pending_route.append(self.send_barrier(int(dpid,16)))
                    # Add packetout info
                    pending_route.append([indatapath, inport, event])
                    # Store new pending_route (waiting for barrier replies)
                    self.pending_routes.append(pending_route)
                           
                    # send path to be highlighted to GUI
                    #self.send_to_gui("highlight",p)
                    
                    # Send packet out (do it after receiving barrier(s))
                    if indatapath == route.id.src or \
                        pyrouting.dp_on_route(indatapath, route):
                        #pass
                        self.routing.send_packet(indatapath, inport, \
                            openflow.OFPP_TABLE,event.buffer_id,event.buf,"", \
                            False, event.flow)
                    else:
                        log.debug("Packet not on route - dropping.")
                    return CONTINUE
                else:
                    log.debug("Invalid route between %s." \
                        % hex(route.id.src.as_host())+':'+str(inport)+' to '+\
                        hex(route.id.dst.as_host())+':'+str(outport))
            else:
                log.debug("No route between %s and %s." % \
                    (hex(route.id.src.as_host()), hex(route.id.dst.as_host())))
        if not checked:
            #just broadcast to external port
            #black food
            eth = ethernet(event.buf)
            if eth.type != ethernet.IP_TYPE and\
                eth.type != ethernet.ARP_TYPE and\
                eth.type != ethernet.PAE_TYPE and\
                eth.type != ethernet.VLAN_TYPE:
                return CONTINUE
            for d in self.dp_stats:
                for port in self.dp_stats[d]['ports']:
                    if not self.pytop.is_internal(\
                    netinet.create_datapathid_from_host(d),port):
                        self.send_openflow_packet(d,event.buf,port)
            return STOP

            

            if event.flow.dl_dst.is_broadcast():
                log.debug("Setting up FLOOD flow on %s", str(indatapath))
                self.routing.setup_flow(event.flow, indatapath, \
                    openflow.OFPP_FLOOD, event.buffer_id, event.buf, \
                        BROADCAST_TIMEOUT, "", \
                        event.flow.dl_type == htons(ethernet.IP_TYPE))
            else:
                inport = ntohs(event.flow.in_port)
                log.debug("Flooding")
                #print 'flooding '
                self.routing.send_packet(indatapath, inport, \
                    openflow.OFPP_FLOOD, \
                    event.buffer_id, event.buf, "", \
                    event.flow.dl_type == htons(ethernet.IP_TYPE),\
                    event.flow)
        else:
            log.debug("Dropping packet")

        return STOP
    def handle_barrier_reply(self, dpid, xid):
        # find the pending route this xid belongs to
        intxid = c_ntohl(xid)
        for pending_route in self.pending_routes[:]:
            if intxid in pending_route:
                pending_route.remove(intxid)
                # If this was the last pending barrier_reply_xid in this route
                if len(pending_route) == 1:
                    log.debug("All Barriers back, sending packetout")
                    indatapath, inport, event = pending_route[0]
                    self.routing.send_packet(indatapath, inport, \
                        openflow.OFPP_TABLE,event.buffer_id,event.buf,"", \
                        False, event.flow)
                    
                    self.pending_routes.remove(pending_route)
                    
        return STOP

    #send flow stats request periodically
    def send_flow_stats_requests(self):
        #send request to all switches
        #self.monitoring.send_flow_stats_request()
        dpids = self.pytop.get_datapaths();
        sent = False
        global xid
        self.requests_queue[xid] = []
        ips = self.ip.keys()
        for ip in ips:
            for dpid in dpids:
            #if True:
                #print type(dpid)
                sent = True
                flow = of.ofp_match()
                flow.wildcards = of.OFPFW_ALL & 0xFFF03FFF
                #print "%x" %flow.wildcards
                #ips = self.ip.keys()
                #for ip in ips:
                flow.nw_dst = ip#self.ip.keys()[0]#convert_to_ipaddr("51.0.168.192")
            
                #print ipstr_to_int("192.168.0.51") == convert_to_ipaddr("51.0.168.192") the same
                #attrs[core.NW_DST] = "192.168.0.51"
                #a = set_match(attrs)

                self.monitoring.send_flow_stats_request(dpid.as_host(),flow,0xff,xid)
                self.requests_queue[xid].append((dpid.as_host(),xid))
                #ready for stor
                self.ip[ip][xid] = {}
                if self.ip[ip].has_key(xid-5):
                    del self.ip[ip][xid-5]

   
            #print self.monitoring.get_latest_switch_stats(dpid.as_host())
            if sent:
                xid = xid + 1
        self.post_callback(INTERVAL,self.send_flow_stats_requests)
    def flow_stats_in_handler(self,dpid,flows,more,xid):
        '''handler for flow stats in event, flows is a dict, one for
           each flow with keys:
           TABLE_ID,MATCH,COOKIE,DUR_SEC,DUR_NSEC,PRIORITY,IDLE_TO,HARD_TO
           PACKET_COUNT,BYTE_COUNT
           @more is a bool,xid is an request id
        '''
        if (not self.requests_queue.has_key(xid) ) or\
            (not ( (dpid,xid) in self.requests_queue[xid] )):
            return CONTINUE

        #print "xid",xid , flows
        


        if more == False:
            self.requests_queue[xid].remove((dpid,xid))
        if len(self.requests_queue[xid]) == 0:
            del self.requests_queue[xid]
            #print 'del self.requests_queue[xid]',xid
        #print dpid,flows,xid

        for flow in flows:
            
            #filtering the drop match
            if (not flow.has_key('actions')) or len(flow['actions']) == 0:
                print flow
                continue

            dstip = flow['match']['nw_dst']

            if not self.ip.has_key(dstip):
                continue
            #print "%x" % dpid,flow['match']['in_port']
            result = self.discovery.get_switch_neighbor_by_port(dpid,\
            flow['match']['in_port'])
            if result == None:
                neighbor = 0x0

            else:
                #print result[0]
                neighbor = result[0]

            if self.ip[dstip].has_key(xid):
                'modify'
                #print 'has_key xid'
                if not self.ip[dstip][xid].has_key(neighbor):
                    self.ip[dstip][xid][neighbor] = {}
                if not self.ip[dstip][xid][neighbor].has_key(dpid):
                    self.ip[dstip][xid][neighbor][dpid] = flow['byte_count']
                else:
                    self.ip[dstip][xid][neighbor][dpid] += flow['byte_count']

                pass
            else:
                #if self.ip[dstip].has_key(xid-4):
                #    del self.ip[dstip][xid-4]
                self.ip[dstip][xid] = { }
                self.ip[dstip][xid][neighbor] = {}
                self.ip[dstip][xid][neighbor][dpid] = flow['byte_count']

        #print self.ip





def getFactory():
    class Factory:
        def instance(self, ctxt):
            return pyfirewall(ctxt)

    return Factory()
