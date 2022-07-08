"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import time
import pathlib
import sys
import warnings

import comtypes.client as cc
import numpy as np

from typing import List, Tuple
from pathos.helpers import mp

# Add the pyTEM package directory to path
package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
    from pyTEM.lib.interface.Acquisition import Acquisition
    from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerInterface, BeamBlankerMixin
except Exception as ImportException:
    raise ImportException


class AcquisitionMixin(BeamBlankerMixin):
    """
    Microscope image acquisition controls.

    This mixin was developed in support of pyTEM.Interface, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem_advanced: type(cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument"))
    except OSError:
        pass

    def acquisition_series(self, camera_name: str, num: int, sampling: str = None, exposure_time: float = None,
                           readout_area: int = None) -> AcquisitionSeries:
        """
        Perform (and return the results of) an acquisition series.

        # TODO: This method remains untested.

        :param camera_name: str:
            The name of the camera you want use. For a list of available cameras, please use the
             get_available_cameras() method.
        :param num: int:
            The number of acquisitions to perform.
        :param sampling: str:
            One of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
        :param exposure_time: float:
            Exposure time for a single acquisition, in seconds. Please expose responsibly.
        :param readout_area: int:
             Sets the area to be read from the camera sensor; the area is defined around the center of the sensor,
             horizontally as well as vertically. Basically this will chop the image (like extra binning). One of:
            - 0: full-size
            - 1: half-size
            - 2: quarter-size

        :return: AcquisitionSeries:
            An acquisition series.
        """
        acq_series = AcquisitionSeries()
        for i in range(num):
            acq, (_, _) = self.acquisition(camera_name=camera_name, sampling=sampling,
                                           exposure_time=exposure_time, readout_area=readout_area)
            acq_series.append(acq=acq)

        return acq_series

    def acquisition(self, camera_name: str, sampling: str = None, exposure_time: float = None,
                    readout_area: int = None, verbose: bool = False) -> Tuple[Acquisition, Tuple[float, float]]:
        """
        Perform (and return the results of) a single acquisition.

        Also, we return a tuple with the start and end epochs of the core acquisition. While this whole acquisition()
         method may take longer, this core time is the time required by the underlying TH acquisition command, this is
         the closest we can get to the actual acquisition time (the actual time the camera is recording useful
         information).

        :param camera_name: str:
            The name of the camera you want use. For a list of available cameras, please use the
             get_available_cameras() method.
        :param sampling: str:
            One of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
        :param exposure_time: float:
            Exposure time is in seconds. Please expose responsibly.
        :param readout_area: int:
             Sets the area to be read from the camera sensor; the area is defined around the center of the sensor,
             horizontally as well as vertically. Basically this will chop the image (like extra binning). One of:
            - 0: full-size
            - 1: half-size
            - 2: quarter-size
        :param verbose:
            Print out extra information. Useful for debugging.

        :return:
            Acquisition: A single acquisition.
            (float, float): The core acquisition start and end times.
        """
        # Make sure the beam is blank while we set up the acquisition
        user_had_beam_blanked = self.beam_is_blank()
        if not user_had_beam_blanked:
            self.blank_beam()



        # if not beam_blanker_controls.beam_is_blank():
        #     beam_blanker_controls.blank_beam()

        # To reduce exposure time as much as possible, only unblank the beam during the active part of the acquisition.
        #  Since Illumination controls (including beam blanker controls) can only be called from the thread in which
        #  they were marshalled, we need to control the blanker from a whole separate process
        # blanker_process = BlankerControl(exposure_time=exposure_time, verbose=verbose)



        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            warnings.warn("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") could "
                          "not be selected. Please use the get_available_cameras() method to confirm that the "
                          "requested camera is actually available. Returning an empty Acquisition object. "
                          "Returning an empty Acquisition object.")
            return Acquisition(None), (np.nan, np.nan)

        camera_settings = acquisition.CameraSettings

        if readout_area is not None:
            camera_settings.ReadoutArea = readout_area

        if sampling is not None:
            supported_samplings = acquisition.CameraSettings.Capabilities.SupportedBinnings
            if sampling == '4k':
                camera_settings.Binning = supported_samplings[0]  # 4k images (4096 x 4096)
            elif sampling == '2k':
                camera_settings.Binning = supported_samplings[1]  # 2k images (2048 x 2048)
            elif sampling == '1k':
                camera_settings.Binning = supported_samplings[2]  # 1k images (1024 x 1024)
            elif sampling == '0.5k':
                camera_settings.Binning = supported_samplings[3]  # 0.5k images (512 x 512)
            else:
                print('Unknown sampling Type. Proceeding with the default sampling.')

        if exposure_time is not None:
            min_supported_exposure_time, max_supported_exposure_time = self.get_exposure_time_range(camera_name)
            if min_supported_exposure_time < exposure_time < max_supported_exposure_time:
                camera_settings.ExposureTime = exposure_time
            else:
                warnings.warn("Unable to perform acquisition because the requested exposure time (" +
                              str(exposure_time) + ") is not in the supported range of "
                              + str(min_supported_exposure_time) + " to " + str(max_supported_exposure_time)
                              + " seconds. Returning an empty Acquisition object.")
                return Acquisition(None), (np.nan, np.nan)

        print("Staring beam blanker process at.." + str(time.time()))

        def blanker_control() -> None:
            """

            :return: None.
            """
            # Unblank while the acquisition is active.
            self.unblank_beam()  # Takes ~0.15 s to run
            beam_unblank_time = time.time()
            time.sleep(exposure_time)  # Make sure we are unblanked for the full exposure time
            beam_reblank_time = time.time()
            self.blank_beam()  # Takes ~0.15 s to run

            if verbose:
                print("\nUnblanked the beam at: " + str(beam_unblank_time))
                print("Re-blanked the beam at: " + str(beam_reblank_time))
                print("Total time spent with the beam unblanked: " + str(beam_reblank_time - beam_unblank_time))

        blanker_process = mp.Process(target=blanker_control)
        blanker_process.start()

        # Actually perform the acquisition
        core_acquisition_start_time = time.time()
        acq = acquisition.Acquire()
        core_acquisition_end_time = time.time()

        blanker_process.join()

        # Leave the blanker the same way the user had it
        if not user_had_beam_blanked:
            self.unblank_beam()

        return Acquisition(acq), (core_acquisition_start_time, core_acquisition_end_time)

    def print_camera_capabilities(self, camera_name: str) -> None:
        """
        Print out the capabilities of the requested camera.

        :param camera_name: str:
            The name of the camera of which you want to know the capabilities. For a list of available cameras,
             please use the get_available_cameras() method.

        :return: None.
        """
        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            warnings.warn("Unable to print camera capabilities because the requested camera (" + str(camera_name) +
                          ") could not be selected. Please use the get_available_cameras() method to confirm that the "
                          "requested camera is actually available.")
            return None

        capabilities = acquisition.CameraSettings.Capabilities

        print("\n-- " + camera_name + " Capabilities --")

        print("\nSupported Samplings:")
        for sampling in capabilities.SupportedBinnings:
            print(str(sampling.Height) + " x " + str(sampling.Width)
                  + " (Image size: " + str(int(4096 / sampling.Height)) + " x " + str(int(4096 / sampling.Width)) + ")")

        print("\nSupported Expose Time Range:")
        exposure_time_range = capabilities.ExposureTimeRange
        print(str(exposure_time_range.Begin) + " - " + str(exposure_time_range.End) + " s")

        print("\nCamera Supports Dose Fractions:")
        print(capabilities.SupportsDoseFractions)

        print("\nMaximum Number of Dose Fractions:")
        print(capabilities.MaximumNumberOfDoseFractions)

        print("\nCamera Supports Drift Correction:")
        print(capabilities.SupportsDriftCorrection)

        print("\nCamera Supports Electron Counting:")
        print(capabilities.SupportsElectronCounting)

        print("\nSCamera Supports EER")
        print(capabilities.SupportsEER)

        print("\nCamera Supports Recording:")
        print(capabilities.SupportsRecording)

    def get_available_cameras(self) -> List[str]:
        """
        Get a list of the available cameras.
        :return: list of strings:
            A list with the names of the available cameras.
        """
        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras
        return [c.name for c in supported_cameras]

    def get_exposure_time_range(self, camera_name: str) -> Tuple[float, float]:
        """
        Get the supported exposure time range, in seconds.

        :param camera_name: str:
            The name of the camera of which you want to get the supported exposure time range. For a list of available
              cameras, please use the get_available_cameras() method.
        :return: float, float:
            The maximum and minimum supported exposure times.
        """
        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            warnings.warn("Unable to get the exposure time range because the requested camera (" + str(camera_name) +
                          ") could not be selected. Please use the get_available_cameras() method to confirm that the "
                          "requested camera is actually available.")
            return np.nan, np.nan

        exposure_time_range = acquisition.CameraSettings.Capabilities.ExposureTimeRange

        return exposure_time_range.Begin, exposure_time_range.End





class AcquisitionInterface(AcquisitionMixin):
    """
    A microscope interface with only acquisition controls.
    """

    def __init__(self):
        try:
            self._tem_advanced = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e


if __name__ == "__main__":

    requested_exposure_time = 0.1  # s

    acq_interface = AcquisitionInterface()
    available_cameras = acq_interface.get_available_cameras()
    acq_interface.print_camera_capabilities(available_cameras[0])

    print("\nPerforming an acquisition...")
    overall_start_time = time.time()
    test_acq, (core_acq_start, core_acq_end) = acq_interface.acquisition(camera_name="BM-Ceta", sampling='1k',
                                                                         exposure_time=requested_exposure_time,
                                                                         readout_area=None, verbose=True)
    overall_stop_time = time.time()

    print("\nRequested Exposure time: " + str(requested_exposure_time))

    print("\nCore acquisition started at: " + str(core_acq_start))
    print("Core acquisition returned at: " + str(core_acq_end))
    print("Core acquisition time: " + str(core_acq_end - core_acq_start))

    print("\nOverall acquisition() method call started at: " + str(overall_start_time))
    print("Overall acquisition() method returned at: " + str(overall_stop_time))
    print("Total overall time spent in acquisition(): " + str(overall_stop_time - overall_start_time))

    print("\nTime between the acquisition() method call and core start: " + str(core_acq_start - overall_start_time))
    print("Time between when the core acquisition finished and when acquisition() returned: "
          + str(overall_stop_time - core_acq_end))

    print(test_acq.get_image())
    test_acq.show_image()

    # out_dir = package_directory.parent.resolve() / "test" / "interface" / "test_images"
    # print("out_dir: " + str(out_dir))
    # out_file_ = out_dir / "test_image.tif"
    # print("Saving the image as " + str(out_file_))
    # test_acq.save_as_tif(out_file=out_file_)
