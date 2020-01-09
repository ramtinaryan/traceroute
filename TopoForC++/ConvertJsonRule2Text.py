import json

inputFileName = "SDNProbeTopo_25hop_1neighbor.json"
outputFileName = "SDNProbeTopo_25hop_1neighbor.txt"


def readRuleFile():
    OFEntriesList = list()
    with open(inputFileName, 'r') as f:
        OFEntries = json.load(f)

    if type(OFEntries) is dict:
        OFEntriesList.append(OFEntries)
    else:
        OFEntriesList = OFEntries
    return OFEntriesList


def generateRuleFile():
    """ Receive the list of rules in Json format. """
    """ Write the list on the output file with the Text format"""
    """ Text format: src_IP;mask;dst_IP;mask;dstPort;in_port;Action;"""
    ruleList = []
    OFList = readRuleFile()

    for rule in OFList:

        src_IP = rule['match']['nw_src'].split(
            '/')[0] if rule['match']['nw_src'] is not None else "*.*.*.*"
        src_IP_Mask = rule['match']['nw_src'].split(
            '/')[1] if rule['match']['nw_src'] is not None else "8"
        dst_IP = "*.*.*.*"
        dst_IP_Mask = "8"
        dstPort = "any"
        in_port = str(rule['match']['in_port']
                      ) if rule['match']['in_port'] is not None else "any"
        action = str(rule['actions'][0]['port']
                     ) if rule['actions'][0]['port'] is not None else "Drop"

        newRule = src_IP + ";" + src_IP_Mask + ";" + dst_IP + ";" + \
            dst_IP_Mask + ";" + dstPort + ";" + in_port + ";" + action + ";" + "\n"
        ruleList.append(newRule)
    with open(outputFileName, 'w') as f:
        for rule in ruleList:
            f.write(rule)


if __name__ == '__main__':
    generateRuleFile()
