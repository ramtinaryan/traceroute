# Imports
import random, ipaddress, netaddr, re
from ryu.ofproto import ether
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, arp, tcp, udp
 

def drawRandomMac():
    """ Generate random MAC addresses """
    return "%02x:%02x:%02x:%02x:%02x:%02x" % ( random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255),random.randint(0, 255),
        random.randint(0, 255),random.randint(0, 255))


def drawRandomIPaddr(single=False):
    """ 
    Generate either single random IP address or range. High probability of 
    small CIDR range, low probability for large range. RFC 1918 addresses. 
    """
    draw = random.randint(0, 2)
    addr = ""

    if draw is 0: # "class a"
        addr = "10"
        for i in range(3):
            addr += "." + str(random.randint(1, 254))
    elif draw is 1: # "class b"
        addr = "172"
        addr += "." + str(random.randint(16, 31))
        for i in range(2):
            addr += "." + str(random.randint(1, 254))
    else: # "class c"
        addr = "192.168"
        for i in range(2):
            addr += "." + str(random.randint(1, 254))

    if single: # return if single addr
        return addr + "/32"

    draw = random.randint(1, 100)
    # 10 % for /32
    if draw <= 10:
        addr += "/32"
    # 35 % chance for a /24 subnet
    elif draw <= 45:
        addr += "/24"
    # 8 % chance for /23
    elif draw <= 53:
        addr += "/23"
    # 10 % for /25
    elif draw <= 63:
        addr += "/25"
    # 15 % for /26 or /27 
    elif draw <= 78:
        addr += "/"+ str(random.randint(26, 27))
    # 3 % for /22
    elif draw <= 81:
        addr += "/22"
    # 9 % for /28 and /29
    elif draw <= 90:
        addr += "/"+ str(random.randint(28, 29))
    # 1 % for /20
    elif draw <= 91:
        addr += "/20"
    # 2 % for /21
    elif draw <= 93:
        addr += "/21"
    # 7 % for /30 and /31
    else:
        addr += "/"+ str(random.randint(30, 31))

    return str(ipaddress.ip_interface(addr).network)


def drawRandomPort(known=True):
    """ Returns a well known pnum if known is true, else return pnum > 1023 """
    nums = [20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 123, 137, 138, 139, 
            143, 161, 162, 179, 389, 443, 465, 587, 993, 995, 989, 990]
    
    if known is True:
        return random.choice(nums)
    else:
        # mix of iana & linux ephemeral ports
        return random.randint(32768, 65535)


def makeCustomTestPacket(probePacket,tosValue):
    """ Generates a test probe with specific header values """
    pkt = packet.Packet()
    ip = ipv4.ipv4(tos=tosValue)
    src= probePacket["srcMac"] if probePacket["srcMac"] is not None else '00:00:de:ad:be:ef' 
    dst= probePacket["dstMac"] if probePacket["dstMac"] is not None else '00:00:de:ad:be:ef'
    eth = ethernet.ethernet(dst, src, ethertype=ether.ETH_TYPE_IP)
    pkt.add_protocol(eth)
    ip.src=probePacket["srcIp"] #if probePacket["srcIp"] is not None else "1.1.1.1"
    ip.dst=probePacket["dstIp"] #if probePacket["dstIp"] is not None else "2.2.2.2"
    pkt.add_protocol(ip)
    pkt.serialize()
    return pkt

def makeTestPacket():
    """ Generates a test probe with fake header values """
    pkt = packet.Packet()
    eth = ethernet.ethernet(dst='00:00:de:ad:be:ef', src='00:00:de:ad:be:ef', 
                            ethertype=ether.ETH_TYPE_IP)
    ip = ipv4.ipv4(src="1.1.1.1", dst = "2.2.2.2", tos=4)
    pkt.add_protocol(eth)
    pkt.add_protocol(ip)
    pkt.serialize()
    return pkt


def ddnToCidr(ip):
    """ Dotted decimal to CIDR """
    hasRange = re.match(".*/(.*)", ip) 
    if hasRange is None:
        return "/32"
    else:
        cidr = "/" + str(netaddr.IPAddress(hasRange.group(1)).netmask_bits())
        return cidr


