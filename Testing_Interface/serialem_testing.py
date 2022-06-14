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

"""

import sys

sys.path.append(str("C:/Program Files/SerialEM/PythonModules"))
import serialem as sem

sem.AutoAlign()
