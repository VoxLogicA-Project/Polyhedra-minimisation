#!/usr/bin/env python3

# Date: 2024/01/05
# Mieke (adapted from a python script by Vincenzo)

# This script takes a .maze specification and produces an LTS in .mcrl2 format of the maze
# The resulting .mcrl2 file can be used for minimisation using the script min_spec.py
# Needs to run from the directory where the .maze file is situated

# Usage: python maze2mcrl2.py <input_file.maze>

import sys
import os
import subprocess

def run_command(command):
    subprocess.run(command, shell=True)

if len(sys.argv) != 2:
    print("Usage: python maze2mcrl2.py <input_file.maze>")
    sys.exit(1)

input_file = sys.argv[1]
base_name = os.path.splitext(input_file)[0]

run_command(f"MazingProject {input_file} > {base_name}_AmazerOutput.json")
run_command(f"python /Users/mieke/Documents/RESEARCH/VVTOOLS/MAZER_MazeToModel/myMazeToLargeCorridorModel.py {base_name}_AmazerOutput.json")
run_command(f"PolyPoProject mazeModel.json {base_name}_Poset.json")
run_command(f"python /Users/mieke/Documents/RESEARCH/VVTOOLS/MCRL2_PYTHON/encodermm_enc_eta_clean_simpler_fewer_tau.py {base_name}_Poset.json")

#run_command(f"mcrl22lps --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm {input_file} {base_name}.lps")
#run_command(f"lps2lts {base_name}.lps {base_name}.lts")
#run_command(f"ltsconvert -ebranching-bisim {base_name}.lts {base_name}_minimised.lts")
#run_command(f"ltsconvert -ebranching-bisim --tau=ch {base_name}_2.lts {base_name}_3.lts")
