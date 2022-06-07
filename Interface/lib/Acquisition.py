"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import numpy as np


def build_metadata_dictionary(tm_acquisition_object):
    """
    Build a metadata dictionary from a Thermo Fisher Acquisition object.

    :param tm_acquisition_object: A Thermo Fisher Acquisition object.

    :return: dictionary:
        A python dictionary with all the metadata.
    """
    return {'DetectorName':             tm_acquisition_object.Metadata[0].ValueAsString,
            'Binning':                  int(tm_acquisition_object.Metadata[1].ValueAsString),
            'ReadoutArea':              ([[tm_acquisition_object.Metadata[3].ValueAsString,
                                           tm_acquisition_object.Metadata[4].ValueAsString],
                                          [tm_acquisition_object.Metadata[5].ValueAsString,
                                           tm_acquisition_object.Metadata[6].ValueAsString]]),
            'ExposureTime':             tm_acquisition_object.Metadata[8].ValueAsString,
            'DarkGainCorrectionType':   tm_acquisition_object.Metadata[9].ValueAsString,
            'ShuttersType':             tm_acquisition_object.Metadata[10].ValueAsString,
            'ShuttersPosition':         tm_acquisition_object.Metadata[11].ValueAsString,
            'AcquisitionUnit':          tm_acquisition_object.Metadata[12].ValueAsString,
            'BitsPerPixel':             tm_acquisition_object.Metadata[13].ValueAsString,
            'Encoding':                 tm_acquisition_object.Metadata[14].ValueAsString,
            'ImageSize':                (tm_acquisition_object.Metadata[15].ValueAsString,
                                         tm_acquisition_object.Metadata[16].ValueAsString),
            'Offset':                   (tm_acquisition_object.Metadata[17].ValueAsString,
                                         tm_acquisition_object.Metadata[18].ValueAsString),
            'PixelSize':                (tm_acquisition_object.Metadata[19].ValueAsString,
                                         tm_acquisition_object.Metadata[20].ValueAsString),
            'PixelUnit':                (tm_acquisition_object.Metadata[21].ValueAsString,
                                         tm_acquisition_object.Metadata[22].ValueAsString),
            'TimeStamp':                tm_acquisition_object.Metadata[23].ValueAsString,
            'MaxPossiblePixelValue':    tm_acquisition_object.Metadata[24].ValueAsString,
            'SaturationPoint':          tm_acquisition_object.Metadata[25].ValueAsString,
            'DigitalGain':              tm_acquisition_object.Metadata[26].ValueAsString,
            'CombinedSubFrames':        tm_acquisition_object.Metadata[27].ValueAsString,
            'CommercialName':           tm_acquisition_object.Metadata[28].ValueAsString,
            'FrameID':                  tm_acquisition_object.Metadata[29].ValueAsString,
            'TransferOK':               tm_acquisition_object.Metadata[30].ValueAsString,
            'PixelValueToCameraCounts': tm_acquisition_object.Metadata[31].ValueAsString,
            'ElectronCounted':          tm_acquisition_object.Metadata[32].ValueAsString,
            'AlignIntegratedImage':     tm_acquisition_object.Metadata[33].ValueAsString}


class Acquisition:
    """
    A simplified, forward facing Acquisition class.

    Private Attributes:
        __image:      numpy.ndarray:   The image itself, as a numpy array.
        __metadata:   dictionary:      All the image metadata (describes and gives information about the __image).
    """

    def __init__(self, tm_acquisition_object):
        self.__image = np.asarray(tm_acquisition_object.AsSafeArray)
        self.__metadata = build_metadata_dictionary(tm_acquisition_object=tm_acquisition_object)

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
