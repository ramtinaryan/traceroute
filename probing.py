# imports
import json


def getQueries():
    fileName = "/home/ramary/tracerout/query.json"
    listOfQueries = list()
    with open(fileName, 'r') as f:
        loaded_queries = json.load(f)

    for query in loaded_queries:
        listOfQueries.append(query)
    return listOfQueries
