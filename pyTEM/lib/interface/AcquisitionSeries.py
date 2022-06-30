"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
import sys
import warnings
import mrcfile

from typing import Union
import numpy as np

package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.lib.interface.Acquisition import Acquisition
except Exception as ImportException:
    raise ImportException


class AcquisitionSeriesIterator:
    """
    Iterator for the AcquisitionSeries class.
    """

    def __init__(self, acquisition_series):
        self.__acquisition_series = acquisition_series
        self.__index = 0

    def __next__(self) -> Acquisition:
        """
        :return: Acquisition:
            The next acquisition in the acquisition series.
        """
        if self.__index < self.__acquisition_series.length():
            self.__index += 1
            return self.__acquisition_series.get_acquisition(idx=self.__index - 1)

        raise StopIteration  # End of Iteration


class AcquisitionSeries:
    """
    Hold a series of Acquisition objects.

    Helpful for saving image stacks to file.

    Public Attributes:
        None

    Protected Attributes:
        None.

    Private Attributes:
        __acquisitions:      Python list:   An list of Acquisition objects.
    """

    def __init__(self):
        self.__acquisitions = []

    def append(self, acq: Acquisition) -> None:
        """
        Added a new acquisition to the series.
        :param acq: Acquisition:
            The acquisition to append.
        :return: None.
        """
        if isinstance(acq, Acquisition):
            self.__acquisitions.append(acq)
        else:
            raise Exception("Error: Unable to append to AcquisitionSeries, the provided argument is not of type "
                            "Acquisition.")

    def length(self) -> int:
        """
        :return: int:
            The number of acquisitions in the series.
        """
        return len(self.__acquisitions)

    def get_acquisition(self, idx: int) -> Acquisition:
        """
        :param idx: int:
            The index of the acquisition you want.
        :return: Acquisition:
            The acquisition at the provided index
        """
        return self.__acquisitions[idx]

    def set_acquisition(self, acq: Acquisition, idx: int) -> None:
        """
        :param acq: Acquisition:
            The acquisition to set.
        :param idx: int:
            Where you want to put the acquisition.
        :return: None.
        """
        self.__acquisitions[idx] = acq

    def downsample(self) -> None:
        """
        Downsample all images in the stack by a factor of 2. Useful for saving space.

        :return: None. Operation performed inplace.
        """
        for acq in self.__acquisitions:
            acq.downsample()

    def save_as_tif(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition as a TIFF file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .tif extension, otherwise it will be added automatically.

        :return: None.
        """
        raise NotImplementedError  # TODO: (save images as 16-byte TIFF)

    def save_as_mrc(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition series as an MRC file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .mrc extension, otherwise it will be added automatically.

        :return: None.
        """
        out_file = str(out_file)  # Encase we received a path.

        if self.length() < 0:
            raise Exception("AcquisitionSeries.save_as_mrc() requires at least one image exist in the series.")

        # In case we are missing the .mrc extension, add it on.
        if out_file[-4:] != ".mrc":
            out_file = out_file + ".mrc"

        # Stack all the images into a 3D array
        # Use the first acquisition in the stack as a reference image to determine shape and type info.
        ref_image = self.get_acquisition(idx=0).get_image()
        image_shape = np.shape(ref_image)
        image_stack = np.empty(shape=(self.length(), image_shape[0], image_shape[1]), dtype=np.int16)  # TODO
        for i, acq in enumerate(self.__acquisitions):
            if np.shape(acq.get_image()) == image_shape:
                image_stack[i] = acq.get_image()
            else:
                warnings.warn("Acquisition at index " + str(i) + " omitted from " + out_file
                              + " because the image is the wrong size.")

        # Until we know how to build our own extended header, just use a stock one
        # TODO: Figure out how to write metadata to MRC header
        header_file = pathlib.Path(
            __file__).parent.resolve().parent.resolve().parent.resolve() / "lib" / "interface" \
                      / "stock_mrc_header" / "stock_mrc_header.npy"
        extended_header = np.load(str(header_file))

        with mrcfile.new(out_file, overwrite=True) as mrc:
            mrc.set_data(image_stack)
        mrc.set_extended_header(extended_header)
        warnings.warn("Acquisition metadata not yet stored in MRC images, for now we are just using a stock header!")

    def __iter__(self):
        return AcquisitionSeriesIterator(self)


if __name__ == "__main__":
    acq_series = AcquisitionSeries()
    acq_series.append(Acquisition(None))
    acq_series.append(Acquisition(None))
    acq_series.append(Acquisition(None))

    out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve().parent.resolve() / "test" \
              / "interface" / "test_images"
    out_file_ = out_dir / "mrc_test_stack.mrc"

    print(acq_series.get_acquisition(idx=0).get_metadata())

    print("\nTesting iteration:")
    for c, acq_ in enumerate(acq_series):
        print(c)
        print(acq_)

    acq_series.save_as_mrc(out_file=out_file_)
