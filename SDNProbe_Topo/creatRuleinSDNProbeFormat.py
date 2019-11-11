#!/usr/bin/python

import random
import ipaddress
import netaddr
import re

outputFileName="SDNProbeTopo.txt"

def writetoFile(ruleList):
    with open(outputFileName, 'a') as f:
        for rule in ruleList:
            f.write(rule+'\n')
def drawRandomIPaddr(single=False):
    """
    Generate either single random IP address or range. High probability of
    small CIDR range, low probability for large range. RFC 1918 addresses.
    """
    draw = random.randint(0, 2)
    addr = ""

    if draw is 0:  # "class a"
        addr = "10"
        for i in range(3):
            addr += "." + str(random.randint(1, 254))
    elif draw is 1:  # "class b"
        addr = "172"
        addr += "." + str(random.randint(16, 31))
        for i in range(2):
            addr += "." + str(random.randint(1, 254))
    else:  # "class c"
        addr = "192.168"
        for i in range(2):
            addr += "." + str(random.randint(1, 254))

    if single:  # return if single addr
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
        addr += "/" + str(random.randint(26, 27))
    # 3 % for /22
    elif draw <= 81:
        addr += "/22"
    # 9 % for /28 and /29
    elif draw <= 90:
        addr += "/" + str(random.randint(28, 29))
    # 1 % for /20
    elif draw <= 91:
        addr += "/20"
    # 2 % for /21
    elif draw <= 93:
        addr += "/21"
    # 7 % for /30 and /31
    else:
        addr += "/" + str(random.randint(30, 31))

    return str(ipaddress.ip_interface(addr).network)


def IP2Bin(ipaddr):

    ip = ipaddr.split('/')[0]
    mask = '32'
    if '/' in ipaddr:
        mask = ipaddr.split('/')[1]

    binIp = "".join(map(str, ["{0:08b}".format(int(x))
                              for x in ip.split('/')[0].split(".")]))
    binIp = list(binIp)

    for i in range(int(mask) + 1, 33):
        binIp[i - 1] = 'x'
    binIp = "".join(binIp)

    return binIp


def generateRule(switch_id, portCount):
    ''' rule_id switch_id   ipaddress  bin_ipaddress in_port outport priority number'''
    portList = list(range(1, int(portCount) + 1))
    rule_id = random.randint(2100, 5530)
    in_port = random.choice(portList)
    outport = random.choice(portList)
    ip = drawRandomIPaddr(False)
    binIp = IP2Bin(ip)
    priority = random.randint(1000, 65000)
    lastItem = random.randint(2100, 5530)
    rule =str(rule_id)+" "+str(switch_id)+" "+str(ip)+" "+str(binIp)+" "+\
                    str(in_port)+" "+str(outport)+" "+str(priority)+" "+str(lastItem)
    
    return rule


def populateSwitch(switch_id, portCount, ruleCount):
    ruleList = list()
    ruleList.append(str(switch_id)+" "+str(ruleCount))
    for i in range(1, int(ruleCount)+1):
        ruleList.append(generateRule(switch_id, portCount))
    return ruleList

def topoRules(switchCount,portCount, ruleCount):
    for i in range(1,int(switchCount)+1):       
        writetoFile(populateSwitch(i,portCount,ruleCount))

    

if __name__ == '__main__':

    switchCount="5"
    portCount=4
    ruleCount=10
    topo="1 2 3 4 5\n2 1 3 4 5\n3 1 2 4 5\n4 1 2 3 5\n5 1 2 3 4 \n"
    with open(outputFileName, 'w') as f:
        f.write(switchCount+"\n")
        f.write(topo)
        
    topoRules(switchCount,portCount,ruleCount)

