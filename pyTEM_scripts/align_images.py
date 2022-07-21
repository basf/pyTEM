"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import sys
import pathlib
import mrcfile

import numpy as np


# If not already, add pyTEM to path
pytem_directory = pathlib.Path(__file__).resolve().parent.resolve().parent.resolve()
print("pytem_directory: " + str(pytem_directory))
for i in range(4):
    pytem_directory = pytem_directory.parent.resolve()
if str(pytem_directory) not in sys.path:
    print("Adding pytem_directory to path")
    sys.path.append(str(pytem_directory))
else:
    print("pytem already on path")


for p in sys.path:
    print(p)
try:
    from pyTEM.lib.interface.Acquisition import Acquisition
    from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
    from pyTEM_scripts.lib.GetInOutFile import GetInOutFile
except Exception as ImportException:
    raise ImportException


def align_images():
    """
    Read in some images (possibly from a stack, possibly from a bunch of single image files), align the images, and save
     the results back to file.

    Image alignment is performed using

    :return: None.
    """
    # Preallocate.
    acq_series = AcquisitionSeries()

    # Get the in and out file info from the user.
    in_file, out_file = GetInOutFile().run()

    if isinstance(in_file, str):
        # Then we have a single file, assume it is an image stack.

        if in_file[-4:] == ".mrc":
            # Then it is an MRC file (probably).
            with mrcfile.open(in_file, permissive=True) as mrc:
                image_stack_arr = mrc.data
                extended_header = mrc.extended_header

            # Load the images into an acquisition series object.
            images = np.shape(image_stack_arr)[0]
            for i in range(images):
                acq_series.append(Acquisition(image_stack_arr[i]))

            # Go ahead and actually perform the alignment and save in this conditional to preserve the metadata stored
            #  in the extended header.
            acq_series = acq_series.align()

            # Save the results to file.
            with mrcfile.new(out_file, overwrite=True) as mrc:
                mrc.set_data(acq_series.get_image_stack())
                mrc.set_extended_header(extended_header)

            return  # We are done here

        elif out_file[-4:] == ".tif" or out_file[-5:] == ".tiff":
            raise NotImplementedError("We don't know how to deal with TIFF stacks yet!")  # TODO

        else:
            raise Exception("File type unknown.")

    else:
        # We have a bunch of single images in separate files.
        for file in in_file:
            acq_series.append(Acquisition(file))

    # Go ahead and perform the alignment using AcquisitionSeries' align() method.
    acq_series = acq_series.align()

    # Save to file.
    if out_file[-4:] == ".mrc":
        acq_series.save_as_mrc(out_file=out_file)

    elif out_file[-4:] == ".tif" or out_file[-5:] == ".tiff":
        acq_series.save_as_tif(out_file=out_file)

    else:
        raise Exception("Error: Out file type not recognized: " + str(out_file))


if __name__ == "__main__":
    align_images()
