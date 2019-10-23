#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController, Node
import json


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


class TopoGenerator(Topo):
    def __init__(self, netConfig):
        # Initialize topology
        Topo.__init__(self)
        switchList = list()
        switch_No = netConfig["switch_No"]
        for indx in range(1, switch_No + 1):
            switch = self.addSwitch('sw%d' % (
                indx), protocols=["OpenFlow13"])
            host = self.addHost('h%d' % (indx))
            self.addLink(host, switch)
            switchList.append(switch)
        for link in netConfig["links"]:
            nodes = link.split(':')
            self.addLink(switchList[int(nodes[0]) - 1],
                         switchList[int(nodes[1]) - 1])


if __name__ == '__main__':
    topos = {'topology': (lambda: TopoGenerator())}
    networkConfig = readConfig()
    topo = TopoGenerator(networkConfig)
    net = Mininet(topo=topo,
                  controller=lambda name: RemoteController(
                      name, ip=networkConfig["controller_IP"]),
                  listenPort=networkConfig["controller_Port"])

    net.start()
    # write_mn_status(1)
    CLI(net)
