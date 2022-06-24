"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

from pyTEM.lib.interface.Acquisition import Acquisition


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

    def append(self, acq):
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

    def series_length(self):
        """
        :return: int:
            The number of acquisitions in the series.
        """
        return len(self.__acquisitions)

    def get_acquisition(self, idx):
        """
        :param idx: int:
            The index of the acquisition you want.
        :return: Acquisition:
            The acquisition at the provided index
        """
        return self.__acquisitions[idx]

    def set_acquisition(self, acq, idx):
        """
        :param acq: Acquisition:
            The acquisition to set.
        :param idx: int:
            Where you want to put the acquisition.
        :return: None
        """
        self.__acquisitions[idx] = acq

    def save_as_tif(self, out_file):
        """
        Save the acquisition as a TIFF file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .tif extension, otherwise it will be added automatically.

        :return: None.
        """
        raise NotImplementedError  # TODO

    def save_as_mrc(self, out_file):
        """
        Save the acquisition series as an MRC file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .mrc extension, otherwise it will be added automatically.

        :return: None.
        """
        raise NotImplementedError  # TODO
