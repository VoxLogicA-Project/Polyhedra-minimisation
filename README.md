# Eta minimisation

This artifact contains all the files and scripts needed in order to reproduce the results shown in the paper. Experiments consist of two separated steps:

1. the minimisation step, where the original model is first translated into a poset, which is encoded into an LTS which is then minimised by branching equivalence minimisation provided by the mCRL2 toolset;
2. the model checking step, where model checking is performed over the minimised model.

In the follwing, we explain in detail how to reproduce results and visualise them, using the triangleRB experiment as a running example.

The artifact is provided with a Dockerfile that starts a new container with all required dependencies. To start the container, it suffices to run the script 
`run_container.sh` in the main directory.

All the proposed experiments are contained in the `experiments` folder. All the files required to run the triangleRB example are thus contained in the `experiments/triangleRB` folder.

## PolyVisualiser

In order to visualise results obtained running the two steps, we provide users with a `PolyVisualiser` application. `PolyVisualiser` accepts as input a model (in JSON format), a colour file
listing all the atomic propositions contained in the model, and an atom file, containing truth values of atomic propositions and possibly formulas.
In order to launch the `PolyVisualiser` tool it suffices to access the application folder, open a terminal and launch a server. For instance, using `python3`, we can run the following
command:

`python3 -m http.server`

and open a browser to the page `127.0.0.1:8000/polyVisualiser.html`. Once we load the required files (in our case `triangleRBModel.json`, `triangleRBColors.json`, `triangleRBAtoms.json`),
we will be able to visualise the model and its properties. Using the Property menu, and selecting the Show Property option, it will be possible to visualise, by highlighting the original color of the polyhedron, where different atomic propositions or formulas hold.

## Minimisation

Minimisation of the model is performed by the `toolchain.py` script, that takes as input a model file, performs the encoding and calls MCRL2 operations. In order to run the script, one must access the experiment folder and run it
from command line. In our example:

`cd experiments/triangleRB` \
`../../scripts/toolchain.py triangleRBModel.json`

The result of the execution (stored in the `toolchain_output/classes` folder) will be a JSON file containing a dictionary of the equivalence classes, in the form of an array of booleans. The length of each array corresponds to the number of
states of the original poset model. Let `classX` be the array of booleans representing the class labelled with `X`: then `classX[i] = True` if and only if the state `i` is included in the class `X`.

The JSON file can be loaded in `PolyVisualiser` as an atom file, in order to graphically visualise the equivalence classes. If there is no model poset file in the experiment folder, the
script generates a model poset file (in the format `experimentName_Poset.json`) that is needed to perform the encoding as an LTS and that can be used as an input for the model
checker `PolyLogicA`. In our case, the generated file will be `triangleRBModel_Poset.json`.
Finally, the toolchain script generates a `polyInput_Poset.json` file, containing the minimised Kripke structure model. It is possible to run model checking on this minimised model, and to 
compare results with those obtained by performing model checking on the original model.

## Model checking

As said, the model checker `PolyLogicA` accepts as an input a model file that can be a poset or a more general Kripke structure, plus an `imgql` specification. It is possible to run analysis on both the original and the minimised model
(in our example, `triangleRBModel_Poset.json` and `polyInput_Poset.json`).

First of all, it is necessary to copy the `PolyLogicA` binaries in the main directory with the following commands from the main directory:

`cd ../..` \
`mkdir PolyLogicA` \
`cp -r ~/VoxLogicA/src/bin PolyLogicA`

Then we can copy the `triangleRB.imgql` file, containing the actual analysis, in the `PolyLogicA` directory:

`cp scripts/triangleRB.imgql PolyLogicA`

as well as the poset files:

`cp experiments/triangleRB/triangleRBModel_Poset.json PolyLogicA` \
`cp experiments/triangleRB/toolchain_output/minimised_model/polyInput_Poset.json PolyLogicA`

The analysis contains two `load` commands: one can decomment the `load` command containing the poset to be analysed. For instance:

`//load triangle = "triangleRBModel_Poset.json"` \
`load triangle = "polyInput_Poset.json"`

loads the minimised model.

Now we can run model checking:

`cd PolyLogicA` \
`./bin/release/net8.0/linux-x64/PolyLogicA triangleRB.imgql`

