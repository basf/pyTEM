"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import warnings
import numpy as np
from datetime import datetime
from tifffile import tifffile


def _build_metadata_dictionary(tm_acquisition_object):
    """
    Build a metadata dictionary from a Thermo Fisher Acquisition object.

    :param tm_acquisition_object: A Thermo Fisher Acquisition object.

    :return: dictionary:
        A python dictionary with all the metadata.
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
            'Date':                     str(date_time.date()),  # Object of type 'date' is not JSON serializable
            'Time':                     str(date_time.time()),  # Object of type 'time' is not JSON serializable
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
    A simplified, forward facing Acquisition class.

    Public Attributes:
        None

    Protected Attributes:
        None.

    Private Attributes:
        __image:      numpy.ndarray:   The image itself, as a numpy array.
        __metadata:   dictionary:      All the image metadata (describes and gives information about the __image).
    """

    def __init__(self, tm_acquisition_object):
        """
        :param tm_acquisition_object: A Thermo Fisher Acquisition object.
        """
        try:
            self.__image = np.asarray(tm_acquisition_object.AsSafeArray)
            self.__metadata = _build_metadata_dictionary(tm_acquisition_object=tm_acquisition_object)
        except AttributeError:
            self.__image = np.random.random((1024, 1024))  # A random 1k image.
            self.__metadata = {'PixelSize': (1, 1)}  # Pixel size metadata required to save image as tif.
            warnings.warn("The Acquisition() constructor received an invalid Thermo Fisher Acquisition object. The "
                          "returned Acquisition object contains a random 1k image with no metadata.")
        except BaseException as e:
            raise e

    def _set_image(self, image):
        """
        Set the image attribute. This method is probably only helpful for testing.
        :param image: 2D numpy.ndarray:
            The new image.
        :return: None.
        """
        self.__image = image

    def _set_metadata(self, metadata):
        """
        Set the metadata attribute. This method is probably only helpful for testing.
        :param metadata: dict:
            The new metadata.
        :return: None.
        """
        self.__metadata = metadata

    def get_image(self):
        """
        :return: image: numpy.ndarray:
            The image, as a 2D numpy array.
        """
        return self.__image

    def get_metadata(self):
        """
        :return: metadata: dictionary:
            A dictionary containing the image metadata (describes and gives information about the image itself).
            The returned dictionary can then be searched for the entries of interest, or further modified as required.
        """
        return self.__metadata

    def update_metadata_parameter(self, key, value, force=False):
        """
        Update an existing metadata parameter.

        :param key: str:
            Metadata dictionary key.
            Key must exist otherwise no changes will be made (can be overridden with the force parameter).
        :param value:
            The corresponding value to store in the metadata dictionary.
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
            print("Error: Unable to update metadata, key '" + key + "' not found in metadata dictionary.")
            return 1

    def add_metadata_parameter(self, key, value):
        """
        Add a new parameter to the metadata dictionary.

        :param key: str:
            Metadata dictionary key.
            Key must exist otherwise no changes will be made (can be overridden with the force parameter).
        :param value:
            The corresponding value to store in the metadata dictionary.

        :return: int:
            0: Success. Key value pair added successfully.
            1: No changes made.
        """
        return self.update_metadata_parameter(key=key, value=value, force=True)

    def save_as_tif(self, out_file):
        """
        Save the acquisition as a tif image.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .tif extension, otherwise it will be added automatically.

        :return: None.
        """
        out_file = str(out_file)  # Encase we received a path.

        # In case we are missing the .tif extension, add it on.
        if out_file[-4:] != ".tif":
            out_file = out_file + ".tif"

        pixel_size_x_in_cm = 100 * self.get_metadata()['PixelSize'][0]  # m -> cm
        pixel_size_y_in_cm = 100 * self.get_metadata()['PixelSize'][1]  # m -> cm

        tifffile.imwrite(out_file, data=self.get_image(), metadata=self.get_metadata(),
                         resolution=(1/pixel_size_x_in_cm, 1/pixel_size_y_in_cm, 'CENTIMETER'))


if __name__ == "__main__":
    import pathlib
    import hyperspy.api as hs

    out_dir = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve().parent.resolve() / "test" \
                / "interface" / "test_images"

    acq = Acquisition(None)
    acq.update_metadata_parameter(key='PixelSize', value=(6.79e-9, 6.79e-9))
    print(acq.get_metadata())

    # print(out_dir)
    out_file_ = out_dir / "random_image1.tif"
    print("Saving image as: " + str(out_file_))
    acq.save_as_tif(out_file=out_file_)

    # Load back in the file and look at the metadata
    print("Reading back in " + str(out_file_))
    ref_image = hs.load(out_file_)

    original_metadata = ref_image.original_metadata
    print(original_metadata)
    print(type(original_metadata))
    print(original_metadata['ResolutionUnit'])
