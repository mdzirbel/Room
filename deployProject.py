import glob
from shutil import copy

for f in glob.glob("*.py"):
    if not f == "deployProject.py":
        copy(f, "Deploy")
