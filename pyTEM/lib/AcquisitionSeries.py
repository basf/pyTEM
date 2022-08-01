"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

# Required to type hint that a method is returning an instance of the enclosing class.
from __future__ import annotations

import os
import pathlib
import warnings
import mrcfile

import numpy as np
import hyperspy.api as hs

from typing import Union, Tuple
from tifffile import tifffile
from tifffile.tifffile import RESUNIT

from pyTEM.lib.RedirectStdStreams import RedirectStdStreams
from pyTEM.lib.hs_metadata_to_dict import hs_metadata_to_dict
from pyTEM.lib.rgb_to_greyscale import rgb_to_greyscale
from pyTEM.lib.stock_mrc_extended_header.get_stock_mrc_header import get_stock_mrc_extended_header
from pyTEM_scripts.lib.micro_ed.hyperspy_warnings import turn_off_hyperspy_warnings
from pyTEM.lib.make_dict_jsonable import make_dict_jsonable
from pyTEM.lib.Acquisition import Acquisition


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
     and datatype as that of the first acquisition in the series (consistent resolution (scale) is not enforced because
     sometimes the resolution needs to be added manually to the image files or acquisition objects, and we don't want
     to force the user to manually set the resolution in every file/acquisition they want to load into the series).

    This class is especially helpful for managing image stacks, including reading and saving to file.

    Notice that because the underlying Acquisition class only supports greyscale images, the same is true for
     AcquisitionSeries objects. When initializing from an RGB image file/stack, the image(s) is(are) converted to
     unsigned 8-bit greyscale.

    Public Attributes:
        None

    Protected Attributes:
        None.

    Private Attributes:
        __acquisitions:      Python list:   An list of Acquisition objects.
    """

    def __init__(self, source: Union[str, pathlib.Path, np.ndarray] = None):
        """
        :param source: From what to initialize the AcquisitionSeries (optional; default is None).
            Supported sources include:

                - A string or path object: In which case the AcquisitionSeries() object will be initialized from file
                    (probably this file contains an image stack, but it could also be a single-image file in which case
                    the returned series will only be 1 acquisition long). The file's metadata will be loaded into each
                    acquisition. When initializing from an RGB image/stack file, the image(s) is(are) converted to
                    unsigned 8-bit greyscale.
                    
                - A 2-dimensional array: In which case the returned series will only be 1 acquisition long (the single
                    acquisition's metadata will be initialized to an empty dictionary). Array must be representing
                    a 2-dimensional greyscale image.

                - A 3-dimensional array: In which case we assume an image stack and iterate over the first axis,
                    loading in 2-dimensional images. Each acquisition's metadata will be initialized to an empty
                    dictionary. Array must be representing a stack of 2-dimensional greyscale image.

                - None: In which case, we return an empty AcquisitionSeries abject. Just like all AcquisitionSeries
                    objects, this empty series can always be appended to later.
        """
        self.__acquisitions = []

        if source is None:
            return  # We are done

        elif isinstance(source, str) or isinstance(source, pathlib.Path):
            # Try to load from file

            # First, check to see if it is an MRC file.
            try:
                # Because mrcfile.validate() prints a lot of stuff that is not helpful, temporarily redirect stdout.
                devnull = open(os.devnull, 'w')
                with RedirectStdStreams(stdout=devnull, stderr=devnull):
                    mrc_file = mrcfile.validate(source)
            except BaseException as e:
                mrc_file = False
                warnings.warn("Error ignored in AcquisitionSeries() while trying to check if the input file was an "
                              "MRC file: " + str(e))

            if mrc_file:
                # Then it is an MRC file, open with mrcfile.
                # No need to worry about checking for RGB -> storing RGB images in the MRC file format would
                #  deviate from MRC standards (and so we naively assume that nobody does it)!
                with mrcfile.open(source) as mrc:
                    image_stack_arr = mrc.data
                    metadata = {}
                    # TODO: Figure out how to read in metadata from MRC file header
                    warnings.warn("We haven't learned how to read MRC file headers yet, so the Acquisition's in the"
                                  "returned AcquisitionSeries object have no metadata!")

            else:
                # Let's see if it is something Hyperspy can load.
                try:
                    hs_data = hs.load(str(source))

                    if hs_data.is_rgb or hs_data.is_rgba or hs_data.is_rgbx:
                        warnings.warn("Acquisition objects do not support RGB images, converting image to unsigned "
                                      "8-bit greyscale.")
                        hs_data.change_dtype('uint8')

                        # Ensure we have the expected dimensionality otherwise the RGB -> greyscale conversion is not
                        # going to work.
                        if hs_data.data.ndim == 3:
                            # Then we have a single 2D image.
                            image_stack_arr = rgb_to_greyscale(rgb_image=hs_data.data)

                        elif hs_data.data.ndim == 4:
                            # Then we have an image stack, loop through and covert to grayscale.
                            num_images, x_dim, y_dim, channels = np.shape(hs_data.data)
                            image_stack_arr = np.full(shape=(num_images, x_dim, y_dim), fill_value=np.nan,
                                                      dtype=np.uint8)
                            for i in range(num_images):
                                image_stack_arr[i] = rgb_to_greyscale(rgb_image=hs_data.data[i])

                        else:
                            # Then we have a problem.
                            raise Exception("AcquisitionSeries is unable to interpret " + str(hs_data.ndim - 1)
                                            + "-dimensional RGB data.")

                    else:
                        # Image is already greyscale, we are good to go.
                        image_stack_arr = hs_data.data

                except BaseException as e:
                    warnings.warn("The Acquisition() constructor received an invalid source.")
                    raise e

                # Try to load metadata.
                try:
                    metadata = hs_metadata_to_dict(hs_data.metadata)
                    # And don't forget to include the original metadata.
                    metadata.update(hs_metadata_to_dict(hs_data.original_metadata))
                except BaseException as e:
                    warnings.warn("Unable to extract metadata from source: " + str(e))
                    metadata = {}

            if image_stack_arr.ndim == 2:
                # Then we have a single image.
                acq = Acquisition(source=image_stack_arr)
                acq._set_metadata(metadata)
                self.append(acq=acq)

            elif image_stack_arr.ndim == 3:
                # Then we have an image stack, look through and append acquisitions.
                num_images = np.shape(image_stack_arr)[0]
                for i in range(num_images):
                    acq = Acquisition(source=image_stack_arr[i])
                    acq._set_metadata(metadata)
                    self.append(acq=acq)

        elif isinstance(source, np.ndarray):
            # Initialize from array. No need to worry about metadata.

            if source.ndim == 2:
                # Then the array only contains a single image.
                self.append(acq=Acquisition(source))

            elif source.ndim == 3:
                # Then we have an image stack, loop through all the images in the stack, appending them onto to
                #  the series.
                for i in range(np.shape(source)[0]):
                    self.append(acq=Acquisition(source[i]))

            else:
                # Invalid dimension, panic.
                raise Exception("AcquisitonSeries() expected a 2 or 3 dimensional source, but the provided source is "
                                "of dimension " + str(source.ndim) + ".")

        else:
            raise Exception("The type of the source received by the AcquisitionSeries() constructor is invlaid.")

    def append(self, acq: Acquisition) -> None:
        """
        Add a new acquisition to the end of the series. Notice you can only append single acquisitions.
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
            raise Exception("Error: Unable to set Acquisition, either the provided argument is not of type "
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
            new_acq = Acquisition(source=image_stack[i])
            new_acq._set_metadata(metadata=self[i].get_metadata())
            result.append(acq=new_acq)

        return result

    def save_as_tif(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition as a TIFF file.

        Metadata (including resolution) is based on the first image in the series.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .tif or .tiff extension, otherwise .tif will be added automatically.

        :return: None.
        """
        out_file = str(out_file)  # Encase we received a path.

        if self.length() < 0:
            raise Exception("AcquisitionSeries.save_as_tif() requires at least one image exists in the series.")

        # In case we are missing the .tif extension, add it on.
        if out_file[-4:] != ".tif" and out_file[-5:] != ".tiff":
            out_file = out_file + ".tif"

        # Try to determine the image resolution.
        if "XResolution" in self[0].get_metadata().keys() and "YResolution" in self[0].get_metadata().keys() \
                and "ResolutionUnit" in self[0].get_metadata().keys():
            # If the required TIFF XResolution and YResolution tags already exist, then go ahead and use them.
            # The TIFF types of the XResolution and YResolution tags are RATIONAL (5) which is defined in the TIFF
            #  specification as "two LONGs: the first represents the numerator of a fraction; the second, the
            #  denominator." Notice we are computing the inverse here and will invert back when we save.
            pixel_size_x = float(self[0].get_metadata()['XResolution'][1] /
                                 self[0].get_metadata()['XResolution'][0])
            pixel_size_y = float(self[0].get_metadata()['YResolution'][1] /
                                 self[0].get_metadata()['YResolution'][0])
            resolution_unit = self[0].get_metadata()['ResolutionUnit']

        elif "PixelSize" in self[0].get_metadata().keys():
            # Maybe we have pixel size data from the TM acq object.
            pixel_size_x = float(100 * self[0].get_metadata()['PixelSize'][0])  # m -> cm
            pixel_size_y = float(100 * self[0].get_metadata()['PixelSize'][1])  # m -> cm
            resolution_unit = RESUNIT.CENTIMETER

        else:
            # Give up, just save without setting the resolution.
            warnings.warn("save_as_tif() could not determine the pixel size, resolution not set in " + str(out_file))
            tifffile.imwrite(out_file, data=self.get_image_stack(), photometric='minisblack',
                             metadata=make_dict_jsonable(self[0].get_metadata()))
            return

        tifffile.imwrite(out_file, data=self.get_image_stack(), metadata=make_dict_jsonable(self[0].get_metadata()),
                         resolution=(1 / pixel_size_x, 1 / pixel_size_y, resolution_unit),
                         photometric='minisblack')

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

    def save_to_file(self, out_file: Union[str, pathlib.Path], extension: str = None) -> None:
        """
        Save the acquisition series to file.

        :param out_file: str or path:
            Out file path (the file path where you want to save the series), optionally including the file extension.
        :param extension: str (optional; default is None):
            The extension of the file that defines the file format.
            Allowable string values are: {'hspy', 'hdf5', 'rpl', 'msa', 'unf', 'blo', 'emd', common image
             extensions e.g. 'tiff', 'png', 'jpeg', etc., and 'mrc'}. If omitted, the extension is determined from the
              following list in this order:
                1. the filename
                2. Signal.tmp_parameters.extension
                3. 'hspy' (the default extension)

        :return: None.
        """
        out_file = str(out_file)  # Encase we received a path.

        if out_file[-4:] == ".tif" or extension == 'tif' or out_file[-5:] == ".tiff" or extension == 'tiff':
            self.save_as_tif(out_file)

        elif out_file[-4:] == ".mrc" or extension == 'mrc':
            self.save_as_mrc(out_file)

        else:
            # Hope for the best...
            im = hs.signals.Signal2D(self.get_image_stack())
            im.save(filename=out_file, overwrite=True)
            warnings.warn("Acquisition series metadata not saved in " + str(out_file))

    def __iter__(self) -> AcquisitionSeriesIterator:
        return AcquisitionSeriesIterator(self)

    def __getitem__(self, i) -> Acquisition:
        return self.__acquisitions[i]


if __name__ == "__main__":
    """
    Testing.
    """
    out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve() / "test" / "test_images"
    in_file_ = out_dir / "RGB" / "S1 0_0.tif"
    # in_file_ = out_dir / "RGB" / "rgb_image_stack.tif"
    # in_file_ = out_dir / "2_11.tif"
    # in_file_ = out_dir / "cat.jpeg"
    acq_series = AcquisitionSeries(in_file_)

    print(acq_series)
    print("Series length: " + str(acq_series.length()))
    print(acq_series[0])
    print("Series datatype: " + str(acq_series.image_dtype()))
    print(acq_series[0].get_image())
    print(acq_series[0].get_metadata())
    print("Average intensity of the first image: " + str(np.mean(acq_series[0].get_image())))

    acq_series[0].show_image()
    # acq_series.append(Acquisition(None))
    #
    # print(acq_series.image_shape())
    # print(acq_series.get_acquisition(0).image_shape())
    # print(acq_series.image_dtype())
    # acq_series.append(Acquisition(None))
    # acq_series.append(Acquisition(None))
    #
    # image_stack_arr_ = acq_series.get_image_stack()
    # print(np.shape(image_stack_arr_))
    #
    # # acq_series.downsample()
    #
    # image_stack_arr_ = acq_series.get_image_stack()
    # print(np.shape(image_stack_arr_))
    #
    # print(acq_series.get_acquisition(idx=0).get_metadata())

    # in_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve() \
    #     / "test" / "interface" / "test_images"
    # acq_series.append(Acquisition(str(in_dir) + "/p2v1 1_25x 14.tif"))
    # acq_series.append(Acquisition(str(in_dir) + "/p2v1 1_25x 13.tif"))
    # acq_series.append(Acquisition(str(in_dir) + "/p2v1 1_25x 12.tif"))

    # print("\nTesting iteration:")
    # for c, acq_ in enumerate(acq_series):
    #     print(c)
    #     print(acq_)

    # new_series = acq_series.align()
    # print(new_series)

    # print("Saving as MRC:")
    # out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve().parent.resolve() / "test" \
    #           / "interface" / "test_images"
    # out_file_ = out_dir / "mrc_test_stack.mrc"
    # acq_series.save_as_mrc(out_file=out_file_)

    # print("Saving as TIF:")
    # out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve().parent.resolve() / "test" \
    #           / "interface" / "test_images"
    # out_file_ = out_dir / "tif_test_stack.tif"
    # acq_series.save_as_tif(out_file=out_file_)
