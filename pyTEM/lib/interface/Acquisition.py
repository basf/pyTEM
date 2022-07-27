"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import pathlib
import warnings
import mrcfile

import numpy as np
import hyperspy.api as hs
from typing import Union, Dict, Any, Tuple
from datetime import datetime

from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.colors import Colormap
from numpy.typing import ArrayLike
from tifffile import tifffile
from tifffile.tifffile import RESUNIT

from pyTEM.lib.interface.RedirectStdStreams import RedirectStdStreams
from pyTEM.lib.interface.hs_metadata_to_dict import hs_metadata_to_dict
from pyTEM.lib.interface.make_dict_jsonable import make_dict_jsonable
from pyTEM.lib.interface.stock_mrc_extended_header.get_stock_mrc_header import get_stock_mrc_extended_header


def _build_metadata_dict_from_tm(tm_acquisition_object) \
        -> Dict[str, Union[str, int, float, datetime.time, datetime.date]]:
    """
    Build a metadata dictionary from a Thermo Fisher Acquisition object.

    :param tm_acquisition_object: A Thermo Fisher Acquisition object.

    :return: dictionary:
        A python dictionary with all the metadata.
        Value restrictions (str, int, float) are to ensure types are JSON serializable.
    """
    # The microscope timestamps acquisitions with an epoch in microseconds.
    epoch = int(float(tm_acquisition_object.Metadata[23].ValueAsString) / 1e6)  # Covert to epoch in seconds
    date_time = datetime.fromtimestamp(epoch)

    return {'DetectorName':             tm_acquisition_object.Metadata[0].ValueAsString,
            'Sampling':                 int(tm_acquisition_object.Metadata[1].ValueAsString),
            'ReadoutArea':              ([[int(tm_acquisition_object.Metadata[3].ValueAsString),
                                           int(tm_acquisition_object.Metadata[4].ValueAsString)],
                                          [int(tm_acquisition_object.Metadata[5].ValueAsString),
                                           int(tm_acquisition_object.Metadata[6].ValueAsString)]]),
            'ExposureTime':             float(tm_acquisition_object.Metadata[8].ValueAsString),
            'DarkGainCorrectionType':   tm_acquisition_object.Metadata[9].ValueAsString,
            'ShuttersType':             tm_acquisition_object.Metadata[10].ValueAsString,
            'ShuttersPosition':         tm_acquisition_object.Metadata[11].ValueAsString,
            'AcquisitionUnit':          tm_acquisition_object.Metadata[12].ValueAsString,
            'BitsPerPixel':             int(tm_acquisition_object.Metadata[13].ValueAsString),
            'Encoding':                 tm_acquisition_object.Metadata[14].ValueAsString,
            'ImageSize':                (int(tm_acquisition_object.Metadata[15].ValueAsString),
                                         int(tm_acquisition_object.Metadata[16].ValueAsString)),
            'Offset':                   (float(tm_acquisition_object.Metadata[17].ValueAsString),
                                         float(tm_acquisition_object.Metadata[18].ValueAsString)),
            'PixelSize':                (float(tm_acquisition_object.Metadata[19].ValueAsString),
                                         float(tm_acquisition_object.Metadata[20].ValueAsString)),
            'PixelUnit':                (tm_acquisition_object.Metadata[21].ValueAsString,
                                         tm_acquisition_object.Metadata[22].ValueAsString),
            'Epoch':                    epoch,
            'Date':                     date_time.date(),
            'Time':                     date_time.time(),
            'MaxPossiblePixelValue':    int(tm_acquisition_object.Metadata[24].ValueAsString),
            'SaturationPoint':          int(tm_acquisition_object.Metadata[25].ValueAsString),
            'DigitalGain':              int(tm_acquisition_object.Metadata[26].ValueAsString),
            'CombinedSubFrames':        int(tm_acquisition_object.Metadata[27].ValueAsString),
            'CommercialName':           tm_acquisition_object.Metadata[28].ValueAsString,
            'FrameID':                  int(tm_acquisition_object.Metadata[29].ValueAsString),
            'TransferOK':               tm_acquisition_object.Metadata[30].ValueAsString,
            'PixelValueToCameraCounts': int(tm_acquisition_object.Metadata[31].ValueAsString),
            'ElectronsCounted':         tm_acquisition_object.Metadata[32].ValueAsString,
            'AlignIntegratedImage':     tm_acquisition_object.Metadata[33].ValueAsString}


