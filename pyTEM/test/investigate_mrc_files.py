import mrcfile
import numpy as np
from mrcfile.constants import MAP_ID
import pathlib
import hyperspy.api as hs

image_dir = pathlib.Path(__file__).parent.resolve() / "test_images"
in_file = image_dir / "Y1908J01-B1 V3 840mm SAD40 2k.mrc"
# in_file = image_dir / "random_image1.mrc"

mrcfile.validate(in_file)

with mrcfile.open(in_file, permissive=True) as mrc:
    # mrc.header.map = MAP_ID  # Fix the header, so we can read without permissive
    print("Reading in file: " + str(in_file))
    print(mrc)
    print(mrc.header)
    print(np.shape(mrc.data))

# hs_image = hs.load(in_file)
# print(hs_image)
