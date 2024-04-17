import json
import argparse
import os
import regex as re

cli = argparse.ArgumentParser()
cli.add_argument("--classesDir")
cli.add_argument("--results",
                 default="result.json")

def readToolchainResults(jsonDir):
    fileList = []
    for jsonFile in os.listdir(jsonDir):
        with open(os.path.join(jsonDir,jsonFile)) as f:
            fileList.append(json.load(f))
    return fileList
    
def readCheckerResults(classesFile):
    with open(classesFile) as f:
        classesData = json.load(f)
        #print(classesData)
        return classesData
    
def computeOriginalResult(jsonFiles, classesFile):
    classesData = readToolchainResults(jsonFiles)
    resultsData = readCheckerResults(classesFile)
    def sortFunc(e):
        str = list(dict.fromkeys(e))[0]
        num = int(re.findall(r'\d+', str)[-1])
        return num
    classesData.sort(key=sortFunc)
    jsonArrays =[{ el : [] } for el in resultsData ]
    keys =  [el for el in resultsData]
    filename = "results/originalResult0.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    for k in range(0,len(resultsData)):
        formula = resultsData[keys[k]]
        trues = []
        for j in range(0, len(formula)):
            if formula[j]:
                trues.append(j)
        originalResults = [False for j in range(0,len(classesData[0]["class0"]))]
        for i in range(0,len(trues)):
            for j in range(0,len(originalResults)):
                originalResults[j] = originalResults[j] or (classesData[trues[i]]["class" + str(trues[i])])[j]
        jsonArrays[k][keys[k]] = originalResults
        with open("results/originalResult" + keys[k] + ".json", 'w') as outjson:
            json.dump(jsonArrays[k], outjson, indent=2)


args = cli.parse_args()
computeOriginalResult(args.classesDir, args.results)