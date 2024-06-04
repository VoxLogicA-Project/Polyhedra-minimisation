This artifact contains all the files and scripts needed in order to reproduce the results shown in the paper. Experiments consist of two separated steps:
    1: the minimisation step, where the original model is translated into a poset and minimised;
    2: the model checking step, where model checking is performed over the minimised model.
In the follwing, we explain in details how to reproduce results and visualise them, using the triangleRB experiment as a running example.

---PolyVisualiser---

In order to visualise results obtained running the two steps, we provide users with a PolyVisualiser. The PolyVisualiser accepts as input a model (in the json format), a colour file
listing all atomic propositions contained in the model and and atom file, containing truth values of atomic propositions and possibly formulas.
In order to launch the PolyVisualiser webapp it suffices to access the application folder, open a terminal and launch a server. For instance, using php, you can run the following
command:
    php -S localhost:5000
and open a browser to the page 127.0.0.1:5000/polyVisualiser.html. Once you have loaded the required files (in our case triangleRBModel.json, triangleRBColors.json, triangleRBAtoms.json),
you will be able to visualise the model and its properties. Using the Property menu, and selecting the Show Property option, it will be possible to visualise where different atomic 
propositions hold.

---Minimisation---

Minimisation of the model is performed by the toolchain.py script, that takes as an input a model file. In order to run the script, one must access the experiment folder and run it
from command line. In our example:
    cd experiments/triangleRB
    ../../scripts/toolchain.py triangleRBModel.json
The result of the execution will be a json file containing a dictionary of the equivalence classes, in the form array of booleans. The length of each array corresponds to the number of
states of the original poset model,