#!/usr/bin/env python3

#%%
# converting to lps...
# ^B^BSegmentation fault (core dumped)
# mcrl2lps time: 14168.65964460373

# TODO: NECESSARY: switch to an execution function that accepts an array of arguments

print("started")


import json
import subprocess
import sys
import re
import os
import time

import resource
import networkx as nx
import pandas as ps

# Utilities
resource.setrlimit(resource.RLIMIT_STACK, (500000000, 500000000))


def run_command(command):
    print(f"Running command: {command}")
    subprocess.run(command, shell=True)

# def init_time():
#     global last_time
#     last_time = time.time()

# def update_time():
#     global last_time
#     tmp = last_time
#     last_time = time.time()
#     return last_time - tmp


times = ({})


def loadData(args):
    with open(args["poset"]) as f:
        # Load the JSON data into a dictionary
        args["data"] = json.load(f)
        print(len(args["data"]["points"]))


def poset2mcrl2(args):
    data = args["data"]
    # These functions are used to encode a model into an LTS

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

    def encode(uncovered):
        print("interpreting data...")
        # Mieke added sorting of LTS states in next line  (2023/06/07)
        # VC: why?
        dg = nx.DiGraph(uncovered["up"])
        tc = nx.transitive_closure(dg)

        print("-- actual encoding starts here --")
        v = uncovered["valuation"]

        result = nx.MultiDiGraph()
        atoms = set(["ap_" + atom for atom in uncovered["atoms"]] +
                    ["tau", "chg", "dwn"])
        
        for point in tc.nodes:
            for atom in uncovered["valuation"][point]:
                result.add_edge(point, point, label="ap_"+atom)  
            # add a self loop using the name of the state as an action
            # this will be renamed into tau later
            stlabel = "st1_"+point
            result.add_edge(point, point, label=stlabel)
            result.add_edge(point, point, label="dwn")
            atoms.add(stlabel)

        for (point, dest) in tc.edges():
            # MKE: here one could first check whether point and dest are just one step in face relation apart
            # and only in that case add the tau-transitions
            # VINCENZO: is this what is done by the following if?
            # VINCENZO: could this be done separately on the non-transitively-closed graph for efficiency?
            if v[dest] == v[point]:
                # The following line is only justified if it is sure that the
                # point is in a monochromatic upset!!!
                # TODO: URGENT: VC: I do not understand this line at all
                if dg.has_edge(point, dest):
                    label = "tau"
                    result.add_edge(point, dest, label=label)
                    result.add_edge(dest, point, label=label)                    
            else:
                label = "chg"
                result.add_edge(point, dest, label=label)
                result.add_edge(dest, point, label=label)
                result.add_edge(dest, point, label="dwn")

        return {
            "atoms": atoms,
            "lts": result,
            "tc": tc 
        }

    print("parsing...")
    uncovered = uncover(data)
    print("encoding...")
    encoded = encode(uncovered)

    print("saving to mcrl2...")

    base_name = args["base_name"]
    output_dir = args["output_dir"]

    def name_state(state):
        return f"t1_{state}"

    import itertools

    def intersperse(iterable, elem):
        return list(itertools.chain.from_iterable(zip(iterable, itertools.repeat(elem))))[:-1]

    def notau(act):
        return act != "tau"

    with open(f"{output_dir}/{base_name}.mcrl2", "w") as outfile:
        # fn=relation_to_function(encoded["transitions"])
        outfile.write("act\n    ")

        for a in intersperse(filter(notau, encoded["atoms"]), ","):
            outfile.write(a)
        outfile.write(";")
        outfile.write("\n\nproc\n")
        lts = encoded["lts"]
        for source in lts.nodes:
            name = name_state(source)

            def fn1(x):
                match x:
                    case(a, b):
                        return f"{a}.{name_state(b)}"
            outfile.write(f"\n{name} = \n    ")
            ts = []
            for (dest, labels) in lts.adj[source].items():
                for (key,data) in labels.items():
                    ts.append(fn1((data["label"], dest)))

            ts1 = intersperse(ts, " + ") 
            for x in ts1:
                outfile.write(x)
            outfile.write(";")
        # VC: TODO: URGENT: is the initial state always 0?
        outfile.write(f"\n\ninit\n\n{name_state(0)};")
    return encoded


def poly2poset(args): #TODO: switch to the release version of PolyPo (not Debug) and also compile it if not present
    run_command(f"../../scripts/PolyPoProject/bin/Debug/net8.0/PolyPoProject " +
                args["poly"] + " " + args["poset"])


def mcrl2lps(args):
    print("converting to lps...")
    #run_command(f"mcrl22lps -rjittyc --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm " +
    #            args["mcrl2"] + " " + args["lps"])
    run_command(f"mcrl22lps --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm " +
                args["mcrl2"] + " " + args["lps"])

