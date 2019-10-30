#!/usr/bin/python
import json
import requests
import subprocess
import sys

# vars
proto = "http://"
ctrl_ip = "0.0.0.0"
port = ":8080"

# OFCTL_REST
getDatapaths = "/stats/switches"
getFlowtables = "/stats/flow/"
clearEntries = "/stats/flowentry/clear/"
addEntry = "/stats/flowentry/add"
removeEntry = "/stats/flowentry/delete_strict"
modifyEntry = "/stats/flowentry/modify_strict"

curlCommand = "curl -X POST -d '"
exeCommand = "/bin/bash   "

inputFileName = "openFlowEntries.json"
outputFileName = "output.sh"

switchId = 1


def readInputFile():
    OFEntriesList = list()
    with open(inputFileName, 'r') as f:
        OFEntries = json.load(f)
        f.close()
    if type(OFEntries) is dict:
        OFEntriesList.append(OFEntries)
    else:
        OFEntriesList = OFEntries
    return OFEntriesList

# GET ALL DATAPATH IDs / SWITCH IDs


def getAllDatapathID():
    """ Get all datapath IDs (list of integers) """
    url = proto + ctrl_ip + port + getDatapaths
    try:
        req = requests.get(url)
        if req.status_code is 200:
            return json.loads(req.text)
    except requests.exceptions.RequestException as e:
        print("Server error: %s" % e)


def addToFlowTable():
    print("Add the New Rule/s ...")
    OFEntries = readInputFile()
    url = "' " + proto + ctrl_ip + port + addEntry
    for p in OFEntries:
        with open(outputFileName, "a+") as f:
            f.write(curlCommand + "\n")
            f.close()
        with open(outputFileName, 'a', newline='\n') as OFfile:
            json.dump(p, OFfile, indent=2, separators=(',', ':'))
            OFfile.close()
        with open(outputFileName, "a") as f:
            f.write(url + "\n")
            f.close()
    process = subprocess.Popen(exeCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is None:
        print("Adding is Finished Successfully!")
    else:
        print("Adding is NOT Completed!")


def removeFromFlowTable():
    print("Remove from the Flowtable ...")
    OFEntries = readInputFile()
    url = "' " + proto + ctrl_ip + port + removeEntry
    for p in OFEntries:
        with open(outputFileName, "a+") as f:
            f.write(curlCommand + "\n")
            f.close()
        with open(outputFileName, 'a', newline='\n') as OFfile:
            json.dump(p, OFfile, indent=2, separators=(',', ':'))
            OFfile.close()
        with open(outputFileName, "a") as f:
            f.write(url + "\n")
            f.close()
    process = subprocess.Popen(exeCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is None:
        print("Removing is Finished Successfully!")
    else:
        print("Removing is NOT Completed!")


def modifyFlowTable():
    print("Modify the Flowtable ...")
    OFEntries = readInputFile()
    url = "' " + proto + ctrl_ip + port + modifyEntry
    for p in OFEntries:
        with open(outputFileName, "a+") as f:
            f.write(curlCommand + "\n")
            f.close()
        with open(outputFileName, 'a', newline='\n') as OFfile:
            json.dump(p, OFfile, indent=2, separators=(',', ':'))
            OFfile.close()
        with open(outputFileName, "a") as f:
            f.write(url + "\n")
            f.close()
    process = subprocess.Popen(exeCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error is None:
        print("Modifying is Finished Successfully!")
    else:
        print("Modifying is NOT Completed!")


def clearFlowTable():
    print("Clear the Flowtable of Switch %s ..." % (switchId))
    url = proto + ctrl_ip + port + clearEntries + switchId
    try:
        req = requests.delete(url)
    except requests.exceptions.RequestException as e:
        print("Server error %s " % e)
        return -1
    print("Cleaning is Finished Successfully!")


def clearAllFlowTables():
    for dpid in getAllDatapathID():
        print("Clear the Flowtable of Switch %d ..." % (dpid))
        url = proto + ctrl_ip + port + clearEntries
        url = url + str(dpid)
        try:
            req = requests.delete(url)
        except requests.exceptions.RequestException as e:
            print("Server error %s " % e)
            return -1
        print("Cleaning is Finished Successfully!")

# def operations(option):


def operations(optionList):
    if optionList[1] == '-a':
        addToFlowTable()
    elif optionList[1] == '-r':
        removeFromFlowTable()
    elif optionList[1] == '-m':
        modifyFlowTable()
    elif optionList[1] == '-c':
        if optionList[2] == 'all':
            clearAllFlowTables()
        else:
            switchId = str(optionList[2])
            clearFlowTable()
    else:
        print("Wrong input !\n \
            Correct input format: operatoin [inputfile].\n \
            operatoin: '-a': add, '-r': remove, '-m': modify, '-c id [no inputfile]':clean flow table in sw_id, 'c all [no inputfile]': clean all flow tables")


if __name__ == '__main__':
    '''Clean the output file'''
    with open(outputFileName, "w") as f:
        f.close()
    optionList = sys.argv
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        inputFileName = str(sys.argv[len(sys.argv) - 1])
        exeCommand = exeCommand + outputFileName
        operations(optionList)
    else:
        print("Wrong input !\n \
            Correct input format: operatoin [inputfile].\n \
            operatoin: '-a': add [inputfile], '-r': remove [inputfile], '-m': modify [inputfile], '-c id [no inputfile]':clean flow table in sw_id, 'c all [no inputfile]': clean all flow tables")
