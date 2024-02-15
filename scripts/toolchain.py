#!/usr/bin/env python3

import json
import subprocess
import sys
import re
import os
import time

import resource
import networkx as nx
import pandas as ps

#Utilities
resource.setrlimit(resource.RLIMIT_STACK, (100000000,100000000))

def run_command(command):
    subprocess.run(command, shell=True)

def init_time():
    global last_time
    last_time = time.time()

def update_time():
    global last_time
    tmp = last_time
    last_time = time.time()
    return last_time - tmp

def poset2mcrl2(args):
    data = args["data"]
    base_name = args["base_name"]
    #These functions are used to encode a model into an LTS
    def uncover(data):
        up = set()
        points = set()
        valuation = {}
        atoms = set()    
        for point in data['points']:
            points.add(point["id"])
            valuation[point["id"]] = sorted(point["atoms"])
            for atom in point["atoms"]:
                atoms.add(atom)        
            for up_id in point['up']:
                up.add((point['id'], up_id))
                points.add(up_id)
        return {
            "atoms": atoms,
            "valuation": valuation,
            "points": points,
            "up": up
        }

    def transitive_closure(pairs):    
        dg = nx.DiGraph(pairs)
        tc = nx.transitive_closure_dag(dg)
        return tc.edges()
        
    def relation_to_function(pairs):
        res = {}
        for (a,b) in pairs:
            if a in res:
                res[a].add(b)
            else:
                res[a] = set([b])
        return lambda x: [] if x not in res else res[x]

    def encode(uncovered):
        ss = [(1,p) for p in uncovered["points"]]
        # Mieke added sorting of LTS states in next line  (2023/06/07)  
        all = sorted(ss)
        tc = transitive_closure(uncovered["up"])    
        fn = relation_to_function(tc)
        tss = set()
        
        for (tag,point) in all:                
                
            for dest in fn(point):
    # MKE: here one could first check whether point and dest are just one step in face relation apart
    # and only in that case add the tau-transitions
                if uncovered["valuation"][dest] == uncovered["valuation"][point]: 
                    # The following line is only justified if it is sure that the
                    # point is in a monochromatic upset!!!
                    if (point,dest) in set(uncovered["up"]):      
                        label="tau"
                        tss.add(((1,point),(label,(1,dest))))
                        tss.add(((1,dest),(label,(1,point))))
    #                    label="a"
    #                    tss.add(((1,point),(label,(1,dest))))
    #                    tss.add(((1,dest),(label,(1,point))))
                else:
                        label="chg"
                        tss.add(((1,point),(label,(1,dest))))
                        tss.add(((1,dest),(label,(1,point))))
                        tss.add(((1,dest),("dwn",(1,point))))
    
            for atom in uncovered["valuation"][point]:
                tss.add(((tag,point),("ap_"+atom,(tag,point))))
            # add a self loop using the name of the state as an action
            # this will be renamed into tau later
            tss.add(((tag, point), ("st1_"+point,(tag,point))))
        return {   
            "atoms": [ "ap_" + atom for atom in uncovered["atoms"] ] + ["tau","chg","dwn"] + [ "st1_"+point for (tag,point) in all],
            "states": all,
            "transitions": list(tss)
        }

    print("parsing...")
    uncovered=uncover(data)
    print("parse time:" + str(update_time()))
    print("encoding...")
    encoded=encode(uncovered)
    print("encode time:" + str(update_time()))

    print("saving to mcrl2...")

    def name_state(state):
        match state:
            case (tag,id):
                return f"t{tag}_{id}"

    import itertools

    def intersperse(iterable, elem):
        return list(itertools.chain.from_iterable(zip(iterable, itertools.repeat(elem))))[:-1]

    def notau(act):
        if act == "tau": return False
        return True 

    with open(f"{base_name}.mcrl2", "w") as outfile:
        fn=relation_to_function(encoded["transitions"])
        outfile.write("act\n    ")

        for a in intersperse(filter(notau,encoded["atoms"]),","):
                outfile.write(a)       
        outfile.write(";")
        outfile.write("\n\nproc\n")
        for source in encoded["states"]:                
            name=name_state(source)
            def fn1(x):
                match x:
                    case(a,b):
                        return f"{a}.{name_state(b)}"        
            outfile.write(f"\n{name} = \n    ")           
            ts=map(fn1,fn(source))
            ts1=intersperse(ts," + ")
            for x in ts1:
                outfile.write(x)
            outfile.write(";")
        outfile.write(f"\n\ninit\n\n{name_state(encoded['states'][0])};")    

def poly2poset(args):
    run_command(f"../../scripts/PolyPoProject/bin/Debug/net8.0/PolyPoProject " + args["poly"] + " " + args["poset"])

def cached_execute(filename, name, fn, args):
    if os.path.exists(filename):
        print("file " + filename + " already exists")
    else:
        fn(args)

### THE GLOBAL SCRIPT STARTS HERE

import sys,os
input_file = sys.argv[1] #this is base_name.json
base_name = os.path.splitext(input_file)[0]

