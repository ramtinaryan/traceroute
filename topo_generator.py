#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController, Node
import json
import sys

fileName = "topology.json"
"""
                    File Format:
                "switch_No":4,
                "links":["1:2","1:3","2:4","3:4"],
                "controller_IP":"158.36.99.24",
                "controller_Port":6633

"""


def readConfig():
    with open(fileName, 'r') as f:
        config = json.load(f)
        f.close()
    return config


def int2dpid(dpid):
    try:
        dpid = hex(dpid)[2:]
        dpid = '0' * (16 - len(dpid)) + dpid
        return dpid
    except IndexError:
        raise Exception('Unable to derive default datapath ID - '
                        'please either specify a dpid or use a '
                        'canonical switch name such as s23.')


class TopoGenerator(Topo):
    def __init__(self, netConfig):
        # Initialize topology
        Topo.__init__(self)
        switchList = dict()
        switch_No = netConfig["switch_No"]
        for indx in netConfig["switchs"]:
            switch = self.addSwitch('sw%d' % (
                indx), dpid=int2dpid(indx), protocols=["OpenFlow13"])
            host = self.addHost('h%d' % (indx))
            self.addLink(host, switch)
            switchList[str(indx)] = 'sw' + str(indx)
        for link in netConfig["links"]:
            nodes = link.split(':')
            self.addLink(switchList.get(nodes[0]), switchList.get(nodes[1]))


if __name__ == '__main__':
    topos = {'topology': (lambda: TopoGenerator())}
    if len(sys.argv) == 2:
        fileName = str(sys.argv[1])
    print("fileName: ", fileName)
    networkConfig = readConfig()
    topo = TopoGenerator(networkConfig)
    net = Mininet(topo=topo,
                  controller=lambda name: RemoteController(
                      name, ip=networkConfig["controller_IP"]),
                  listenPort=networkConfig["controller_Port"])

    net.start()
    # write_mn_status(1)
    CLI(net)
