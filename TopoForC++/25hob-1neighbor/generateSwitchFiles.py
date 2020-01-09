
inputFileName = "SDNProbeTopo_25hop_1neighbor.txt"


def readRuleFile():
    lines = []
    with open(inputFileName, 'r') as f:
        for line in f:
            lines.append(line)

    return lines


def writeFile(filename, ruleList):
    with open(filename, 'w') as f:
        for rule in ruleList:
            f.write(rule)


def generateSwitchFiles():
    """ Receive the list of rules in text format. """
    """ generate switch files with the spicific number of rules"""

    rules = readRuleFile()
    ruleList = []
    switchRulesNumber = 50
    ruleNumber = 1
    switchCounter = 1
    print("number of rules:", len(rules))
    for rule in rules:
        if ruleNumber < switchRulesNumber:
            ruleList.append(rule)
            ruleNumber = ruleNumber + 1
        else:
            ruleList.append(rule)
            filename = "SW_" + str(switchCounter) + ".txt"
            print("filename is :", filename)
            writeFile(filename, ruleList)
            ruleList.clear()
            switchCounter = switchCounter + 1
            ruleNumber = 1


if __name__ == '__main__':
    generateSwitchFiles()
