"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import argparse

from pyTEM.lib.Acquisition import Acquisition
from pyTEM.lib.AcquisitionSeries import AcquisitionSeries

from pyTEM_scripts.lib.bulk_carbon_analysis.GetInOutFiles import GetInOutFiles

DESCRIPTION = "Given 16 natural light micrographs of a bulk carbon sample sandwiched between polarizers of varying " \
              "cross, produce both anisotropy and orientation maps. " \
              "\n\n" \
              "Since input files will be read in alphabetical order (regardless of the order in which they are " \
              "selected), the files must be titled such that they are ordered as follows when sorted alphabetically: " \
              "\n" \
              "\n  Polarizer Angle [deg]       Analyzer Angle [deg]     Suggested Filename Prefix " \
              "\n          0                           0                      11_  OR  0_0_" \
              "\n          0                           45                     12_  OR  0_45_" \
              "\n          0                           90                     13_  OR  0_90_" \
              "\n          0                          135                     14_  OR  0_135_" \
              "\n\n" \
              "\n          45                          0                      21_  OR  45_0_" \
              "\n          45                          45                     22_  OR  45_45_" \
              "\n          45                          90                     23_  OR  45_90_" \
              "\n          45                         135                     24_  OR  45_135_" \
              "\n\n" \
              "\n          90                          0                      31_  OR  90_0_" \
              "\n          90                          45                     32_  OR  90_45_" \
              "\n          90                          90                     33_  OR  90_90_" \
              "\n          90                         135                     34_  OR  90_135_" \
              "\n\n" \
              "\n         135                           0                     41_  OR  135_0_" \
              "\n         135                           45                    42_  OR  135_45_" \
              "\n         135                           90                    43_  OR  135_90_" \
              "\n         135                          135                    44_  OR  135_135_" \
              "\n\n" \
              "Notice that putting the suggested file name prefixes at the beginning of your input file names " \
              "ensures the input files are read in the expected order." \
              "\n\n" \
              "We use the technique explained in the following paper:" \
              "\n   Gillard, Adrien & Couégnat, Guillaume & Caty, O. & Allemand, Alexandre & P, Weisbecker & " \
              "\n         Vignoles, Gerard. (2015). A quantitative, space-resolved method for optical anisotropy " \
              "\n         estimation in bulk carbons. Carbon. 91. 423-435. 10.1016/j.carbon.2015.05.005." \
              "\n" \
              "\nIn line with the Gillard et al. notation, image variables are labeled and referenced as follows:" \
              "\n" \
              "\n                                  Analyzer angle" \
              "\n                                  0 deg       45 deg      90 deg      135 deg" \
              "\n  Polarizer angle     0 deg         11          12          13          14" \
              "\n                      45 deg        21          22          23          24" \
              "\n                      90 deg        31          32          33          34" \
              "\n                      135 deg       41          42          43          44"


def bulk_carbon_analysis(verbose: bool = False):
    """
    Given 16 natural light micrographs of a bulk carbon sample sandwiched between polarizers of varying cross, produce
     both anisotropy and orientation maps. For more information, please refer to the above description, or view using:

        bulk_carbon_analysis --help

    :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: None. The resulting anisotropy and orientation maps are saved to file at the locations requested by the
                user.
    """
    # Get the in and out file info from the user.
    if verbose:
        print("Prompting the user for in and out file path info...")
    in_files, anisotropy_out_path, orientation_out_path = GetInOutFiles().run()

    if len(in_files) != 16:
        raise Exception("Error: bulk_carbon_analysis() received the wrong number of input files. "
                        "Expected 16, received " + str(len(in_files)))

    # Use the pyTEM Acquisition and AcquisitionSeries classes to make our lives a little easier.
    if verbose:
        print("\nLoading the 16 in files into a AcquisitionSeries object.")
    acq_series = AcquisitionSeries()
    for file in in_files:
        acq_series.append(Acquisition(file))

    # There shouldn't be any drift, but sometimes there is some.
    if verbose:
        print("\nAligning series.")
    acq_series.align()

    raise NotImplementedError  # TODO


def script_entry():
    """
    Entry point for the Bulk Carbon Analysis script. Once pyTEM is installed, view script usage by running the following
     command in a terminal window:

        bulk_carbon_analysis --help

    """
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--verbose", help="Increase verbosity, especially useful when debugging.",
                        action="store_true")
    args = parser.parse_args()

    bulk_carbon_analysis(verbose=args.verbose)


if __name__ == "__main__":
    bulk_carbon_analysis()
