"""
Test flipping and rotating images with numpy
"""
import pathlib

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from pyTEM.lib.interface.Acquisition import Acquisition


out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve() \
                / "interface" / "test_images"
out_file = out_dir / "cat.jpeg"

print("Building acquisition from " + str(out_file))
acq = Acquisition(out_file)

img = acq.get_image()
print(np.shape(img))
print(acq.get_image())

# flipped_image = np.flip(img, axis=1)
# rotated_image = np.rot90(flipped_image)

# All in one step
img = np.rot90(np.flip(img, axis=1))
img_plot = plt.imshow(img, cmap='Greys_r')
plt.show()