def lps2lpspp(args):
    run_command("lpspp " + args["lps"] + " " + args["lpspp"])

def renamelps(args):
    print("renaming...")
    cmd = "lpsactionrename --regex=\"st1_[0-9]+/tau\" " + args["base"] + " " + args["renamed"]
    run_command(cmd)    

def findStates(args):
    print("finding original states...")
    states = [i for i in range(0, args["points"] + 1)]
    with open(args["base"], "r") as infile:
        # read the lps pretty print file lines
        lines = infile.readlines()
        for i in range(0, len(lines)-1):
            # clean whitespaces
            no_whitespace = re.sub(r'\s', '', lines[i])
            # if the line starts with s, it is the fake label named as the original state
            if len(no_whitespace) > 0 and no_whitespace[0] == 's':
                # the required index is the final part of the string
                num_str = int(re.findall(r'\d+', no_whitespace)[-1])
                # remove whitespaces from the following line
                next_no_whitespace = re.sub(r'\s', '', lines[i+1])
                # convert the final part of the string to int and place it in the list of states:
                states[int(num_str)] = int(re.findall(r'\d+', next_no_whitespace)[-1])
    args["states"] = states


def lps2lts(args):
    print("converting to lts...")
    # run_command("lps2lts  --cached -rjittyc --threads=32 " +
    #             args["lps"] + " " + args["lts"])
    run_command("lps2lts  --cached --threads=32 " +
                args["lps"] + " " + args["lts"])
    run_command("ltsconvert " + args["lts"] + " " + args["lts"] + ".dot")
    #run_command("neato -Tpdf " + args["lts"] + ".dot" + " -o " + args["lts"] + ".pdf" )


def ltsminimise(args):
    print("minimizing....")
    #TODO: please use a variable to hold the filenames, and use popen with an array of arguments instead of run_command
    run_command("ltsconvert -ebranching-bisim " + args["base"] + " " + args["minimised"])    
    run_command("ltsconvert " + args["minimised"] + " " + args["minimised"] + ".dot")
    run_command("neato -Tpdf " + args["minimised"] + ".dot" + " -o " + args["minimised"] + ".pdf" )


