import json
import subprocess
import sys
import re
import os
import time

#These functions are used to encode a model into an LTS

def compute_elapsed_time(s_time):
    return time.time_ns() - s_time

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
    closure = set(pairs)
    while True:
        new_relations = set((x, w) for x, y in closure for q, w in closure if q == y)
        closure_until_now = closure | new_relations
        if closure_until_now == closure:
            break
        closure = closure_until_now
    return closure

def relation_to_function(pairs):
    res = {}
    for (a,b) in pairs:
        if a in res:
            res[a].add(b)
        else:
            res[a] = set([b])
    return lambda x: [] if x not in res else res[x]

import sys,os
input_file = sys.argv[1]
base_name = os.path.splitext(input_file)[0]

start_time = time.time_ns()

with open(f'{input_file}') as f:
    # Load the JSON data into a dictionary
    data = json.load(f)

d = uncover(data)

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


encoded=encode(uncover(data))

encode_time = compute_elapsed_time(start_time)
print("encode time:" + str(encode_time))

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

tomcrl2_time = compute_elapsed_time(encode_time)
print("To mcrl2 time: " + str(tomcrl2_time))

def run_command(command):
    subprocess.run(command, shell=True)

# generate the lps and get the lps pretty print
run_command(f"mcrl22lps --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm {base_name}.mcrl2 {base_name}.lps")
run_command(f"lpspp {base_name}.lps {base_name}2.lpspp")

tolps_time = compute_elapsed_time(tomcrl2_time)
print("To lps time: " + str(tolps_time))

states = [0 for i in range(0,len(data["points"]))]

# get the correspondence between the original states and the mcrl2 states
with open(f"{base_name}2.lpspp", "r") as infile:
    # print("reading")
    lines = infile.readlines()
    for i in range(0,len(lines)-1):
        no_whitespace = re.sub(r'\s', '', lines[i])
        if len(no_whitespace) > 0 and no_whitespace[0] == 's':
            next_no_whitespace = re.sub(r'\s', '', lines[i+1])
            states[int(no_whitespace[4])] = int(next_no_whitespace[-2])

    # print(states)
points = len(data["points"])

originalstates_time = compute_elapsed_time(tolps_time)
print("Get original states time: " + str(originalstates_time))

# now rename actions into tau and get the clean lps
run_command(f"lpsactionrename --regex=\"st1_[0-{points}]/tau\" {base_name}.lps {base_name}.lps")
run_command(f"lpspp {base_name}.lps {base_name}.lpspp")

renametau_time = compute_elapsed_time(originalstates_time)
print("Renaming time: " + str(renametau_time))

# transform the lps into an lts and minimise it
run_command(f"lps2lts {base_name}.lps {base_name}.lts")
run_command(f"ltsconvert -ebranching-bisim {base_name}.lts {base_name}_minimised.lts")

minimise_time = compute_elapsed_time(renametau_time)
print("Minimise time: " + str(minimise_time))

# now we get the ltsinfo and the correspondence between classes and original states
result = subprocess.run(f"ltsinfo -l {base_name}_minimised.lts", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) 
stderr_str = result.stderr

with open("ltsinfo.txt", 'wb') as infofile:
    infofile.write(stderr_str)

decoded_string = stderr_str.decode("utf-8")
no_white_decoded = re.sub(r'\s', '', decoded_string)
states_string = no_white_decoded.split("Thestatelabelsofthislabelledtransitionsystem:",1)[1]
# print(states_string)

string_pairs = re.sub(r':', '', states_string)

# print(string_pairs)

pairs = [(0,0) for i in range(0,points)]

for i in range(0, len(string_pairs)):
    if string_pairs[i] == '.' or string_pairs[i] == '(' or string_pairs[i] == ')':
        continue
    if string_pairs[i+1] == '(':
        # print(string_pairs[i])
        index = states.index(int(string_pairs[i+2]))
        pairs[index] = (int(string_pairs[i]), index)

# pairs contains now the pairs (class, original_state)
# print(pairs)

# get the correspondence between original states and atoms (don't know if this is needed)
color_state = [(0,"") for i in range(0,points)]
i=0

for elem in data["points"]:
    color_state[i] = (pairs[i][0], elem["atoms"])
    i = i+1

# print(color_state)

classes_with_duplicates = [i for (i,_) in pairs]
classes = list(dict.fromkeys(classes_with_duplicates))

# # print(classes)
jsonArrays = [ {"class" + str(i) : []} for i in range(0, len(classes)) ]

for i in range(0, len(classes)):
    for j in range(0, len(pairs)):
        if classes[i] == pairs[j][0]:
            jsonArrays[i]["class" + str(i)].append("true")
        else:
            jsonArrays[i]["class" + str(i)].append("false")

# print(jsonArrays)

finals = []

for i in range(0, len(jsonArrays)):
    with open("jsonOutput" + str(i) + ".json", 'w') as outjson:
        json.dump(jsonArrays[i], outjson, indent=2)