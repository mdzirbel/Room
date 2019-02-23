py deployProject.py
"C:/Program Files/Putty/plink" pi@128.146.101.84 -batch -pw 0517fic sudo killall python
"C:/Program Files/Putty/pscp" -r -pw 0517fic Deploy\ pi@128.146.101.84:PythonProjects/Room/
rem "C:/Program Files/Putty/plink" pi@128.146.101.84 -batch -pw 0517fic sudo python "PythonProjects/main.py"