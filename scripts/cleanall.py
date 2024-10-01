import os
import shutil

# Clean the environment from results of previous experiments

os.chdir("..")
for root, dirs, files in os.walk("experiments"):
    for name in dirs:
        try:
            shutil.rmtree(root + "/" + name + "/toolchain_output")
            shutil.rmtree(root + "/" + name + "/results")
            os.remove(root + "/" + name + "/results.json")
        except OSError as e:
            pass

try:
    shutil.rmtree("PolyLogicA")
except OSError as e:
    pass