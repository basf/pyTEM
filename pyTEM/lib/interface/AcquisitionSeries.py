"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
from typing import Union

from pyTEM.lib.interface.Acquisition import Acquisition


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
        :return: None
        """
        self.__acquisitions[idx] = acq

    def save_as_tif(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition as a TIFF file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .tif extension, otherwise it will be added automatically.

        :return: None.
        """
        raise NotImplementedError  # TODO

    def save_as_mrc(self, out_file: Union[str, pathlib.Path]) -> None:
        """
        Save the acquisition series as an MRC file.

        :param out_file: str or path:
            Out file path (where you want to save the file).
            Optionally, you can include the .mrc extension, otherwise it will be added automatically.

        :return: None.
        """
        raise NotImplementedError  # TODO

    def __iter__(self):
        return AcquisitionSeriesIterator(self)


if __name__ == "__main__":
    acq_series = AcquisitionSeries()
    acq_series.append(Acquisition(None))
    acq_series.append(Acquisition(None))
    acq_series.append(Acquisition(None))
    print(acq_series)
    print(acq_series.length())

    print(acq_series.get_acquisition(idx=0).get_metadata())

    print("\nTesting iteration:")
    for i, acq_ in enumerate(acq_series):
        print(i)
        print(acq_)