def makeRandomFlowMod(datapath, links):
    """ Generate random fake OpenFlow FlowMod request """

    # ofp and args
    priority = random.randint(1, 65534)
    ofp = datapath.ofproto
    ofp_parser = datapath.ofproto_parser
    match = ofp_parser.OFPMatch()
    kwargs = {}

    # wildcard in_port or actual port
    portlist = list()
    for link in links:
        if "dpid" in link.to_dict()["src"]:
            if int(link.to_dict()["src"]["dpid"].lstrip("0")) is datapath.id:
                if "port_no" in link.to_dict()["src"]:
                    portlist.append(int(link.to_dict()["src"]["port_no"].lstrip("0")))
    
    if len(portlist) > 1:
        kwargs["in_port"] = random.choice(portlist)
    else:
        kwargs['in_port'] = ofp.OFPP_ANY

    # draw variations of the 5 tuple
    kwargs['eth_type'] = 0x0800 # add ip proto

    # layer 3 - every time
    draw = random.randint(1, 4)
    if draw is 1:
        kwargs['ipv4_src'] = drawRandomIPaddr()
        kwargs['ipv4_dst'] = drawRandomIPaddr("single")
    elif draw is 2:
        kwargs['ipv4_src'] = drawRandomIPaddr("single")
        kwargs['ipv4_dst'] = drawRandomIPaddr()
    elif draw is 3:
        kwargs['ipv4_src'] = drawRandomIPaddr("single")
        kwargs['ipv4_dst'] = drawRandomIPaddr("single")
    else:
        kwargs['ipv4_src'] = drawRandomIPaddr()
        kwargs['ipv4_dst'] = drawRandomIPaddr()

    # layer 4 - are we doing layer 4? 30 % of the time
    if random.randint(1, 100) <= 30:
        # 7 out of 10 is tcp
        if random.randint(1, 10) <= 7:
            kwargs['ip_proto'] = 6
            if random.randint(1, 2) is 1:
                kwargs["tcp_src"] = drawRandomPort()
                kwargs["tcp_dst"] = drawRandomPort(False)
            else:
                kwargs["tcp_src"] = drawRandomPort(False)
                kwargs["tcp_dst"] = drawRandomPort()
        # 3 out of 10 is udp
        else:
            kwargs['ip_proto'] = 17
            draw = random.randint(1, 3)
            if random.randint(1, 2) is 1:
                kwargs["udp_src"] = drawRandomPort()
                kwargs["udp_dst"] = drawRandomPort(False)
            else:
                kwargs["udp_src"] = drawRandomPort(False)
                kwargs["udp_dst"] = drawRandomPort()

    # pick a port
    draw = True
    while draw:
        pick = random.sample(portlist, 1)[0]
        if pick != kwargs["in_port"]:
            outport = pick
            draw = False

    # create OF objects
    match = ofp_parser.OFPMatch(**kwargs)
    actions = [ofp_parser.OFPActionOutput(outport)]
    inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
    req = ofp_parser.OFPFlowMod(datapath, 0, 0, 0, ofp.OFPFC_ADD, 0, 0, 
            priority, ofp.OFP_NO_BUFFER, ofp.OFPP_ANY, ofp.OFPG_ANY, 0, match, inst)

    # return
    return req


def addressToIPSet(ip):
    """ Takes ip addr in string format and returns IPSet object """
    hasRange = re.match(".*/(.*)" , ip)
    if hasRange is None:
        return netaddr.IPSet([ip+"/32"]) # no range, treat as single addr
    else:
        cidr = "/" + str(netaddr.IPAddress(hasRange.group(1)).netmask_bits())
        ip = re.sub('/(.*)' , cidr , ip)
        return netaddr.IPSet([ip])


def sortKey(dct):
    """ Sort list of dictionaries by key """
    return dct['priority']


