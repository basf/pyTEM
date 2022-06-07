# Just some simple testing to get started with openCV
# openCV is a computer vision library that may be require to help solve the tilting problem
import pathlib
import sys
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

print("Your OpenCV version is: " + cv.__version__)

in_dir = pathlib.Path(__file__).parent.resolve()
in_file = in_dir / "data" / "Tiltseies_28k_-20-20deg_0.5degps_1.ser"


# image = cv.imread(cv.samples.findFile(relative_path=""))
#
# if image is None:
#     sys.exit()
