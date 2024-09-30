import json
import argparse
import os
import regex as re

cli = argparse.ArgumentParser()
cli.add_argument("--classesFile")
cli.add_argument("--experiment")
cli.add_argument("--results",
                 default="result.json")

def readResults(jsonFile):
    with open(jsonFile) as f:
        data = json.load(f)
        return data
    
def computeOriginalResult(classesFile, experiment, resultsFile):
    classesData = readResults(classesFile)
    resultsData = readResults(resultsFile)
    jsonDict = {}
    keys =  [el for el in resultsData]
    for el in keys:
        jsonDict[el] = []
    filename = "../experiments/" + experiment + "/results/originalResults.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    for k in range(0,len(resultsData)):
        formula = resultsData[keys[k]]
        trues = []
        for j in range(0, len(formula)):
            if formula[j]:
                trues.append(j)
        originalResults = [False for _ in range(0,len(classesData["class0"]))]
        for i in range(0,len(trues)):
            for j in range(0,len(originalResults)):
                originalResults[j] = originalResults[j] or (classesData["class" + str(trues[i])])[j]
        jsonDict[keys[k]] = originalResults
    with open("../experiments/" + experiment + "/results/originalResults.json", 'w') as outjson:
        json.dump(jsonDict, outjson, indent=2)


args = cli.parse_args()
computeOriginalResult(args.classesFile, args.experiment, args.results)