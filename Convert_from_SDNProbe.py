import json

fileName = "example_topology"
OFName = "openFlow_Format"
f = open(fileName, "r")
lines = f.readlines()
f.close()
rule = {}
for line in lines:
    fields = line.split()
    if len(fields) == 8:  # 0,1,2,4,5,6
        id = fields[0]
        sw = fields[1]
        ip = fields[2]
        inport = fields[4]
        outport = fields[5]
        priority = fields[6]
        rule['dpid'] = id
        rule['priority'] = priority
        rule['cookie'] = 0
        rule['table_id'] = 0
        rule['match'] = {"in_port": inport,
                         "nw_src": ip}
        rule['actions'] = []
        rule['actions'].append({
            "type": "OUTPUT",
            "port": outport})
        with open(OFName, 'a') as OFfile:
            json.dump(rule, OFfile)
