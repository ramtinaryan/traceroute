# imports
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_2, ether, inet
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, arp, tcp, udp
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_all_switch
from ryu.topology.api import get_link, get_all_link
import ryu.app.ofctl.api as api
import ryu.utils as utils

import gather, requests, random, json, re, sys
import generator, time, gather, probing, netaddr, array
import copy

#### CLASS
class ctrlapp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]


    #### INIT
    def __init__(self, *args, **kwargs):
        super(ctrlapp, self).__init__(*args, **kwargs)
        self.isTesting = False
        self.testingRules =[]
        self.isTablesPopulated = False
        self.totalSent = 0
        self.totalReceived = 0
        self.starttime = 0
        self.rulesInstalled = 0
        self.rulesRemoved = 0
        self.generateTime = 0
        self.totalOverlap = 0
        self.pullFlowTable = 0
        self.allFlowTables = dict()
        self.packetGenTime = 0
        self.installCatchRuleTime = 0
        self.skipFirstMiss = 0
        self.dataPathsList = dict()
        self.tos=0
        self.dstSwitch=0
        # USed for learning switch functioning
        self.mac_to_port = {}
        # Holds the topology data and structure
        self.topo_raw_switches = []
        self.topo_raw_links = []


    #### PACKET IN
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packetIn(self, ev):
        """ PacketIn message """

        # Parse the incoming packet
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt = packet.Packet(msg.data)
            

        # Empty packets, will/should never happen
        if len(pkt.get_protocols(ethernet.ethernet)) < 1:
            return
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignore LLDP packets when using verbose mode
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        #   print out the packetin

        """print ("\n OFPPacketIn received: switch=", datapath.id, "buffer_id=", 
            msg.buffer_id , "total_len=" , msg.total_len , " reason=" , 
            msg.reason , "table_id=" , msg.table_id , "cookie=" , msg.cookie , 
            "match=" , msg.match , "pkt=" , pkt , "\n")
        """
        
        # Populate flow tables, once
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            if (pkt.get_protocols(arp.arp)[0].src_ip == "10.0.0.1" and 
            pkt.get_protocols(arp.arp)[0].dst_ip == "10.0.0.20" and 
            pkt.get_protocols(arp.arp)[0].src_mac == "00:00:00:00:00:01"):
                if not self.isTablesPopulated:
                    self.populateAllFlowtables()
                    self.isTablesPopulated = True


        # Reset Test  
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            if (pkt.get_protocols(arp.arp)[0].src_ip == "10.0.0.1" and 
            pkt.get_protocols(arp.arp)[0].dst_ip == "10.0.0.30" and 
            pkt.get_protocols(arp.arp)[0].src_mac == "00:00:00:00:00:01"):
                if self.isTesting:
                    self.isTesting=False
                    print("*********************************************************************")
                    print("*********************************************************************")
                    print("*********************************************************************")
                    print("**************    TEST IS RESET SUCESSFULLY !!!    ******************")
                    print("*********************************************************************")
                    print("*********************************************************************")

        # Check trigger conditions to start testing
        if (eth.ethertype == ether_types.ETH_TYPE_ARP and not self.isTesting):
            if (pkt.get_protocols(arp.arp)[0].src_ip == "10.0.0.1" and 
            pkt.get_protocols(arp.arp)[0].dst_ip == "10.0.0.10" and 
            pkt.get_protocols(arp.arp)[0].src_mac == "00:00:00:00:00:01"):
                self.isTesting = True
                queries=probing.getQueries()
                self.dataPathsList=self.getDataPaths()
                for query in queries:
                    probepath=query["path"]
                    print("probepath: ",probepath)
                    probePacket=query["packet"]
                    print("probe: ",probePacket)
                    self.tos=int(query["tos"])
                    self.dstSwitch=int(query["dst"])
#                probePackage={"probePacket":probePacket,"probepath":probepath}
#                probeList=list()
#                probeList.append(probePackage)
#                self.dataPathsList=self.getDataPaths()
#                print("datapaths: ", self.dataPathsList)
#                print("datapath 1: ", self.dataPathsList[1])

