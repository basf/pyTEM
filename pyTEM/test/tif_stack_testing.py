import pathlib

import numpy as np
import hyperspy.api as hs

from tifffile import tifffile


out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve() / "test" \
                / "interface" / "test_images"
print(out_dir)
in_file_ = out_dir / "example_tiff_stack.tif"
# in_file_ = out_dir / "cat.jpeg"

print("\nLoading with tifffile...")
input_ = tifffile.imread(str(in_file_))
print(type(input_))
print(np.shape(input_))
print(type(input_[0][0][0]))

print("\nLoading with Hyperspy...")
input_2 = hs.load(str(in_file_))
print(type(input_))
print(np.shape(input_))
print(type(input_[0][0][0]))

# out_file = out_dir / "tif_stack_written.tif"
# tifffile.imwrite(out_file, input_)
