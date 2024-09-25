# This script invokes the toolchain on a given experiment,
# then runs PolyLogicA on the minimised model.
# Finally, it moves the json result of PolyLogicA to
# the experiment's folder and invokes resultTransformer.
# At this point, the user can visualise the result on 
# PolyVisualiser.
import os
import argparse
import subprocess

os.chdir("..")
subprocess.run("mkdir PolyLogicA", shell=True)
subprocess.run("cp -r ~/VoxLogicA/src/bin PolyLogicA", shell=True)
subprocess.run(f'''touch PolyLogicA/mazeModelMinimised.imgql''', shell=True)
subprocess.run(f'''echo \
                'load model = "polyInput_Poset.json"\n \
                // Define reach (rho) in terms of through (gamma)\n \
                let reach(x,y) = x | through(y,x)\n \
                // Surround in terms of reach (rho)\n \
                let sur(x,y)	= x & !reach(!(x | y), !y)\n \
                let green       = ap("G")\n \
                let white       = ap("W")\n \
                let corridor    = ap("corridor")\n \
                let greenOrWhite		= (green | white)\n \
                let oneStepToWhite   = eta((green | eta(corridor,white)),white)\n \
                let twoStepsToWhite  = eta((green | eta(corridor,oneStepToWhite)), oneStepToWhite) & (!oneStepToWhite)\n \
                let threeStepsToWhite = eta((green | eta(corridor,twoStepsToWhite)), twoStepsToWhite) & (!twoStepsToWhite) & (!oneStepToWhite)\n \
                let phi1 = eta((green | eta(corridor,white)),white)\n \
                let phi2 = eta((green | eta(corridor,oneStepToWhite)), oneStepToWhite)\n \
                save "green" green\n \
                save "white" white\n \
                save "corr" corridor\n \
                save "phi1" phi1\n \
                save "phi2" phi2\n' > PolyLogicA/mazeModelMinimised.imgql''', shell=True)

def runExperiment(experiment):
    experimentPath = "experiments/" + experiment
    print(experimentPath)
    os.chdir(experimentPath)
    subprocess.run("../../scripts/toolchain.py mazeModel.json", shell=True)
    subprocess.run("cp toolchain_output/minimised_model/polyInput_Poset.json ../../PolyLogicA", shell=True)
    os.chdir("../../PolyLogicA")
    subprocess.run(f'''./bin/release/net8.0/linux-x64/PolyLogicA mazeModelMinimised.imgql''', shell=True)
    subprocess.run(f'''mv result.json ../{experimentPath}''', shell=True)
    os.chdir("../" + experimentPath)
    subprocess.run(f'''python3 ../../scripts/resultTransformer.py --classesFile toolchain_output/classes/jsonOutputAll.json --results result.json''', shell=True)

runExperiment("3DMAZE_3x5x3_G1W_LC_V2")
runExperiment("3DMAZE_3x5x4_G1W_LC_V2")
runExperiment("3DMAZE_5x5x5_G1W_LC_V2")