"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import argparse

from typing import Tuple

from pyTEM.lib.Acquisition import Acquisition
from pyTEM.lib.AcquisitionSeries import AcquisitionSeries
from pyTEM_scripts.lib.align_images.GetInOutFile import GetInOutFile
from pyTEM_scripts.lib.align_images.display_goodbye_message import display_goodbye_message

DESCRIPTION = "Read in some images (possibly from an image stack, possibly from a bunch of single image files), " \
              "align the images, and save the results back to file." \
              "\n\n" \
              "Image shifts are estimated using Hyperspy's estimate_shift2D() function. This function uses a phase " \
              "correlation algorithm based on the following paper: " \
              "\n   Schaffer, Bernhard, Werner Grogger, and Gerald Kothleitner. “Automated Spatial Drift Correction " \
              "\n       for EFTEMmImage Series.” Ultramicroscopy 102, no. 1 (December 2004): 27–36."


def align_images(verbose: bool = False):
    """
    Read in some images (possibly from a stack, possibly from a bunch of single image files), align the images, and
     save the results back to file. For more information, please refer to the above description, or view using:

        align_images --help

    :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: None. The resulting image stack is saved to file at the location requested by the user.
    """
    # Get the in and out file info from the user.
    if verbose:
        print("Prompting the user for in/out file path information...")
    in_file, out_file = GetInOutFile().run()

    if isinstance(in_file, str):
        # Then we have a single file, assume it is an image stack.
        if verbose:
            print("Reading in image stack...")
        acq_series = AcquisitionSeries(source=in_file)

    elif isinstance(in_file, Tuple):
        # We have a bunch of single images in separate files.
        num_in_files = len(in_file)
        if verbose:
            print("Reading in single image files...")

        acq_series = AcquisitionSeries()
        for i, file in enumerate(in_file):
            if verbose:
                print(" Loading image " + str(i + 1) + " out of " + str(num_in_files) + "...")
            acq_series.append(Acquisition(file))

    else:
        raise Exception("Error: in_file type not recognized: " + str(type(in_file)))

    # Go ahead and perform the alignment using AcquisitionSeries' align() method.
    if verbose:
        print("Performing image alignment...")
    acq_series = acq_series.align()
    if verbose:
        print("Image alignment complete...")

    # Save to file.
    if out_file[-4:] == ".mrc":
        if verbose:
            print("Saving to file as MRC...")
        acq_series.save_as_mrc(out_file=out_file)

    elif out_file[-4:] == ".tif" or out_file[-5:] == ".tiff":
        if verbose:
            print("Saving to file as TIFF...")
        acq_series.save_as_tif(out_file=out_file)

    else:
        raise Exception("Error: Out file type not recognized: " + str(out_file))

    if verbose:
        print("Displaying goodbye message...")
    display_goodbye_message(out_path=out_file)


def script_entry():
    """
    Entry point for Align Images script. Once pyTEM is installed, view script usage by running the following
     command in a terminal window:

        align_images --help

    """
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--verbose", help="Increase verbosity; especially useful when debugging.",
                        action="store_true")
    args = parser.parse_args()
    align_images(verbose=args.verbose)


if __name__ == "__main__":
    align_images(verbose=True)