The execution of these commands generates a file named `result.json`, containing JSON arrays of booleans. Being `prop` the array representing the property prop, `prop[i] = True` if
and only if the property prop is true at cell `i` of the polyhedral model..
While the result file generated by running analysis on the original model poset has the same number of states as the original model, this is not the case for the result file
generated by running analysis on the minimised model. To recover the results for the original model, we provide users with a `resultTransformer.py` script, that takes care of aligning the number of states of 
the result file with that of the original model, in such a way that it is possible to use results as an atom file in the `PolyVisualiser` tool. The `resultTransformer.py` script takes as input 
the `jsonOutputAll.json` file and the result file from the model checker, together with the name of the experiment. We can move for convenience the result file into the example directory:

`mv result.json ../experiments/triangleRB`

Now we can run:

`cd ../scripts` \
`python3 resultTransformer.py --classesFile ../experiments/triangleRB/toolchain_output/classes/jsonOutputAll.json --experiment triangleRB --results ../experiments/triangleRB/result.json`

The script creates a directory `..experiments/triangleRB/results` containing the file `originalResults.json`, namely an atom file whose size is compatible with that of the original poset model, and that thus can
be used as an atom file in the `PolyVisualiser`. It is hence possible to compare the results of the model checking procedure on both the original model and the minimised one.

After completing experiments, it is possible to clean all the directories by running the following:

`python3 cleanall.py`

## Automated experiments

In order to facilitate the process of reproducing the maze experiments proposed in the paper, we also provide a python script that performs all the aforementioned steps at once. This can be run as follows from the main directory:

`cd scripts` \
`python3 minimisedExperiments.py`

The script performs minimisation for the maze test suite, namely 3x3x3, 3x5x3, 3x5x4, 5x5x5. We can now again provide the `result.json` file to the `resultTransformer` tool, as an example:

`python3 resultTransformer.py --classesFile ../experiments/3DMAZE_3x3x3_G1W_LC_V2/toolchain_output/classes/jsonOutputAll.json --experiment 3DMAZE_3x3x3_G1W_LC_V2 --results ../experiments/3DMAZE_3x3x3_G1W_LC_V2/result.json`

We obtain a suitable atom file to be used in the `PolyVisualizer` tool for comparison.

WARNING: the line that launches the experiment `3DMAZE_3x3x3_G1W_LC_V2` is commented in the file, as the experiment requires high computational resources (it runs in ~1400s on a machine equipped with with an Intel(R) Core(TM) i9-9900K CPU @ 3.60 GHz (8 cores, 16 threads), 32GB RAM). If you want to run this experiment, you can just decomment this line.

# Elements

## Toolchain.py

Takes as input a model or a model poset. If the input is a model, the toolchain invokes Poly2Poset and transforms the input into a model poset.
The poset is then encoded into an LTS: the procedure produces a MCRL2 file.

The MCRL2 file is then transformed into an LPS. As states' labels are recreated during the encoding process, we generate an LPSpp (pretty print) file, that allows us to enstablish a correspondence between the original states' labels and the new ones. In order to do this:
* we add a self loop with the state name to every state in the form st_(state_label);
* we produce the lpspp;
* we check for lines starting with st to recover the state label and get the correspondent inner state.

In order to preserve minimisation, all the self loops labelled with the state names must be removed. We thus invoke the renamelps command to transform all these self loops into tau transitions. These will be removed by minimising the LTS.

We now produce the minimised LTS and create JSon files that serve as input for the PolyVisualiser. Finally, we create a LaTeX table containing execution times.

Recap: in order to get a minimised model, the user must only provide a model file (in JSon format) OR a model poset file (also in JSon format) and a filename with *.tex extension, indicating the latex table to be generated at the end of the process.

Output files are organised in subfolders. /toolchain_output contains all the intermediate files, plus two subfolders:
* minimised_model contains the minimised output;
* classes contains the JSon files in the PolyVisualiser format.

## ResultTransformer.py

In order to get a result file containing the right number of states, we wrote a resultTransformer script. It takes as input the result of the model checking procedure and the JSon files generated by the toolchain. The script parses the results and computes the or of all the classes where a formula is true, recovering them from the JSon files. The obtained files, stored in the folder /toolchain_output/results, can be now used to visualise the result of the model checking procedure in PolyVisualiser.

## Cleanall.py

After any experiment, we can run the utility script `cleanall.py` to remove all the ouput directories of previous experiments.