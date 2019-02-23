import glob, os
from shutil import copyfile

# os.chdir("")

for f in glob.glob("*.py"):
    if not os.path.basename(f.name) == "makeDeploy.py":
        copyfile(f.name, "/Deploy")
