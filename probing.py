# imports
import json


def getQueries():
	fileName="/home/ramary/ryu/ryu/app/query.json"
	listOfQueries=list()
	with open(fileName, 'r') as f:
	    loaded_queries = json.load(f)
	f.close()
	for query in loaded_queries:
		listOfQueries.append(query)
	return listOfQueries

