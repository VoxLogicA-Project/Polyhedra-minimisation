# This script invokes the toolchain on a given experiment,
# then runs PolyLogicA on the minimised model.
# Finally, it moves the json result of PolyLogicA to
# the experiment's folder and invokes resultTransformer.
# At this point, the user can visualise the result on 
# PolyVisualiser.
import os
import shutil
import subprocess

# Clean the environment from results of previous experiments

os.chdir("..")
for root, dirs, files in os.walk("experiments"):
    for name in dirs:
        try:
            shutil.rmtree(root + "/" + name + "/toolchain_output")
            shutil.rmtree(root + "/" + name + "/results")
            print(root + "/" + name + "result.json")
            os.remove(root + "/" + name + "/result.json")
        except OSError as e:
            pass

# Copy PolyLogicA binaries if they do not exist

subprocess.run("mkdir PolyLogicA", shell=True)
subprocess.run("cp -r ~/VoxLogicA/src/bin PolyLogicA", shell=True)
subprocess.run("cp scripts/mazeModelMinimised.imgql PolyLogicA", shell=True)

def runExperiment(experiment):
    experimentPath = "experiments/" + experiment
    print(experimentPath)
    os.chdir(experimentPath)
    subprocess.run("../../scripts/toolchain.py mazeModel.json", shell=True)
    subprocess.run("cp toolchain_output/minimised_model/polyInput_Poset.json ../../PolyLogicA", shell=True)
    os.chdir("../../PolyLogicA")
    subprocess.run(f'''./bin/release/net8.0/linux-x64/PolyLogicA mazeModelMinimised.imgql''', shell=True)
    subprocess.run(f'''mv result.json ../{experimentPath}''', shell=True)
    #os.chdir("../" + experimentPath)
    os.chdir("../scripts")
    subprocess.run(f'''python3 resultTransformer.py --classesFile ../experiments/{experiment}/toolchain_output/classes/jsonOutputAll.json --experiment {experiment} --results ../experiments/{experiment}/result.json''', shell=True)
    os.chdir("..")

# Run actual experiments

runExperiment("3DMAZE_3x3x3_G1W_LC_V2")
runExperiment("3DMAZE_3x5x3_G1W_LC_V2")
#runExperiment("3DMAZE_3x5x4_G1W_LC_V2")
#runExperiment("3DMAZE_5x5x5_G1W_LC_V2")