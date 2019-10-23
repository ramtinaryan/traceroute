import json

fileName = "example_topology"
OFName = "openFlow_Format"

with open(fileName, "r") as f:
    lines = f.readlines()
    f.close()

rule = {}
ruleList = list()

for line in lines:
    fields = line.split()
    if len(fields) == 8:  # 0,1,2,4,5,6
        id = fields[0]
        sw = fields[1]
        ip = fields[2]
        inport = fields[4]
        outport = fields[5]
        priority = fields[6]
        rule['dpid'] = sw
        rule['priority'] = priority
        rule['cookie'] = 0
        rule['table_id'] = 0
        rule['match'] = {"in_port": inport,
                         "nw_src": ip}
        rule['actions'] = []
        rule['actions'].append({
            "type": "OUTPUT",
            "port": outport})
        ruleList.append(rule)
with open(OFName, 'w', newline='\n') as OFfile:
    json.dump(ruleList, OFfile, indent=2, separators=(',', ':'))
    OFfile.close()
