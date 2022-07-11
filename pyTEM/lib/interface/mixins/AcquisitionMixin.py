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
import multiprocessing as mp

from typing import List, Tuple

# Add the pyTEM package directory to path
package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.lib.interface.mixins.StageMixin import StageMixin
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

    def acquisition_series(self,
                           camera_name: str,
                           num: int,
                           exposure_time: float = 0,
                           sampling: str = None,
                           readout_area: int = None,
                           blanker_optimization: bool = True,
                           tilt_destinations: float = None,
                           verbose: bool = False
                           ) -> AcquisitionSeries:
        """
        Perform (and return the results of) an acquisition series.

        # TODO: This method remains untested.

        :param num: int:
            The number of acquisitions in the series.
        :param camera_name: str:
            The name of the camera you want use. For a list of available cameras, please use the
             get_available_cameras() method.
        :param exposure_time: float:
            Exposure time, in seconds. Please expose responsibly.
        :param sampling: str:
            One of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
        :param readout_area: int (optional, default is 0):
             Sets the area to be read from the camera sensor; the area is defined around the center of the sensor,
             horizontally as well as vertically. Basically this will chop the image (like extra binning). One of:
            - 0: full-size
            - 1: half-size
            - 2: quarter-size

        :param tilt_destinations: # TODO
        :param blanker_optimization:

         :param verbose: (optional; default is False):
            Print out extra information. Useful for debugging.

        :return: AcquisitionSeries:
            An acquisition series.
        """
        acq_series = AcquisitionSeries()
        for i in range(num):
            acq, (_, _) = self.acquisition(camera_name=camera_name, sampling=sampling,
                                           exposure_time=exposure_time, readout_area=readout_area)
            acq_series.append(acq=acq)

        return acq_series

    def acquisition(self,
                    camera_name: str,
                    exposure_time: float = None,
                    sampling: str = None,
                    readout_area: int = 0,
                    blanker_optimization: bool = True,
                    tilt_destination: float = None,
                    verbose: bool = False
                    ) -> Tuple[Acquisition, Tuple[float, float]]:
        """
        Perform (and return the results of) a single acquisition.

        Also, we return a tuple with the start and end epochs of the core acquisition. While this whole acquisition()
         method may take longer, this core time is the time required by the underlying Thermo Fisher acquisition
         command, and is the closest we can get to the actual acquisition time (the actual time the camera is recording
         useful information).

        :param camera_name: str:
            The name of the camera you want use. For a list of available cameras, please use the
             get_available_cameras() method.
        :param exposure_time: float:
            Exposure time, in seconds. Please expose responsibly.
        :param sampling: str:
            One of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
        :param readout_area: int (optional, default is zero):
             Sets the area to be read from the camera sensor; the area is defined around the center of the sensor,
             horizontally as well as vertically. Basically this will chop the image (like extra binning). One of:
            - 0: full-size
            - 1: half-size
            - 2: quarter-size

        :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging.

        This function provides the following optional controls by means of multiprocessing. Utilizing either of these
         functionalities significantly increase runtime because we have to wait for a separate parallel process (a new
         instance of the Python interpreter) to spawn and initialize a new microscope interface for this other process.
         # TODO: Eliminate the additional runtime caused by process creation and interface creation (maybe by switching
            to threading, sharing an single interface across processes/threads, or creating the parallel process right
            when the user first connects to the microscope).
            Illumination controls (including beam blanker controls) can only be called from the thread in which they
            were marshalled, so right now we just perform all multitasking with a separate process. Maybe could use
            pythoncom.CoMarshalInterThreadInterfaceInStream() to sort the issue.

        :param blanker_optimization: bool (optional; default is True):
            When we call the core Thermo Fisher acquisition command, the camera is blind for
             one interval of exposure_time and then records for next interval of exposure_time. Therefore the full
             acquisition takes 2 * exposure_time + some communication delays. In order to minimize sample exposure
             (material are often beam sensitive), we control the blanker in a parallel process where we only unblank
             when the camera is actually recording. This optional beam blanker control can be controlled via the
             following optional parameter.
            True: Minimize dose by means of blanking while the camera is not actually recording.
            False: Proceed without optimized blanker control, the beam will be unblanked for the full
                    2 * exposure_time + some communication delays.

        :param tilt_destination: float (optional; default is None):
            The angle to which you would like to tilt to over the duration of the acquisition.
            If provided, then acquire-while-tilting functionality is enabled and the stage will tilt from its
             current location to the provided tilt_destination over the course of the acquisition. Tilt speed is
             determined automatically from the exposure_time (which when tilting is really more of an integration time).
            Upon return the stage is left at the tilt_destination.

        :return:
            Acquisition: A single acquisition.
            (float, float): The core acquisition start and end times.
        """
        # Make sure the beam is blank while we set up the acquisition
        user_had_beam_blanked = self.beam_is_blank()
        if not user_had_beam_blanked:
            self.blank_beam()

        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            raise Exception("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") "
                            "could not be selected. Please use the get_available_cameras() method to get a list of "
                            "the available cameras.")

        camera_settings = acquisition.CameraSettings

        camera_settings.ReadoutArea = readout_area

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

        min_supported_exposure_time, max_supported_exposure_time = self.get_exposure_time_range(camera_name)
        if min_supported_exposure_time < exposure_time < max_supported_exposure_time:
            camera_settings.ExposureTime = exposure_time
        else:
            raise Exception("Unable to perform acquisition because the requested exposure time (" +
                            str(exposure_time) + ") is not in the supported range of "
                            + str(min_supported_exposure_time) + " to " + str(max_supported_exposure_time)
                            + " seconds. ")

        print("Staring beam blanker process at.." + str(time.time()))

        # Blanker optimization and tilting while acquiring both require multitasking.
        multitasking_required = blanker_optimization or tilt_destination is not None
        blanker_tilt_process = None  # Warning suppression
        if multitasking_required:
            # Then we either need to optimize the blanker or tilt while acquiring. Either way, we need to spawn a
            #  parallel process.

            # Create a barrier to help improve synchronization.
            barrier = mp.Barrier(2)  # 1 for the main process + 1 for the blanker/tilt process = 2

            blanker_tilt_process = mp.Process(target=blanker_tilt_control, kwargs={'exposure_time': exposure_time,
                                              'blanker_optimization': blanker_optimization, 'barrier': barrier,
                                              'tilt_destination': tilt_destination, 'verbose': verbose})

            blanker_tilt_process.start()
            barrier.wait()  # Wait for the blanker/tilt process to initialize.

        # Actually perform the acquisition
        core_acquisition_start_time = time.time()
        acq = acquisition.Acquire()
        core_acquisition_end_time = time.time()

        if multitasking_required:
            blanker_tilt_process.join()

        # Leave the blanker the same way we found it
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


