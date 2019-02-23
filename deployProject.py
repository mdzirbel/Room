import glob, os
from shutil import copy

# os.chdir("")

for f in glob.glob("*.py"):
    if not f == "deployProject.py":
        copy(f, "Deploy")
