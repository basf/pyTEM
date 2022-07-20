"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

# Required to type hint that a method is returning an instance of the enclosing class.
from __future__ import annotations

import pathlib
import sys
import warnings
import mrcfile

import numpy as np
import hyperspy.api as hs

from typing import Union, Tuple

package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.lib.interface.stock_mrc_extended_header.get_stock_mrc_header import get_stock_mrc_extended_header
    from pyTEM.lib.micro_ed.hyperspy_warnings import turn_off_hyperspy_warnings
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
    Hold a series of Acquisition objects. The image of each acquisition in the series must have the same shape
     and datatype as that of the first acquisition in the series.

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
        # TODO: Initialize from MRC, TIFF, and nd.array.

    def append(self, acq: Acquisition) -> None:
        """
        Added a new acquisition to the series.
        :param acq: Acquisition:
            The acquisition to append. The image of the acquisition must have the same shape and datatype as the rest
             of those in the series.
        :return: None.
        """
        if self.is_empty() and isinstance(acq, Acquisition):
            # This will be the first image in the series.
            self.__acquisitions.append(acq)

        # If it is not the first image, we have to check to make sure shape and datatype match.
        elif isinstance(acq, Acquisition) \
                and acq.image_shape() == self.image_shape() and acq.image_dtype() == self.image_dtype():
            self.__acquisitions.append(acq)

        else:
            raise Exception("Error: Unable to append to AcquisitionSeries, either the provided argument is not of type "
                            "Acquisition, the image is the wrong shape, or the image uses the wrong datatype.")

    def is_empty(self):
        """
        :return: True if the acquisition series is empty (contains 0 acquisitions), False otherwise.
        """
        if self.length() >= 1:
            return False  # Not empty
        else:
            return True

    def length(self) -> int:
        """
        :return: int:
            The number of acquisitions in the series.
        """
        return len(self.__acquisitions)

    def image_shape(self) -> Tuple[int, int]:
        """
        :return: (int, int):
            Image shape, in pixels.
            The image shape is determined by the shape of the first image in the series.
        """
        if not self.is_empty():
            return self.get_acquisition(idx=0).image_shape()

        else:
            raise Exception("Cannot determine the image shape of an empty series.")

    def image_dtype(self) -> type:
        """
        :return: type:
            The image datatype.
            The first image in the series is used as for reference.
        """
        if not self.is_empty():
            ref_image = self.get_acquisition(idx=0).get_image()  # Use the first image as reference
            return type(ref_image[0][0])

        else:
            raise Exception("Cannot determine the image type of an empty series.")

    def get_acquisition(self, idx: int) -> Acquisition:
        """
        :param idx: int:
            The index of the acquisition you want.
        :return: Acquisition:
            The acquisition at the provided index.
        """
        return self[idx]

    def set_acquisition(self, acq: Acquisition, idx: int) -> None:
        """
        :param acq: Acquisition:
            The acquisition to set.
        :param idx: int:
            Where you want to put the acquisition. The image of the acquisition must have the same shape and datatype
             as the rest of those in the series.
        :return: None.
        """
        if isinstance(acq, Acquisition) \
                and acq.image_shape() == self.image_shape() and acq.image_dtype() == self.image_dtype():
            self.__acquisitions[idx] = acq

        else:
            raise Exception("Error: Unable to append to AcquisitionSeries, either the provided argument is not of type "
                            "Acquisition, the image is the wrong shape, or the image uses the wrong datatype.")

    def downsample(self) -> None:
        """
        Downsample all images in the stack by a factor of 2. Useful for saving space.

        :return: None. Operation performed inplace.
        """
        for acq in self.__acquisitions:
            acq.downsample()

    def get_image_stack(self, dtype: type = None) -> np.ndarray:
        """
        Build and return an 3-dimensional images stack array with the images in the series.
        :param dtype: type (optional; default is None):
            The datatype to use. If omitted or None, then the datatype defaults to the series' current image datatype as
             found with image_dtype().
        :return: np.ndarray:
            A 3-dimensional numpy array containing a stack of the all the images in the series.
        """
        if self.length() > 1:

            # Preallocate
            number_images = self.length()
            image_shape = np.shape(self[0].get_image())
            if dtype is None:
                dtype = self.image_dtype()
            image_stack_arr = np.full(shape=(number_images, image_shape[0], image_shape[1]), fill_value=np.nan,
                                      dtype=dtype)

            # Loop through and actually fill in the stack.
            for i, acq in enumerate(self):
                image_stack_arr[i] = acq.get_image()

            return image_stack_arr

        else:
            raise Exception("Error: get_image_stack() requires the AcquisitionSeries contains at least 2 acquisitions "
                            "in order to generate an image stack. Use "
                            "AcquisitionSeries.get_acquisition(idx=0).get_image() to get an array of the lone "
                            "first image in the series.")

    def align(self) -> AcquisitionSeries:
        """
        Align the images in the acquisition series.

        Image shifts are estimated using Hyperspy's estimate_shift2D() function. This function uses a phase correlation
         algorithm based on the following paper:
            Schaffer, Bernhard, Werner Grogger, and Gerald Kothleitner. “Automated Spatial Drift Correction for EFTEM
                Image Series.” Ultramicroscopy 102, no. 1 (December 2004): 27–36.

        :return: AcquisitionSeries:
            A new acquisition series containing the aligned images.
        """
        turn_off_hyperspy_warnings()

        # Build a Hyperspy signal from the image stack, align it, and convert it back to a numpy array.
        image_stack = hs.signals.Signal2D(self.get_image_stack())
        if self.length() > 20:
            # For large series perform the image alignment step in parallel.
            image_stack.align2D(parallel=True)  # In-place.
        else:
            image_stack.align2D()  # In-place.
        image_stack = np.asarray(image_stack, dtype=self.image_dtype())

        # Build a new acquisition series with the results.
        result = AcquisitionSeries()
        for i in range(self.length()):
            # Build a new acquisition with the aligned image and old metadata and add it to the series.
            new_acq = Acquisition(image_stack[i])
            new_acq._set_metadata(metadata=self[i].get_metadata())
            result.append(new_acq)

        return result

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
            raise Exception("AcquisitionSeries.save_as_mrc() requires at least one image exists in the series.")

        # In case we are missing the .mrc extension, add it on.
        if out_file[-4:] != ".mrc":
            out_file = out_file + ".mrc"

        with mrcfile.new(out_file, overwrite=True) as mrc:
            mrc.set_data(self.get_image_stack())  # Write image data
            # Until we know how to build our own extended header, just use a stock one  # TODO: Write metadata to header
            mrc.set_extended_header(get_stock_mrc_extended_header())
        warnings.warn("Acquisition metadata not yet stored in MRC images, for now we are just using a stock header!")

    def __iter__(self):
        return AcquisitionSeriesIterator(self)

    def __getitem__(self, i):
        return self.__acquisitions[i]


if __name__ == "__main__":
    """
    Testing.
    """
    acq_series = AcquisitionSeries()
    acq_series.append(Acquisition(None))

    print(acq_series.image_shape())
    print(acq_series.get_acquisition(0).image_shape())
    print(acq_series.image_dtype())
    acq_series.append(Acquisition(None))
    acq_series.append(Acquisition(None))

    image_stack_arr_ = acq_series.get_image_stack()
    print(np.shape(image_stack_arr_))

    acq_series.downsample()

    image_stack_arr_ = acq_series.get_image_stack()
    print(np.shape(image_stack_arr_))

    print(acq_series.get_acquisition(idx=0).get_metadata())

    print("\nTesting iteration:")
    for c, acq_ in enumerate(acq_series):
        print(c)
        print(acq_)

    new_series = acq_series.align()

    print(new_series)

    # out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve().parent.resolve() / "test" \
    #           / "interface" / "test_images"
    # out_file_ = out_dir / "mrc_test_stack.mrc"
    # acq_series.save_as_mrc(out_file=out_file_)