if not base_name.split('_')[-1] == "Poset":
    print("here")
    base_name = base_name + "_Poset"
    cached_execute(base_name + ".json", base_name + ".json", poly2poset, { "poly" : input_file, "poset" : base_name + ".json"})
poset_file = base_name + f".json"

init_time()
times = {}

with open(f'{poset_file}') as f:
    # Load the JSON data into a dictionary
    data = json.load(f)

print(base_name)

cached_execute(base_name + ".mcrl2", base_name + ".mcrl2", poset2mcrl2, {"data" : data, "base_name" : base_name})
now = update_time()
times["To mcrl2"] = [now]
print("To mcrl2 time: " + str(now))
print(times)
psTimes = ps.DataFrame(times)
jsonTime = psTimes.to_json()
print(jsonTime)

print("converting to lps...")

# generate the lps and get the lps pretty print
# NOTE: this files must always be recreated, as they are computed twice with different actions.
# Therefore, an existing lps file is different than the one created here, that is needed to retrieve original states
run_command(f"mcrl22lps --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm " + base_name + ".mcrl2 " + base_name + ".lps")
run_command(f"lpspp {base_name}.lps {base_name}.lpspp")

print("To lps time: " + str(update_time()))

print("finding original states...")
# create a list of zeroes: zeroes will be replaced with the corresponding
# state of the mcrl2 model: the index of the original state will contain the corresponding mmcrl2 state
states = [0 for i in range(0,len(data["points"]))]

# get the correspondence between the original states and the mcrl2 states
with open(f"{base_name}.lpspp", "r") as infile:
    # read the lps pretty print file lines
    lines = infile.readlines()
    for i in range(0,len(lines)-1):
        # clean whitespaces
        no_whitespace = re.sub(r'\s', '', lines[i])
        # if the line starts with s, it is the fake label named as the original state
        if len(no_whitespace) > 0 and no_whitespace[0] == 's':
            # the required index is the final part of the string
            num_str = no_whitespace[4:-1]
            # remove whitespaces from the following line
            next_no_whitespace = re.sub(r'\s', '', lines[i+1])
            # convert the final part of the string to int and place it in the list of states
            states[int(num_str)] = int(next_no_whitespace[10:-1])

points = len(data["points"])

print("Get original states time: " + str(update_time()))
print("renaming...")
# now rename actions into tau and get the clean lps
run_command(f"lpsactionrename --regex=\"st1_[0-{points}]/tau\" {base_name}.lps {base_name}.lps")
run_command(f"lpspp {base_name}.lps {base_name}.lpspp")

print("Renaming time: " + str(update_time()))
print("converting to lts...")
# transform the lps into an lts and minimise it
run_command(f"lps2lts --threads=32 {base_name}.lps {base_name}.lts")
print("convert time: " + str(update_time()))

print("minimizing....")
run_command(f"ltsconvert -ebranching-bisim {base_name}.lts ./{base_name}_minimised.lts")

print("Minimise time: " + str(update_time()))
print("converting to visualizer format...")
# now we get the ltsinfo and the correspondence between classes and original states
result = subprocess.run(f"ltsinfo -l {base_name}_minimised.lts", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) 
stderr_str = result.stderr

# parse ltsinfo.txt and decode it
with open("ltsinfo.txt", 'wb') as infofile:
    infofile.write(stderr_str)

decoded_string = stderr_str.decode("utf-8")
# remove whitespaces
no_white_decoded = re.sub(r'\s', '', decoded_string)
# get the final part of the string, containing pairs (class, state)
states_string = no_white_decoded.split("Thestatelabelsofthislabelledtransitionsystem:",1)[1]

# remove colons
string_pairs = re.sub(r':', '', states_string)

pairs = [(0,0) for i in range(0,points)]

# split the string in such a way that we get a list of strings ".class(state"
string_list = string_pairs.split(')')
# last string is a semicolon
string_list = string_list[:-1]
for i in range(0, len(string_list)):
    # remove periods from strings
    string_list[i] = re.sub(r'\.', '', string_list[i])
    # split strings to separate classes and states
    splitted = string_list[i].split('(')
    # now assign classes to the original states
    index = states.index(int(splitted[1]))
    pairs[index] = (int(splitted[0]), index)

# get the correspondence between original states and atoms (don't know if this is needed)
color_state = [(0,"") for i in range(0,points)]
i=0

for elem in data["points"]:
    color_state[i] = (pairs[i][0], elem["atoms"])
    i = i+1

classes_with_duplicates = [i for (i,_) in pairs]
classes = list(dict.fromkeys(classes_with_duplicates))

jsonArrays = [ {"class" + str(i) : []} for i in range(0, len(classes)) ]

for i in range(0, len(classes)):
    for j in range(0, len(pairs)):
        if classes[i] == pairs[j][0]:
            jsonArrays[i]["class" + str(i)].append("true")
        else:
            jsonArrays[i]["class" + str(i)].append("false")

for i in range(0, len(jsonArrays)):
    with open("jsonOutput" + str(i) + ".json", 'w') as outjson:
        json.dump(jsonArrays[i], outjson, indent=2)

print("Conversion time: " + str(update_time()))