#                self.frodeTest(msg, datapath, ofp, pkt)
                    self.ramtinTest(msg, datapath, ofp, pkt, query)
        # Check packetin L3 PDU for ToS
        if msg.reason == ofp.OFPR_ACTION:
            if len(pkt.get_protocols(ipv4.ipv4)) is not 0:
                if pkt.get_protocols(ipv4.ipv4)[0].tos is self.tos:
                    self.totalReceived += 1
                    if  datapath.id is self.dstSwitch: 
                        print("*********************************************************************")
                        print("*********************************************************************")
                        print("*********************************************************************")
                        print("*****************       REACH  THE TARGET       *********************")
                        print("*********************************************************************")
                        print("*********************************************************************")
                    else:
                        print("*********************************************************************")
                        print("*********************************************************************")
                        print("*********************************************************************")
                        print("************    WARNING : THERE IS A FAILURE !!!    *****************")
                        print("*********************************************************************")
                        print("*********************************************************************")


                    # is last rule?
                    if len(self.testingRules) is 0:
                        print ("TOTAL SENT " , self.totalSent)
                        print ("RECEIVED LAST " , self.totalReceived)
                        print ("TOTAL OVERLAPS: " , self.totalOverlap)
                        print ("CATCH-RULE INSTALLATION TIME: " , format(self.installCatchRuleTime - self.starttime, '.5f'))
                        print ("TIME ON LINK: " , format(time.time() - self.starttime - self.packetGenTime, '.5f'))
                        print ("TOTAL RUNTIME: " , format(time.time() - self.starttime, '.5f'))
            '''    else:
                    forwardingProcess(ev)
            '''
        # Invalid TTL, might be caused by loop
        elif msg.reason == ofp.OFPR_INVALID_TTL:
            print ("INVALID TTL")
            # is test packet?
            if len(pkt.get_protocols(ipv4.ipv4)) is not 0:
                if pkt.get_protocols(ipv4.ipv4)[0].tos is self.tos:
                    print ("INVALID TTL ON TEST PACKET")



        # Table miss, might be shadow or non-working rule? or just a miss
        elif msg.reason == ofp.OFPR_NO_MATCH:
            # is test packet?
            if len(pkt.get_protocols(ipv4.ipv4)) > 0:
                if pkt.get_protocols(ipv4.ipv4)[0].tos is self.tos and self.skipFirstMiss > 0:
                    # yes its a test packet, investigate..
                    self.totalReceived += 1
                    probe = self.compareMatchPacket(pkt)
                    if probe != -1:
                        print ("Rule MISS received on " , datapath.id , " , but was expected on " , probe["neighbour"])
                        print ("ENTRY: \n" , probe)
                self.skipFirstMiss += 1


    ### Frode Test
    def frodeTest(self, msg, datapath, ofp, pkt):
        
        # Time the execution
        self.starttime = time.time()
        allSwitches = self.getAllDatapaths()
        # Loop through all switches
        for sw in allSwitches:
            print("===============================================================================")
            print ("Testing switch: " , sw.dp.id)
            #if sw.dp.id is 1:
            # remove catch rule from self, if any
            self.removeCatchRuleByID(sw.dp.id)

            # Install catch rules on neighbours
            allNeighbours = self.getNeighborsByID(sw.dp.id)
            for neigh in allNeighbours: # id
                self.addCatchRuleByID(int(neigh,16))

            # Scrape and sort flowtable
            flowtable = gather.getMatchData(sw.dp.id)
            flowtable = sorted(flowtable, key=generator.sortKey, reverse=True)


            # Loop through flow table entries
            for entry in flowtable:
                # Generate packet from match field and rules above
                pkt = generator.packetFromMatch(entry, flowtable)
                self.generateTime = time.time()

                # add packet to list
                entry["packet"] = {"ip" : pkt.get_protocol(ipv4.ipv4())}

                if entry["packet"]["ip"].proto is 6:
                    entry["packet"]["tcp"] = pkt.get_protocol(tcp.tcp())
                elif entry["packet"]["ip"].proto is 17:
                    entry["packet"]["udp"] = pkt.get_protocol(udp.udp())

                # is total overlap? 
                if pkt == -1:
                    # log and move on
                    entry["totalOverlap"] = True
                    self.totalOverlap += 1
                    # log some info about
                    # the entry & packet
                    break # ?

                # is drop rule?
                if (len(entry["actions"]) is 0 or re.search('CLEAR_ACTIONS', entry["actions"][0]) is not None):
                    # get match and send packet
                    self.checkDropRule(entry, pkt, sw)

                # is unicast
                else:
                    # get match and send packet
                     self.checkUnicastRule(entry, pkt, sw)



                self.packetGenTime = self.generateTime - self.starttime
                print ("PACKET GEN TIME: " , format(self.packetGenTime, '.5f'))

                # done testing?
                #self.isTesting = False

                # clean up
                #for sw in allSwitches:
                #    self.removeCatchRule(sw.dp)


    ### Frode Test
    def ramtinTest(self, msg, datapath, ofp, pkt, query):
        
        # Time the execution
       self.starttime = time.time()
       sw =self.dataPathsList.get(int(query["src"]))
       print("===============================================================================")
       print ("Testing switch: " , sw.dp.id)
  		#if sw.dp.id is 1:
  		# remove catch rule from self, if any
       self.removeCatchRuleByID(sw.dp.id)
       # Install catch rules on neighbours
       allNeighbours=self.getExpectedPathNeighbors(query["path"])
       for neigh in allNeighbours: # id
