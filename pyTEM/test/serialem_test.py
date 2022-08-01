"""
SerialEM is a program that can acquire a variety of data from electron microscopes:
- tilt series for electron tomography,
- large image areas for 3-D reconstruction from serial sections,
- and images for reconstruction of macromolecules by single-particle methods.

As shown here:
https://sphinx-emdocs.readthedocs.io/en/latest/serialem-note-hidden-goodies.html#example-5-scripting-with-python, it is
possible to call serialEM functions from Python. SerialEM has lots of interesting high-level commands that could prove
useful in a variety of context -> a list of available serialEM commands can be found here:
 https://bio3d.colorado.edu/SerialEM/hlp/html/script_commands.htm


In oder to enable remote python, I added the following lines to the SerialEM property file
 (C:/ProgramData/SerialEM/SerialEMproperties.txt on the Talos PC):
PathToPython 3.6 C:\FEI\Python36
PythonModulePath C:\Program Files\SerialEM\PythonModules
ScriptMonospaceFont Consolas
EnableExternalPython 1
"""

import serialem as sem

print("\nHere is a list of the available serialEM commands:")
print(dir(sem))

try:

    print("\nTesting moving the stage..")
    sem.MoveStageTo(1, 1)  # MoveTo takes input in um

    print("\nTesting obtaining the spot size..")
    spot_size = sem.ReportSpotSize
    print(type(spot_size))
    print(dir(spot_size))

    # print("\nPerforming auto alignment..")
    # sem.AutoAlign()

except sem.SEMmoduleError as e:
    print("Unable to connect to microscope, please double check that the SerialEM client is running.")
    raise e
