import json

fileName = "example_topology"
OFName = "openFlowEntries.json"

with open(fileName, "r") as f:
    lines = f.readlines()

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
        rule = {}
        rule['dpid'] = int(sw) + 1
        rule['priority'] = int(priority)
        rule['cookie'] = 0
        rule['table_id'] = 0
        rule['match'] = {"in_port": int(inport),
                         "nw_src": ip,
                         "dl_type": 2048}
        rule['actions'] = []
        rule['actions'].append({
            "type": "OUTPUT",
            "port": int(outport)})
        ruleList.append(rule)
with open(OFName, 'w', newline='\n') as OFfile:
    json.dump(ruleList, OFfile, indent=2, separators=(',', ':'))