def blanker_tilt_control(barrier: mp.Barrier, exposure_time: float,
                         blanker_optimization: bool, tilt_destination: float,
                         verbose: bool = False) -> None:
    """
    This function is to be run in a parallel thread/process.

    Support pyTEM.Interface.acquisition() with the control of blanking and/or tilting. For more information on why this
     is helpful, please refer to pyTEM.Interface.acquisition()

    :param barrier: mp.Barrier:
        Multiprocessing barrier, used to synchronize with the main thread.
    :param exposure_time: float:
        Exposure (integration) time, in seconds.

    :param blanker_optimization: bool:
        Whether to perform blanker optimization or not.
    :param tilt_destination: float (optional; default is None):
        The angle to tilt to, in degrees. If None, then no tilting is performed.

    :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging.

    :return: None.
    """
    interface = StageAndBlankerInterface()

    # Declarations for warning suppression
    beam_unblank_time, beam_reblank_time, tilt_start_time, tilt_stop_time = None, None, None, None

    barrier.wait()  # Synchronize with the main thread

    # Wait while the camera is blind
    time.sleep(exposure_time)

    if blanker_optimization:
        # Unblank while the acquisition is active.
        interface.unblank_beam()
        beam_unblank_time = time.time()

    if tilt_destination is not None:
        # Perform a tilt, this blocks the program for the full integration time so no need to sleep
        tilt_start_time = time.time()
        interface.set_stage_position_alpha(alpha=tilt_destination, speed=tilt_speed, movement_type="go")
        tilt_stop_time = time.time()
    else:
        time.sleep(exposure_time)

    if blanker_optimization:
        # Re-blank the beam
        beam_reblank_time = time.time()
        interface.blank_beam()

    if verbose:
        if blanker_optimization:
            print("\nUnblanked the beam at: " + str(beam_unblank_time))
            print("Re-blanked the beam at: " + str(beam_reblank_time))
            print("Total time spent with the beam unblanked: " + str(beam_reblank_time - beam_unblank_time))
        if tilt_destination is not None:
            print("\nStarted titling at: " + str(tilt_start_time))
            print("Stopped tilting at: " + str(tilt_stop_time))
            print("Total time spent tilting: " + str(tilt_stop_time - tilt_start_time))


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


class StageAndBlankerInterface(StageMixin, BeamBlankerMixin):
    """
    A microscope interface with only stage and blanker controls.
    """

    def __init__(self):
        try:
            self._tem = cc.CreateObject("TEMScripting.Instrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e


if __name__ == "__main__":

    requested_exposure_time = 1  # s

    acq_interface = AcquisitionInterface()
    available_cameras = acq_interface.get_available_cameras()
    acq_interface.print_camera_capabilities(available_cameras[0])

    print("\nPerforming an acquisition...")
    overall_start_time = time.time()
    test_acq, (core_acq_start, core_acq_end) = acq_interface.acquisition(camera_name="BM-Ceta", sampling='1k',
                                                                         exposure_time=requested_exposure_time,
                                                                         blanker_optimization=True, verbose=True,
                                                                         tilt_destination=None)
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