#           self.addCatchRuleByID(int(neigh.lstrip("0")))
           self.addCatchRuleByID(int(neigh,16))
       print("the neighbor: ",allNeighbours)
       self.addCatchRuleByID(int(query["dst"]))
       self.installCatchRuleTime=time.time()
  		# Scrape and sort flowtable
       ''' 
       flowtable = gather.getMatchData(sw.dp.id)
       flowtable = sorted(flowtable, key=generator.sortKey, reverse=True)
       '''
       self.generateTime = time.time()
       pkt = generator.makeCustomTestPacket(query["packet"],self.tos)
       '''
       # add packet to list
       entry["packet"] = {"ip" : pkt.get_protocol(ipv4.ipv4())}
       if entry["packet"]["ip"].proto is 6:
           entry["packet"]["tcp"] = pkt.get_protocol(tcp.tcp())
       elif entry["packet"]["ip"].proto is 17:
           entry["packet"]["udp"] = pkt.get_protocol(udp.udp())       	
  		# is total overlap?
       if pkt == -1:
  			# log and move on
           entry["totalOverlap"] = True
           self.totalOverlap += 1
  			# log some info about
  			# the entry & packet
           break # ?
  	
  		# is drop rule?
       if (len(entry["actions"]) is 0 or re.search('CLEAR_ACTIONS', entry["actions"][0]) is not None):
  		# get match and send packet
        self.checkDropRule(entry, pkt, sw)
  
  		# is unicast
       else:
  			# get match and send packet
           self.checkUnicastRule(entry, pkt, sw)
       '''
       self.newCheckUnicastRule(pkt, sw)
       self.packetGenTime = time.time() - self.generateTime #- self.starttime
       print ("PACKET GEN TIME: " , format(self.packetGenTime, '.5f'))
  	
  		# done testing?
  		#self.isTesting = False
  	
  		# clean up
  		#for sw in allSwitches:
  		#    self.removeCatchRule(sw.dp)
  	
  					

    #### DATAPATHS
    def getDatapathByID(self, dpid):
        """ Returns datapath object by ID """
        return api.get_datapath(self, dpid)

    def getAllDatapaths(self):
        """ Returns a list of all switch objects """
        switches = list()
        for i in get_all_switch(self):
            switches.append(i)
        return switches
    
    def getDataPaths(self):
        """ Returns a dict of all switch objects """
        switches = dict()
        for i in get_all_switch(self):
            switches[i.dp.id]=i
        return switches
        
        


    #### LINKS
    def getAllLinks(self):
        """ Get all link objects """
        links = list()
        for i in get_all_link(self):
            links.append(i)
        return links
    
    def getLinksByDatapathID(self, dpid):
        """ Get datapath links by object ID """
        #dp = self.getDatapathByID(dpid)
        #link = get_link(self, dp.id)
        link = get_link(self, dpid)
        return link


    #### NEIGHBOURHOOD
    def getNeighborsByID(self, dpid):
        """ Get list of datapath neighbor (IDs) """
        neigh = list()
        for link in self.getLinksByDatapathID(dpid):
            for k, v in link.to_dict().items():
                if k is 'dst':
                    neigh.append(v['dpid'])
        return neigh
    
    def getAllDatapathNeighbors(self):
        """ Get dict of all datapath neighbor (IDs) """
        allNeighbors = {}
        for d in self.getAllDatapaths():
            allNeighbors[d.dp.id] = self.getNeighborsByID(d.dp.id)
        return allNeighbors

    def getNeighborByPort(self, dpid, port):
        """ Get dpid from port number """
        for link in self.getLinksByDatapathID(dpid):
            if link.to_dict()["src"]["port_no"].lstrip("0") == str(port):
                return link.to_dict()["dst"]["dpid"].lstrip("0")

    def getExpectedPathNeighbors(self, expath):
        """expath format: ['1','2','3'] neighbor format: ['0000000000000001','0000000000000002','0000000000000003'] """
        neighbor=set()
        if type(expath) != 'set':
            path=set(expath)
        else:
            path=expath
        datapathNeighbors=self.getAllDatapathNeighbors()
        for sw in path:
            neighbor.update(datapathNeighbors.get(int(sw)))

        pathList=list(path)
        for i in range(len(pathList)):
            pathList[i]="0"*(len(list(neighbor)[0])-len(str(hex(int(pathList[i]))).split('x')[1])) + str(hex(int(pathList[i]))).split('x')[1] #convert expath foramt to neighbor format

        neighbor.difference_update(set(pathList))
        return neighbor


    #### CATCH RULES
    def addCatchRule(self, datapath, prio=None, ckie=None, prt=None):
        """ Install catch rule by datapath object """
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        priority = prio if prio is not None else 65500
        cookie = ckie if ckie is not None else 65500
        port = prt if prt is not None else ofp.OFPP_CONTROLLER
        buffer_id = ofp.OFP_NO_BUFFER
        match = ofp_parser.OFPMatch(eth_type = 2048, ip_dscp = 1)
        actions = [ofp_parser.OFPActionOutput(port)]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        req = ofp_parser.OFPFlowMod(datapath, cookie, 0, 0, ofp.OFPFC_ADD, 0, 0, priority, 
                    buffer_id, ofp.OFPP_ANY, ofp.OFPG_ANY, 0, match, inst)
        print ("\nADD CATCH RULE ON SWITCH: " , datapath.id , "\n" , req , "\n")
        datapath.send_msg(req)


    def addCatchRuleByID(self, dpid):
        """ Add catch rule by datapath ID """
        self.addCatchRule(self.getDatapathByID(dpid))
    

    def removeCatchRule(self, datapath, prio=None, ckie=None, prt=None):
        """ Remove catch rule """
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        priority = prio if prio is not None else 65500
        cookie = ckie if ckie is not None else 65500
        port = prt if prt is not None else ofp.OFPP_CONTROLLER
        buffer_id = ofp.OFP_NO_BUFFER
        match = ofp_parser.OFPMatch(eth_type = 2048, ip_dscp = 1)
        actions = [ofp_parser.OFPActionOutput(port)]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        req = ofp_parser.OFPFlowMod(datapath, cookie, 0, 0, ofp.OFPFC_DELETE, 0, 0, 
                                    priority, buffer_id,ofp.OFPP_ANY, ofp.OFPG_ANY,
                                    ofp.OFPFF_SEND_FLOW_REM, match, inst)
        print ("\nREMOVE CATCH RULE ON SWITCH: " , datapath.id , "\n" , req , "\n")
        datapath.send_msg(req)


    def removeCatchRuleByID(self, dpid):
        """ Remove catch rule by datapath ID """
        self.removeCatchRule(self.getDatapathByID(dpid))



    #### SEND OUT PACKET
    def sendPacket(self, datapath, pkt=None, in_port=None):
        """ Send packet by datapath object """
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        buffer_id = ofp.OFP_NO_BUFFER
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_TABLE)]
        pkt = pkt if pkt is not None else generator.makeTestPacket()

        # in port set or use ANY?
        if in_port is None or re.search('ANY', str(in_port)) is not None:
            in_port = ofp.OFPP_ANY

        req = ofp_parser.OFPPacketOut(datapath, buffer_id, in_port, actions, pkt)
        print ("\nPACKET OUT FROM SW " , datapath.id , " : " , req)
        datapath.send_msg(req)


    def sendPacketByID(self, dpid, pkt=None, in_port=None):
        """ Send test packet by datapath ID """
        self.sendPacket(self.getDatapathByID(dpid), pkt, in_port)



    #### RULE PARSING
    def checkDropRule(self, entry, pkt, sw):
        """ Check drop rule by rewriting the ft entry and probe the rule """

        # edge cases for prio # not testable
        if (int(entry["priority"]) is 65500 or int(entry["priority"]) is 0):
            return -1

        entry["isDrop"] = True

        # pick a random neighbour to (maybe) receive the probe
        dplink = self.getLinksByDatapathID(sw.dp.id)[0] # pick first port
        dpport = dplink.src.to_dict()["port_no"].lstrip("0")
        entry["neighbour"] = self.getNeighborByPort(sw.dp.id, dpport) # get neigh on link
        prio = int(entry["priority"])
        ckie = int(entry["cookie"])
        
        # choose port
        if "in_port" in entry.get("match", {}):
            port = entry["match"]["in_port"]
        else:
            port = "ANY"

        # append info
        entry["port"] = port
        entry["dpid"] = sw.dp.id

        # add catch rules above (cntrl) and below (neigh) target rule
        self.addCatchRule(sw.dp, prio+1, prio+1)
        self.addCatchRule(sw.dp, prio-1, prio-1, int(dpport))

        # send packet
        self.sendPacket(sw.dp, pkt, port)
        self.testingRules.append(entry)
        self.totalSent += 1

        # delete rules
        self.removeCatchRule(sw.dp, prio+1, prio+1)
        self.removeCatchRule(sw.dp, prio-1, prio-1, int(dpport))


    def checkUnicastRule(self, entry, pkt, sw):
        """ Probe unicast rule """

        entry["isDrop"] = False

        # ignore out to cntrl
        isOutput = re.search('OUTPUT', entry["actions"][0])
        isCntrl = re.search('CONTROLLER', entry["actions"][0])

        if isOutput is not None and isCntrl is None:
            entry["outport"] = entry["actions"][0].split(":",1)[1]
            entry["neighbour"] = self.getNeighborByPort(sw.dp.id, entry["outport"])
            entry["dpid"] = sw.dp.id

            # choose port
            if "in_port" in entry.get("match", {}):
                entry["in_port"] = entry["match"]["in_port"]
            else:
                entry["in_port"] = "ANY"

            # send out the probe
            self.sendPacket(sw.dp, pkt, entry["in_port"])
            self.testingRules.append(entry)
            self.totalSent += 1
    
    def newCheckUnicastRule(self, pkt, sw):
        """ Probe unicast rule """
        # send out the probe
        self.sendPacket(sw.dp, pkt, "ANY")        

    def compareMatchPacket(self, pkt):
        """ 
        Compare incoming packet with entries in dictlist.
        If no entry found, return -1
        """

        entry = ""
        # incoming probe, find target entry in list
        for rule in self.testingRules:
            
            # does layer 3 match?
            packetIP = pkt.get_protocol(ipv4.ipv4())
            ruleIP = rule["packet"]["ip"]
            if (ruleIP.src == packetIP.src and ruleIP.dst == packetIP.dst):
                
                # has layer 4, and is matching?
                if (ruleIP.proto != 0 and ruleIP.proto == packetIP.proto):
                    if ruleIP.proto is 6:
                        packetTCP = pkt.get_protocol(tcp.tcp())
                        ruleTCP = rule["packet"]["tcp"]
                        if (ruleTCP.src_port == packetTCP.src_port and 
                        ruleTCP.dst_port == packetTCP.dst_port):
                            index = self.testingRules.index(rule)
                            return self.testingRules.pop(index)

                    elif ruleIP.proto is 17:
                        udpPacket = pkt.get_protocol(udp.udp())
                        ruleUDP = rule["packet"]["udp"]
                        if (ruleUDP.src_port == udpPacket.src_port and
                        ruleUDP.dst_port == udpPacket.dst_port):
                            index = self.testingRules.index(rule)
                            return self.testingRules.pop(index)

                    # rule is L4, but not matching
                    print ("rule is L4, but not matching")
                    return -1
            index = self.testingRules.index(rule)
            return self.testingRules.pop(index)
        # no match found
        print ("no match found")
        return -1


    def loopcheck(self, pkt, dpid, entry):
        """ 
        Method for looping through flowtable, match packet and look at outport 
        - pull the flowtable from dpid
        - loop through and find match for pkt
        - if any match, loop is found
        - print the pkt and original entry
        """


        # scrape flowtable
        if dpid not in self.allFlowTables:
            flowtable = gather.getMatchData(dpid)
            flowtable = sorted(flowtable, key=generator.sortKey, reverse=True)
            self.allFlowTables[dpid] = flowtable
        
        # create packet from entry and compare with the incoming packet
        for field in self.allFlowTables[dpid]:
            fieldPacket = generator.packetFromMatch(field, self.allFlowTables[dpid])

            # proto matching? 
            if (pkt.get_protocol(ipv4.ipv4()).proto != 
            fieldPacket.get_protocol(ipv4.ipv4()).proto):
                continue

            # check layer 4
            fieldSport = ""
            fieldDport = ""

            if fieldPacket.get_protocol(tcp.tcp()) is not None:
                fieldSport = fieldPacket.get_protocol(tcp.tcp()).src_port
                fieldDport = fieldPacket.get_protocol(tcp.tcp()).dst_port
            elif fieldPacket.get_protocol(udp.udp()) is not None:
                fieldSport = fieldPacket.get_protocol(udp.udp()).src_port
                fieldDport = fieldPacket.get_protocol(udp.udp()).dst_port

            if "tp_src" in field["match"]:
                if fieldSport != field["match"]["tp_src"]:
                    continue
            elif "tp_dst" in field["match"]:
                if fieldDport != field["match"]["tp_src"]:
                    continue


            # check layer 3
            fieldSrcRange = ""
            fieldDstRange = ""

            if "nw_src" in field["match"]:
                fieldSrcRange = generator.addressToIPSet(field["match"]["nw_src"])
            if "nw_dst" in field["match"]:
                fieldDstRange = generator.addressToIPSet(field["match"]["nw_dst"])

            # check if packet resides in the fields IP range, if any
            pktSrcRange = netaddr.IPSet([pkt.get_protocol(ipv4.ipv4()).src])
            pktDstRange = netaddr.IPSet([pkt.get_protocol(ipv4.ipv4()).dst])

            overlap = [False, False]
            for i in fieldSrcRange:
                for k in pktSrcRange:
                    if i == k:
                        overlap[0] = True

            for i in fieldDstRange:
                for k in pktDstRange:
                    if i == k:
                        overlap[1] = True

            # if packet might match with the entry
            if overlap[0] is True or overlap[1] is True:
                isOutput = re.search('OUTPUT', field["actions"][0])
                isCntrl = re.search('CONTROLLER', field["actions"][0])
                if isOutput is not None and isCntrl is None:
                    # check neighbour on link
                    outport = field["actions"][0].split(":",1)[1]
                    neigh = self.getNeighborByPort(dpid, outport)
                    if neigh is None:
                        # not possible to determine
                        return 0

                    if int(neigh) == entry["dpid"]:
                        print ("LOOP FOUND FOR SWITCH " , dpid)
                        print ("PACKET: " , pkt)
                        #print ("FIELDPACKET: " , fieldPacket)
                        print ("ENTRY: " , field)
                        return 1
        # no loop, move to next
        return 0



    #### POPULATE WITH FAKE FLOWS
    def populateAllFlowtables(self):
        """ Populate all datapaths with fake flow table entries """
        for sw in self.getAllDatapaths():
            links = self.getLinksByDatapathID(sw.dp.id)
            for r in range(random.randint(3, 3)):
                sw.dp.send_msg(generator.makeRandomFlowMod(sw.dp, links))





