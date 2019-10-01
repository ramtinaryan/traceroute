# imports
import json, requests, sys, re, random, generator

# vars
proto = "http://"
ctrl_ip = "0.0.0.0"
port = ":8080"

# OFCTL_REST
getDatapaths = "/stats/switches"
getFlowtables = "/stats/flow/"
removeEntries = "/stats/flowentry/clear/"

# REST_TOPOLOGY
getLinks = "/v1.0/topology/links"
allPorts = "/v1.0/topology/switches"


# REMOVE ALL TABLE ENTRIES
def removeAllEntries():
    """ Method for emptying out all flow table entries """
    for dpid in getAllDatapathID():
        url = proto + ctrl_ip + port + removeEntries
        url = url + str(dpid)
        try:
            req = requests.delete(url)
        except requests.exceptions.RequestException as e:
            print ("Server error %s " % e)
            return -1
    

# GET ALL DATAPATH IDs / SWITCH IDs
def getAllDatapathID():
    """ Get all datapath IDs (list of integers) """
    url = proto + ctrl_ip + port + getDatapaths
    try:
        req = requests.get(url)
        if req.status_code is 200:
            return json.loads(req.text)
    except requests.exceptions.RequestException as e:
        print ("Server error: %s" % e)


# GET FLOW TABLES
def getFlowtable(dpid=None):
    """ Method for getting each switch's flow table (json objects) """
    url = proto + ctrl_ip + port + getFlowtables
    if dpid is not None:
        url = url + str(dpid)
        try:
            req = requests.get(url)
            if req.status_code is 200:
                return json.loads(req.text)
        except requests.exceptions.RequestException as e:
            print ("Server error %s " % e)
    else:
        ftables = {}
        for dpid in getAllDatapathID():
            url = proto + ctrl_ip + port + getFlowtables + str(dpid)
            ftables[dpid] = getFlowtable(str(dpid))
        return ftables


# GET FLOW TABLE MATCH (as json/dict)
def getFlowtableMatch(dpid=None):
    """ Get match field from flow table """
    ftable = getFlowtable(dpid)
    if dpid is not None:
        entries = list()
        for entry in ftable[str(dpid)]:
            entries.append(entry["match"])
        return entries
    else:
        allEntries = {}
        for k, v in ftable.items():
            for a, b in v.items():
                entries = list()
                for entry in b:
                    entries.append(entry["match"])
                allEntries[k] = entries
        return allEntries


# GET ALL LINK PORTS
def getDatapathLinks(dpid=None):
    """ Get all connected ports on all switches """
    url = proto + ctrl_ip + port + getLinks
    if dpid is not None:
        if isinstance(dpid, int):
            dpid = str(dpid)
        if isinstance(dpid, str) and len(dpid) < 16:
            while len(dpid) < 16:
                dpid = "0" + dpid
        url = url + "/" + dpid
    try:
        req = requests.get(url)
        if req.status_code is 200:
            return json.loads(req.text)
    except requests.exceptions.RequestException as e:
        print ("Server error %s " % e)


# GET ALL PORTS
def getAllDatapathPorts(dpid=None):
    """ Get all switches and ports """
    url = proto + ctrl_ip + port + allPorts
    if dpid is not None:
        if isinstance(dpid, int):
            dpid = str(dpid)
        if isinstance(dpid, str) and len(dpid) < 16:
            while len(dpid) < 16:
                dpid = "0" + dpid
        url = url + "/" + dpid
    try:
        req = requests.get(url)
        if req.status_code is 200:
            return json.loads(req.text)
    except requests.exceptions.RequestException as e:
        print ("Server error %s " % e)


# GET MATCH DATA
def getMatchData(dpid=None):
    """ Extracts: prio, cookie, match and action & returns list of dicts """
    url = proto + ctrl_ip + port + getFlowtables
    table = []
    if dpid is not None:
        url = url + str(dpid)
        try:
            req = requests.get(url)
            if req.status_code is 200:
                req = json.loads(req.text)
                for k, v in req.items():
                    for line in v:
                        if "dl_type" in line["match"]:
                            if line["match"]["dl_type"] != 35020:
                                entry = {}
                                entry["priority"] = line["priority"]
                                entry["cookie"] = line["cookie"]
                                entry["actions"] = line["actions"]
                                entry["match"] = line["match"]
                                table.append(entry)
        except requests.exceptions.RequestException as e:
            print ("Server error %s " % e)
    else:
        raise NotImplementedError
    return table

