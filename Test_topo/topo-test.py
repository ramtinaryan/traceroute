# Mininet topology
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch

class simple( Topo ):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        leftHost = self.addHost( 'h1' )
        leftSwitch = self.addSwitch( 's1', protocols=["OpenFlow13"] )

        topSwitch = self.addSwitch( 's2', protocols=["OpenFlow13"] )
        topHost = self.addHost( 'h2' )

        bottomSwitch = self.addSwitch( 's3', protocols=["OpenFlow13"] )
       	bottomHost = self.addHost( 'h3' )
        
        middleSwitch = self.addSwitch( 's4', protocols=["OpenFlow13"] )
       	middleHost = self.addHost( 'h4' )
	
        rightSwitch = self.addSwitch( 's5', protocols=["OpenFlow13"] )
       	rightHost = self.addHost( 'h5' )

        # Add host links
        self.addLink( leftHost , leftSwitch )
        self.addLink( topHost, topSwitch )
        self.addLink( bottomHost, bottomSwitch )
        self.addLink( rightHost, rightSwitch )
        self.addLink( middleHost, middleSwitch )
        self.addLink( leftSwitch , topSwitch )
        self.addLink( leftSwitch , bottomSwitch )
        self.addLink( leftSwitch , middleSwitch )
        self.addLink( topSwitch , middleSwitch )
        self.addLink( topSwitch , rightSwitch )
        self.addLink( bottomSwitch , rightSwitch )
        self.addLink( bottomSwitch , middleSwitch )
        self.addLink(rightSwitch, middleSwitch )


topos = {
    'simple': simple
}