class Acquisition:
    """
    A simplified, forward facing Acquisition class. This class holds, and allows the user to interact
     with, the results of a single acquisition (single 2D image).

    Public Attributes:
        None

    Protected Attributes:
        None.

    Private Attributes:
        __image:      numpy.ndarray:   The image itself, as a numpy array.
        __metadata:   dictionary:      All the image metadata (describes and gives information about the __image).
    """

    def __init__(self, source: Union[str, pathlib.Path, Any] = None):
        """
        :param source: From what to initialize the Acquisition (optional; default is None).
            Supported sources include:
                - A string or path object: In which case the Acquisition() object will be initialized from file.
                - A Thermo Fisher Acquisition object: In which case we will initialize from that.
                - A 2D array: In which case we will initialize from that (metadata will be initialized to an empty
                    dictionary).
            If omitted or None, then we return a dummy Acquisition object with a random 16-bit image (good for testing).
        """
        if source is None:
            # Just return a random image, this is helpful for testing.
            self.__image = np.random.random((1024, 1024))  # A random 1k image.
            self.__image = (65535 * self.__image).astype(np.int16)  # Covert to 16-bit
            self.__metadata = {}
            warnings.warn("The Acquisition() constructor received None. The returned Acquisition object contains a "
                          "random 1k image with no metadata.")
            return

        try:
            if isinstance(source, str) or isinstance(source, pathlib.Path):
                # Try to load from file

                # First, check to see if it is an MRC file.
                try:
                    # Because mrcfile.validate() prints a lot of stuff that is not helpful, temporarily redirect stdout.
                    devnull = open(os.devnull, 'w')
                    with RedirectStdStreams(stdout=devnull, stderr=devnull):
                        mrc_file = mrcfile.validate(source)
                except BaseException as e:
                    mrc_file = False
                    warnings.warn("Error ignored in Acquisition() while trying to check if the source was an MRC file: "
                                  + str(e))

                if mrc_file:
                    # Then it is an MRC file, open with mrcfile
                    with mrcfile.open(source) as mrc:
                        self.__image = mrc.data
                        # TODO: Figure out how to read in metadata from MRC file header
                        warnings.warn("We haven't learned how to read MRC file headers yet, so the returned "
                                      "Acquisition object has no metadata!")
                        self.__metadata = {}

                else:
                    # Let's see if it is something hyperspy can load
                    image = hs.load(source)
                    self.__image = image.data

                    try:
                        # Try to load metadata.
                        self.__metadata = hs_metadata_to_dict(image.metadata)
                        # And don't forget to include the original metadata.
                        self.__metadata.update(hs_metadata_to_dict(image.original_metadata))
                    except BaseException as e:
                        self.__metadata = {}
                        warnings.warn("Unable to extract metadata from source: " + str(e))

                    try:
                        # If the file was generated from an Acquisition object, then a bunch of metadata will be in
                        #  the ImageDescription field as a string, and we need to turn it back into a dictionary.
                        if 'ImageDescription' in self.__metadata.keys():
                            self.__metadata['ImageDescription'] = eval(self.__metadata['ImageDescription'])
                    except BaseException as e:
                        warnings.warn("Unable to evaluate the metadata in the ImageDescription field: " + str(e))

            elif isinstance(source, np.ndarray):
                # Initialize from array.
                self.__image = source
                self.__metadata = {}

            else:
                # Try to load from a Thermo Fisher Acquisition object.
                # Notice that we load as a 16-bit image.
                # Notice that we will to flip and then rotate the image to match what is shown on the FluCam.
                self.__image = np.rot90(np.flip(np.asarray(source.AsSafeArray, dtype=np.int16), axis=1))
                self.__metadata = _build_metadata_dict_from_tm(tm_acquisition_object=source)

        except BaseException as e:
            warnings.warn("The Acquisition() constructor received an invalid source.")
            raise e

        if self.__image.ndim != 2:
            raise Exception("The Acquisition class is only meant for single 2-dimensional images, however the source "
                            "data is not 2-dimensional. For image stacks, please use the AcquisitionSeries class.")

    def _set_image(self, image: ArrayLike) -> None:
        """
        Set the image attribute. This method is probably only helpful for testing.
        :param image: 2D numpy.ndarray:
            The new image.
        :return: None.
        """
        self.__image = image

    def _set_metadata(self, metadata: Dict[str, Union[str, int, float]]) -> None:
        """
        Set the metadata attribute. This method is probably only helpful for testing.
        :param metadata: dict:
            The new metadata.
        :return: None.
        """
        self.__metadata = metadata

    def get_image(self) -> np.ndarray:
        """
        :return: image: numpy.ndarray:
            The image, as a 2D numpy array.
        """
        return self.__image

    def get_metadata(self) -> Dict[str, Union[str, int, float, ArrayLike]]:
        """
        :return: metadata: dictionary:
            A dictionary containing the image metadata (describes and gives information about the image itself).
            The returned dictionary can then be searched for the entries of interest, or further modified as required.
        """
        return self.__metadata

    def show_image(self, cmap: Union[str, Colormap] = "Greys_r") -> None:
        """
        Display the image.
        :param cmap: str or Colormap (optional; default is 'Greys_r'):
            The colour map to use.
        :return: None. Image is shown in a pop-up window.
        """
        plt.imshow(self.__image, cmap=cmap)
        plt.show()

    def update_metadata_parameter(self, key: str, value: Union[str, int, float, ArrayLike], force: bool = False) -> int:
        """
        Update an existing metadata parameter.

        :param key: str:
            Metadata dictionary key.
            Key must exist otherwise no changes will be made (can be overridden with the force parameter).
        :param value:
            The corresponding value to store in the metadata dictionary. Must be JSON serializable.
        :param force: bool (optional; default is False)
            If True, the key value pair will be force added, even if the provided key doesn't currently exist with the
             metadata dictionary.

        :return: int:
            0: Success. Value updated successfully.
            1: No changes made.
        """
        key = str(key)
        if key in self.__metadata.keys() or force:
            self.__metadata[key] = value
            return 0
        else:
            print("Unable to update metadata, key '" + key + "' not found in metadata dictionary.")
            return 1

    def add_metadata_parameter(self, key: str, value: Union[str, int, float, ArrayLike]) -> int:
        """
        Add a new parameter to the metadata dictionary.

        :param key: str:
            Metadata dictionary key.
            Key must exist otherwise no changes will be made (can be overridden with the force parameter).
        :param value:
            The corresponding value to store in the metadata dictionary. Must be JSON serializable.

        :return: int:
            0: Success. Key value pair added successfully.
            1: No changes made.
        """
        return self.update_metadata_parameter(key=key, value=value, force=True)

    def image_shape(self) -> Tuple[int, int]:
        """
        :return: (int, int):
            Image shape, in pixels.
        """
        return np.shape(self.get_image())

    def image_dtype(self) -> type:
        """
        :return: type:
            The image datatype.
        """
        return type(self.get_image()[0][0])

    def downsample(self) -> None:
        """
        Downsample the image by a factor of 2. Useful for saving space.

        Image size will change (obviously), but the image datatype should remain the same.

        :return: None. Operation performed inplace.
        """
        data_type = self.image_dtype()
        width, height = np.shape(self.get_image())
        image = Image.fromarray(self.get_image())
        resized_image = image.resize(size=(int(width / 2), int(height / 2)), resample=Image.BILINEAR)
        self.__image = np.array(resized_image, dtype=data_type)

    def save_as_tif(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition as a TIFF file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .tif or .tiff extension, otherwise .tif will be added automatically.

        :return: None.
        """
        out_file = str(out_file)  # Encase we received a path.

        # In case we are missing the .tif extension, add it on.
        if out_file[-4:] != ".tif" and out_file[-5:] != ".tiff":
            out_file = out_file + ".tif"

        # Try to determine the image resolution.
        if "XResolution" in self.get_metadata().keys() and "YResolution" in self.get_metadata().keys() \
                and "ResolutionUnit" in self.get_metadata().keys():
            # If the required TIFF XResolution and YResolution tags already exist, then go ahead and use them.
            # The TIFF types of the XResolution and YResolution tags are RATIONAL (5) which is defined in the TIFF
            #  specification as "two LONGs: the first represents the numerator of a fraction; the second, the
            #  denominator." Notice we are computing the inverse here and will invert back when we save.
            pixel_size_x_in_cm = float(self.get_metadata()['XResolution'][1] / self.get_metadata()['XResolution'][0])
            pixel_size_y_in_cm = float(self.get_metadata()['YResolution'][1] / self.get_metadata()['YResolution'][0])
            resolution_unit = self.get_metadata()['ResolutionUnit']

        elif "PixelSize" in self.get_metadata().keys():
            # Maybe we have pixel size data from the TM acq object.
            pixel_size_x_in_cm = float(100 * self.get_metadata()['PixelSize'][0])  # m -> cm
            pixel_size_y_in_cm = float(100 * self.get_metadata()['PixelSize'][1])  # m -> cm
            resolution_unit = RESUNIT.CENTIMETER

        else:
            # Give up, just save without setting the resolution.
            warnings.warn("save_as_tif() could not determine the pixel size, resolution not set in " + str(out_file))
            tifffile.imwrite(out_file, data=self.get_image(), metadata=make_dict_jsonable(self.get_metadata()),
                             photometric='minisblack')
            return

        tifffile.imwrite(out_file, data=self.get_image(), metadata=self.get_metadata(), photometric='minisblack',
                         resolution=(1 / pixel_size_x_in_cm, 1 / pixel_size_y_in_cm, resolution_unit))

    def save_as_mrc(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition as an MRC file.

        This method only writes the image array to file, it doesn't mess around with the header.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .mrc extension, otherwise it will be added automatically.

        :return: None.
        """
        out_file = str(out_file)  # Encase we received a path.

        # In case we are missing the .mrc extension, add it on.
        if out_file[-4:] != ".mrc":
            out_file = out_file + ".mrc"

        with mrcfile.new(out_file, overwrite=True) as mrc:
            mrc.set_data(self.get_image())
            # Until we know how to build our own extended header, just use a stock one  # TODO: Write metadata to header
            mrc.set_extended_header(get_stock_mrc_extended_header())
        warnings.warn("Acquisition metadata not yet stored in MRC images, for now we are just using a stock header!")

    def save_to_file(self, out_file: Union[str, pathlib.Path], extension: str = None) -> None:
        """
        Save the acquisition to file.

        :param out_file: str or path:
            Out file path (the file path where you want to save the acquisiton), optionally including the file
             extension.
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
            im = hs.signals.Signal2D(self.get_image())
            im.save(filename=out_file, overwrite=True)
            warnings.warn("Acquisition metadata not saved in " + str(out_file))


if __name__ == "__main__":
    """
    Testing
    """

    out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve() / "test" / "interface" / \
        "test_images"
    # in_file_ = out_dir / "Tiltseies_SAD40_-20-20deg_0.5degps_1.1m.tif"
    in_file_ = out_dir / "2_14.tif"
    # out_file_ = out_dir / "checking_if_metadata_saved.tif"

    # acq = Acquisition(None)
    acq = Acquisition(in_file_)
    acq_metadata = acq.get_metadata()
    print("Metadata:")
    print(acq_metadata)
    print("Resolution unit:")
    print(acq_metadata['ResolutionUnit'])
    # print(type(acq_metadata['ResolutionUnit']))
    # print(acq_metadata['ResolutionUnit'] == RESUNIT.CENTIMETER)
    # print(acq.get_image().dtype)
    # acq.show_image()

    # acq.save_as_mrc(out_file=out_file_)
    # acq.save_as_tif(out_file=out_file_)

    # img = acq.get_image()
    # print(np.shape(img))