'''
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        self.logger.info('OFPSwitchFeatures received: '
                         '\n\tdatapath_id=0x%016x n_buffers=%d '
                         '\n\tn_tables=%d auxiliary_id=%d '
                         '\n\tcapabilities=0x%08x',
                         msg.datapath_id, msg.n_buffers, msg.n_tables,
                         msg.auxiliary_id, msg.capabilities)

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    # We are not using this function
    def delete_flow(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for dst in self.mac_to_port[datapath.id].keys():
            match = parser.OFPMatch(eth_dst=dst)
            mod = parser.OFPFlowMod(
                datapath, command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                priority=1, match=match)
            datapath.send_msg(mod)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)



    def forwardingProcess(self,ev):
              if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # self.logger.info("\tpacket in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    ###################################################################################
    """
    The event EventSwitchEnter will trigger the activation of get_topology_data().
    """
    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        # The Function get_switch(self, None) outputs the list of switches.
        self.topo_raw_switches = copy.copy(get_switch(self, None))
        # The Function get_link(self, None) outputs the list of links.
        self.topo_raw_links = copy.copy(get_link(self, None))

        """
        Now you have saved the links and switches of the topo. So you could do all sort of stuf with them. 
        """

        print(" \t" + "Current Links:")
        for l in self.topo_raw_links:
            print (" \t\t" + str(l))

        print(" \t" + "Current Switches:")
        for s in self.topo_raw_switches:
            print (" \t\t" + str(s))

    """
    This event is fired when a switch leaves the topo. i.e. fails.
    """
    @set_ev_cls(event.EventSwitchLeave, [MAIN_DISPATCHER, CONFIG_DISPATCHER, DEAD_DISPATCHER])
    def handler_switch_leave(self, ev):
        self.logger.info("Not tracking Switches, switch leaved.")

'''        