def packetFromMatch(match=None, ftable=None):
    """ Make packet from match entry """

    # check object
    if match is None:
        print("match is None")
        return -1
    else:
        # build layer 2
        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(src = drawRandomMac(), 
            dst = drawRandomMac(), ethertype=ether.ETH_TYPE_IP))

        # remove lower prio ft entries and LLDP rules
        ftable = [x for x in ftable if x["priority"] > match["priority"] if x["match"]["dl_type"] != 35020]

        # extract 5-tuple values from match object
        matchSrcaddr = addressToIPSet(match["match"]["nw_src"]) if "nw_src" in match["match"] else None
        matchDstaddr = addressToIPSet(match["match"]["nw_dst"]) if "nw_dst" in match["match"] else None
        matchProto = match["match"]["nw_proto"] if "nw_proto" in match["match"] else None
        matchSport = match["match"]["tp_src"] if "tp_src" in match["match"] else None
        matchDport = match["match"]["tp_dst"] if "tp_dst" in match["match"] else None

        # declare
        ipheader = ipv4.ipv4(tos=4)
        tcpheader = tcp.tcp()
        udpheader = udp.udp()
        addresses = { "src" : [] , "dst" : [] }
        usedports = { "tcp" : [] , "udp" : [] }
        overlap = { "src" : False , "dst" : False }

        # LOOP compare entries descending
        for entry in ftable:

            ## check for differences; if any, break out

            # if in_port in both dicts && differs, move on
            if "in_port" in entry and "in_port" in match:
                if entry["match"]["in_port"] is not match["in_port"]:
                    break

            # if nw_proto differs, move on
            elif matchProto is not None and "nw_proto" in entry["match"]:
                if matchProto is entry["match"]["nw_proto"]:
                    break

            # if sport differs, move on
            elif "tp_src" in entry["match"] and entry["match"]["tp_src"] is not matchSport:
                if entry["match"]["nw_proto"] is 6:
                    usedports["tcp"].append(entry["match"]["tp_src"])
                else:
                    usedports["udp"].append(entry["match"]["tp_src"])
                break

            # if dport differs, move on
            elif "tp_dst" in entry["match"] and entry["match"]["tp_dst"] is not matchDport:
                if entry["match"]["nw_proto"] is 6:
                    usedports["tcp"].append(entry["match"]["tp_dst"])
                else:
                    usedports["udp"].append(entry["match"]["tp_dst"])
                break

            # done checking for differences
            # extract 5-tuple values from the entry to compare against
            entrySrcaddr = addressToIPSet(match["match"]["nw_src"]) if "nw_src" in entry["match"] else None
            entryDstaddr = addressToIPSet(entry["match"]["nw_dst"]) if "nw_dst" in entry["match"] else None
            entryProto = entry["match"]["nw_proto"] if "nw_proto" in entry["match"] else None
            entrySport = entry["match"]["tp_src"] if "tp_src" in entry["match"] else None
            entryDport = entry["match"]["tp_dst"] if "tp_dst" in entry["match"] else None

            # L3 - SOURCE ADDRESS MATCHING

            # total overlap after subtraction? add set to list
            if matchSrcaddr is not None and entrySrcaddr is not None:
                if len(matchSrcaddr - entrySrcaddr) <= 0:
                    overlap["srcaddr"] = True
                    addresses["src"].append(matchSrcaddr)
                # subtracting (possible) ipset portion
                matchSrcaddr -= entrySrcaddr

            # L3 - DESTINATION ADDRESS MATCHING

            # total overlap after subtraction? add set to list
            if matchDstaddr is not None and entryDstaddr is not None:
                if len(matchDstaddr - entryDstaddr) <= 0:
                    overlap["dstaddr"] = True
                    addresses["dst"].append(matchDstaddr)
                # subtracting (possible) ipset portion
                matchDstaddr -= entryDstaddr

        # DONE LOOPING

        # check for total shadowing
        if overlap["src"] is True and overlap["dst"] is True:
            return -1 # true

        # L3 - set fake addr if None is set
        if matchSrcaddr is None:
            #matchSrcaddr = drawRandomIPaddr(True) <--- sketchy
            matchSrcaddr = "1.1.1.1"
        else:
            # field is shadowed, pick last "good" range
            if len(matchSrcaddr) is 0:
                addr = list()
                for iprange in addresses["src"]:
                    for ip in iprange:
                        addr.append(ip.format())
                matchSrcaddr = random.choice(addr)
            else:
                # collect ip addresses and mask, could be multiple portions
                addr = list()
                for i in range(len(matchSrcaddr.iter_cidrs())):
                    for ip in matchSrcaddr.iter_cidrs()[i]:
                        addr.append(ip.format())
                matchSrcaddr = random.choice(addr)

        if matchDstaddr is None or len(matchDstaddr) is 0:
            #matchDstaddr = drawRandomIPaddr(True)
            matchDstaddr = "2.2.2.2"
        else:
            # field is shadowed, pick last "good" range
            if len(matchDstaddr) is 0:
                addr = list()
                for iprange in addresses["dst"]:
                    for ip in iprange:
                        addr.append(ip.format())
                matchDstaddr = random.choice(addr)
            else:
                # collect ip addresses and mask, could be multiple portions
                addr = list()
                for i in range(len(matchDstaddr.iter_cidrs())):
                    for ip in matchDstaddr.iter_cidrs()[i]:
                        addr.append(ip.format())
                matchDstaddr = random.choice(addr)

        # set values and add to header
        ipheader.src = matchSrcaddr
        ipheader.dst = matchDstaddr
        pkt.add_protocol(ipheader)


        # L4 check proto and set header value
        # tcp
        if matchProto is 6: 
            ipheader.proto = 6
            # src
            if matchSport is not None:
                tcpheader.src_port = matchSport
            else:
                # draw random value && is not in list of used port nums
                port = drawRandomPort()
                while port in usedports["tcp"]:
                    port = drawRandomPort() # draw new
                tcpheader.src_port = port
            # dst
            if matchDport is not None:
                tcpheader.dst_port = matchDport
            else:
                # draw random value && is not in list of used port nums
                port = drawRandomPort()
                while port in usedports["udp"]:
                    port = drawRandomPort() # draw new
                tcpheader.dst_port = port
            pkt.add_protocol(tcpheader) # adding header to packet

        # udp
        elif matchProto is 17:
            ipheader.proto = 17
            if matchSport is not None:
                udpheader.src_port = matchSport
            else:
                # draw random value && is not in list of used port nums
                port = drawRandomPort()
                while port in usedports:
                    port = drawRandomPort() # draw new
                tcpheader.src_port = port
            if matchDport is not None:
                udpheader.dst_port = matchDport
            else:
                # draw random value && is not in list of used port nums
                port = drawRandomPort()
                while port in usedports:
                    port = drawRandomPort() # draw new
                tcpheader.dst_port = port
            pkt.add_protocol(udpheader) # adding header to packet

        # serialize and send
        #print ("ENTRY: " , match , "\n")
        #print ("PACKET: " , pkt , "\n")
        pkt.serialize()
        return pkt

