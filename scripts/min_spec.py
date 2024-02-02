#!/usr/bin/env python3

# Date: 2023/11/02
# Mieke (adapted from a version by Vincenzo)

# This script takes a mCRL2 specification and produces a minimised lts according to branching bisimulation
#
# It does so via transformation to lps and then lts, which in turn is minimised
# The mcrl22lps procedure has all options set that avoid implicit intermediate reduction of the mCRL2 specification
# All intermediate files are saved for inspection, in particular the lts of the full mCRL2 specification

# Usage: python min_spec.py <input_file.mcrl2>

import sys
import os
import subprocess

def run_command(command):
    subprocess.run(command, shell=True)

if len(sys.argv) != 2:
    print("Usage: python min_spec.py <input_file.mcrl2>")
    sys.exit(1)

input_file = sys.argv[1]
base_name = os.path.splitext(input_file)[0]

run_command(f"mcrl22lps --no-alpha --no-cluster --no-constelm --no-deltaelm --no-globvars --no-rewrite --no-sumelm {input_file} {base_name}.lps")
run_command(f"lps2lts {base_name}.lps {base_name}.lts")
run_command(f"ltsconvert -ebranching-bisim {base_name}.lts {base_name}_minimised.lts")
#run_command(f"ltsconvert -ebranching-bisim --tau=ch {base_name}_2.lts {base_name}_3.lts")
