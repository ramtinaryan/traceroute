import json
import sys

outPutFileName = ""


def createTopo(path_length, neighbor_count, ctrIP, ctrPort, outputFile):
    """Create a Json file which is an input for the topo_generator.py """
    outPutFileName = outputFile
    ruleList = list()
    topo = {}
    topo['switch_No'] = path_length + (path_length * neighbor_count)
    topo['switchs'] = []
    topo['links'] = []
    topo['controller_IP'] = str(ctrIP)
    topo['controller_Port'] = ctrPort

    for node in range(1, path_length + 1):
        topo['switchs'].append(node)
        if node != path_length:
            link = str(node) + ":" + str(node + 1)
            topo['links'].append(link)

        for neighbor in range(1, neighbor_count + 1):
            link = str(node) + ":" + str(node) + str(neighbor) + "00"
            topo['links'].append(link)
            topo['switchs'].append(int(str(node) + str(neighbor) + "00"))

    with open(outPutFileName, 'w', newline='\n') as topoFile:
        json.dump(topo, topoFile, indent=3, separators=(',', ':'))


if __name__ == '__main__':
        if len(sys.argv) == 6:
     createTopo(int(sys.argv[1]), int(sys.argv[2]),
                str(sys.argv[3]), int(sys.argv[4]), str(sys.argv[5]))
     else:
     print("Wrong input !\n \
             Correct input format: path-length  neighbor  cnotroller_IP  controller_Port outputFile .\n \
             path-length:number of switches on the main path    neighbor: number of neighbor for each switch  controller_IP: controller IP address\
               controller_Port: controller port number  outputFile: address and name of the outputFile")

#    createTopo(10, 1, "158.36.99.24", 6623, "topology.json")
