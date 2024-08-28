#!/usr/bin/env python3


#%%

# Date: 2024/08/27
# Mieke (adapted from older version by Vincenzo)
# Encoding for SLCS with gamma and reverse closure as in Note by Diego
# on "Gamma revisited"

import json
    

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
                
            if (point,dest) in set(uncovered["up"]):      
                    label="dir"
                    tss.add(((1,point),(label,(1,dest))))
            else:
                    label="cnv"
                    tss.add(((1,point),(label,(1,dest))))
                        
        for atom in uncovered["valuation"][point]:
            tss.add(((tag,point),("ap_"+atom,(tag,point))))
            tss.add(((tag,point),("dir",(tag,point))))
            tss.add(((tag,point),("cnv",(tag,point))))
    return {   
        "atoms": [ "ap_" + atom for atom in uncovered["atoms"] ] + ["dir","cnv"],
        "states": all,
        "transitions": list(tss)
    }


encoded=encode(uncover(data))

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


#%%