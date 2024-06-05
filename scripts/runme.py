# This script invokes the toolchain on a given experiment,
# then runs PolyLogicA on the minimised model.
# Finally, it moves the json result of PolyLogicA to
# the experiment's folder and invokes resultTransformer.
# At this point, the user can visualise the result on 
# PolyVisualiser.
import os
import argparse
import subprocess

cli = argparse.ArgumentParser()
cli.add_argument("--experimentName")

args = cli.parse_args()
experiment = args.experimentName
experimentPath = "../experiments/" + experiment
os.chdir(experimentPath)

subprocess.run("../../scripts/toolchain.py " + experiment + "Model.json", shell=True)
subprocess.run("cp toolchain_output/minimised_model/polyInput_Poset.json ../../PolyLogicA", shell=True)
os.chdir("../../PolyLogicA")
subprocess.run(f'''./bin/release/net8.0/linux-x64/PolyLogicA {experiment}.imgql''', shell=True)
subprocess.run(f'''mv result.json ../experiments/{experimentPath}''', shell=True)
os.chdir("../experiments/" + experimentPath)
subprocess.run(f'''python3 ../../scripts/resultTransformer.py --classesFile toolchain_output/classes/jsonOutputAll.json --results result.json''', shell=True)