def createJsonFiles(args):
    print("converting to visualizer format...")
    result = subprocess.run(
        "ltsinfo -l " + args["minimised"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stderr_str = result.stderr
    # parse ltsinfo.txt and decode it
    with open("ltsinfo.txt", 'wb') as infofile:
        infofile.write(stderr_str)
    decoded = stderr_str.decode("utf-8")

    pairs = [(0, 0) for i in range(0, points)]
    no_white_decoded = re.sub(r'\s', '', decoded)
    # get the final part of the string, containing pairs (class, state)
    states_string = no_white_decoded.split(
        "Thestatelabelsofthislabelledtransitionsystem:", 1)[1]

    # remove colons
    string_pairs = re.sub(r':', '', states_string)

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
    color_state = [(0, "") for i in range(0, points)]
    i = 0

    for elem in data["points"]:
        color_state[i] = (pairs[i][0], elem["atoms"])
        i = i+1

    classes_with_duplicates = [i for (i, _) in pairs]
    classes = list(dict.fromkeys(classes_with_duplicates))

    jsonArrays = [{"class" + str(i): []} for i in range(0, len(classes))]

    for i in range(0, len(classes)):
        for j in range(0, len(pairs)):
            if classes[i] == pairs[j][0]:
                jsonArrays[i]["class" + str(i)].append(True)
            else:
                jsonArrays[i]["class" + str(i)].append(False)

    for i in range(0, len(jsonArrays)):
        with open("jsonOutput" + str(i) + ".json", 'w') as outjson:
            json.dump(jsonArrays[i], outjson, indent=2)

def createModelFiles(args):
    print("converting to model checker format...")
    result = subprocess.run(
        "ltsconvert --out=aut " + args["minimised"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stderr_str = result.stdout
    decoded = stderr_str.decode("utf-8")

    string_list = decoded.split('\n')
    outDict = {"points" : []}
    tmpDict = {}
    for el in string_list:
        match = re.match(r'\((\d+),("dwn"|"ap.*"),(\d+)\)', el)
        l =[]
        if match:
            #print(match.group(1) + " " + match.group(2))
            dest = match.group(1) # this is the destination of an "up" transition
            atom = match.group(2)
            source = match.group(3)
            if not source in tmpDict:
                outDict["points"].append({ "id": source, "up": [], "atoms": []})
                tmpDict[source] = len(outDict["points"]) - 1
            else:
                if not dest in outDict["points"][tmpDict[source]]["up"]:
                    outDict["points"][tmpDict[source]]["up"].append(dest)
            if "ap" in atom:
                outDict["points"][tmpDict[source]]["atoms"].append(atom[4:-1])
    with open("polyInput_Poset.json", 'w') as outjson:
        json.dump(outDict, outjson, indent=2)

# CACHED EXECUTION

use_cache = True #TODO: make this a command line switch, default to True

def cached_execute(filename, name, fn, args):
    start_time = time.time()
    if use_cache and os.path.exists(filename):
        print("file " + filename + " already exists")
    else:
        result = fn(args)
        now = time.time() - start_time
        times[name] = [now]
        print(f"{name} time: " + str(now))
        return result


# THE GLOBAL SCRIPT STARTS HERE


input_file = sys.argv[1]  # this is base_name.json

# For interactive use:
# os.chdir("/workspaces/case-study-eta-minimization/experiments/triangle")
# input_file = "triangleRBModel_Poset.json"

base_name = os.path.splitext(input_file)[0]

norm_base_name = os.path.normpath(base_name)
abs_base_name = os.path.abspath(norm_base_name)
norm_dir_name = os.path.dirname(abs_base_name)
output_dir = f'{norm_dir_name}/toolchain_output'

print(input_file,base_name,norm_base_name,abs_base_name,norm_dir_name,output_dir)


os.makedirs(output_dir, exist_ok=True)

if not base_name.split('_')[-1] == "Poset":
    base_name = base_name + "_Poset"
    cached_execute(base_name + ".json", f"poly2poset", poly2poset,
                   {"poly": input_file, "poset": base_name + ".json"})
poset_file = base_name + f".json"



tmp = {"poset": poset_file}
cached_execute("fakefile.txt", f"loadData", loadData, tmp)

data = tmp["data"]

x = cached_execute(output_dir + "/" + base_name + ".mcrl2", f"poset2mcrl2",
                   poset2mcrl2, {"data": data, "base_name": base_name, "output_dir": output_dir})

def debug():
    return nx.to_dict_of_dicts(x["lts"])

#debug()
#%%

# generate the lps and get the lps pretty print
# NOTE: this files must always be recreated, as they are computed twice with different actions.
# Therefore, an existing lps file is different than the one created here, that is needed to retrieve original states
cached_execute(f"{output_dir}/{base_name}.lps", f"mcrl2lps", mcrl2lps, {
               "mcrl2": f"{output_dir}/{base_name}.mcrl2", "lps": f"{output_dir}/{base_name}.lps"})

cached_execute(f"{output_dir}/{base_name}.lpspp", f"lps2lpspp", lps2lpspp, {
               "lps": f"{output_dir}/{base_name}.lps", "lpspp": f"{output_dir}/{base_name}.lpspp"})

# create a list of zeroes: zeroes will be replaced with the corresponding
# state of the mcrl2 model: the index of the original state will contain the corresponding mmcrl2 state
tmp2 = {"base": f"{output_dir}/{base_name}.lpspp",
        "points": len(data["points"])}

# get the correspondence between the original states and the mcrl2 states
cached_execute(f"{output_dir}/states.txt", f"findStates", findStates, tmp2)
states = tmp2["states"]

points = len(data["points"])

# now rename actions into tau and get the clean lps
cached_execute(f"{output_dir}/{base_name}_renamed.lps", f"renamelps", renamelps, {
               "base": f"{output_dir}/{base_name}.lps", "renamed": f"{output_dir}/{base_name}_renamed.lps", "points": points})
cached_execute(f"{output_dir}/{base_name}_renamed.lpspp", f"lps2lpspp", lps2lpspp, {
               "lps": f"{output_dir}/{base_name}_renamed.lps", "lpspp": f"{output_dir}/{base_name}_renamed.lpspp"})

# transform the lps into an lts and minimise it
cached_execute(f"{output_dir}/{base_name}_renamed.lts", f"lps2lts", lps2lts, {
               "lps": f"{output_dir}/{base_name}_renamed.lps", "lts": f"{output_dir}/{base_name}_renamed.lts"})

cached_execute(f"{output_dir}/{base_name}_minimised.lts", f"ltsminimise", ltsminimise, {
               "base": f"{output_dir}/{base_name}_renamed.lts", "minimised": f"{output_dir}/{base_name}_minimised.lts"})

# now we get the ltsinfo and the correspondence between classes and original states
cached_execute(f"jsonOutput0.json", f"createJsonFiles", createJsonFiles, {
               "minimised": f"{output_dir}/{base_name}_minimised.lts"})

cached_execute(f"modelInput.json", f"createModelFile", createModelFiles, {
               "minimised": f"{output_dir}/{base_name}_minimised.lts", "input": f"{output_dir}/{base_name}_minimised.json"})

df = ps.DataFrame.from_dict(times, orient="index")

print("---")
print(df)

with open(sys.argv[2], 'w') as outfile:
    df.to_latex(outfile, header=False)
