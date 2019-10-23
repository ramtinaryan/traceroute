# Mininet topology
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch
import json


class TopoGenerator(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)
        fileName = "topology.json"
        switchList = list()

        with open(fileName, 'r') as f:
            config = json.load(f)
        f.close()

        print(config["switch_No"])
        switch_No = config["switch_No"]
        for indx in range(1, switch_No + 1):            
            switch = self.addSwitch('sw%d' % (
                indx), protocols=["OpenFlow13"])
            host = self.addHost('h%d' % (indx))
            self.addLink(host, switch)
            switchList.append(switch)
        for link in config["links"]:
            nodes = link.split(':')
            self.addLink(switchList[int(nodes[0])-1],switchList[int(nodes[1])-1])            
topos = {
    'simple': TopoGenerator
}
