#!/usr/bin/env python3


#%%

# Date: 2023/12/14
# Mieke (adapted from older version by Vincenzo)
# Improving on encodermm_enc_eta_clean.py

# Implements Vincenzo's proposal for encoding w.r.t. the eta-operator propsed in Tbilisi Oct 2023
# Uses different action labels: "a" -> "chg" and "b" -> "dwn"

# NOTE: This version is specific for the MAZE example as it reduces the number of 
# tau-transitions for cells that are part of a monochromatic upset (such as in the 
# "rooms" of a maze). See line "if (point,dest) in set(uncovered["up"]): "
# In general this cannot be done as it could generate too few tau-transitions!!!!

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
    return {   
        "atoms": [ "ap_" + atom for atom in uncovered["atoms"] ] + ["tau","chg","dwn"],
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