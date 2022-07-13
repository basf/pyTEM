"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import time
import pathlib
import sys
import warnings

import comtypes.client as cc
import numpy as np
import multiprocessing as mp

from typing import List, Tuple, Union, Any
from numpy.typing import ArrayLike

package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    # Mixins
    from pyTEM.lib.interface.mixins.ImageShiftMixin import ImageShiftMixin
    from pyTEM.lib.interface.mixins.ScreenMixin import ScreenMixin
    from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerMixin
    from pyTEM.lib.interface.mixins.StageMixin import StageMixin
    from pyTEM.lib.interface.mixins.VacuumMixin import VacuumMixin

    # Other library imports
    from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
    from pyTEM.lib.interface.Acquisition import Acquisition
    from pyTEM.lib.interface.blanker_tilt_control import blanker_tilt_control
except Exception as ImportException:
    raise ImportException


class AcquisitionMixin(ImageShiftMixin,     # So we can apply compensatory image shifts
                       ScreenMixin,         # So we can make sure the screen is retracted while acquiring
                       BeamBlankerMixin,    # So we can control the blanker - needed to eliminate necessary dose
                       StageMixin,          # So we can provide tilt-while-acquiring functionality
                       VacuumMixin          # So we can make sure the column valve is open while acquiring
                       ):
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
                           num: int,
                           camera_name: str,
                           exposure_time: float = 0,
                           sampling: str = None,
                           readout_area: int = None,
                           blanker_optimization: bool = True,
                           tilt_bounds: Union[ArrayLike, None] = None,
                           shifts: Any = None,
                           verbose: bool = False
                           ) -> AcquisitionSeries:
        """
        Perform (and return the results of) an acquisition series.

        If they are not already, the column valve will be opened and the screen retracted. They will be returned to
         the position in which the were found upon completion of the series.

        # TODO: This method remains untested.

        :param num: int:
            The number of acquisitions to perform.
        :param camera_name: str:
            The name of the camera you want use.
            For a list of available cameras, please use the get_available_cameras() method.
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
        :param shifts: np.array of float tuples (optional; default is None):
            An array of tuples of the form (x, y) where x and y are the image shifts (in microns) to apply for the
             corresponding acquisition. If None, no image shifts will be applied.
            If provided, len(shifts) should equal num
            While there are other applications, image shifts can be used to compensation for lateral image shift while
             tilting or moving.
        :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging.

        This function provides the following optional controls by means of multitasking. Utilizing either of these
         functionalities results in the spawning of a separate parallel process.

        :param blanker_optimization: bool (optional; default is True):
            When we call the core Thermo Fisher acquisition command, the camera is blind for
             one interval of exposure_time and then records for the next interval of exposure_time. Therefore the full
             acquisition takes 2 * exposure_time + some communication delays. In order to minimize sample exposure
             (material are often beam sensitive), we control the blanker in a parallel process where we only unblank
             when the camera is actually recording.
            This optional beam blanker control can be controlled via this
             optional parameter. One of:
                True: Minimize dose by means of blanking while the camera is not actually recording.
                False: Proceed without optimized blanker control, the beam will be unblanked for the full
                        2 * exposure_time + some communication delays.

        :param tilt_bounds: array of float (optional; default is None):
            An array of alpha start-stop values for the tilt acquisition(s), in degrees.
            len(tilt_bounds) should equal num + 1
            Doesn't need to be evenly spaced, the tilt speed will adapt for each individual acquisition.
            This method takes care of ensuring we are at the starting angle (tilt_bounds[0]) before performing the
             first acquisition.
            Notice that when tilting, exposure time is really more of an integration time.
            Upon return the stage is left at the final destination -> tilt_bounds[-1].
            If None, or an array of length 0, then no tilting is performed.

        :return: AcquisitionSeries:
            An acquisition series.
        """
        if num <= 0:
            raise Exception("Error: acquisition_series() requires we perform at least one acquisition.")

        if shifts is not None:
            if len(shifts) != num:
                raise Exception("Error: The shifts array passed to acquisition_series() has a length of "
                                + str(shifts) + ", but it should have a length of num=" + str(num) + ".")

        # Make sure the beam is blank, column valve is open, and the screen is removed.
        user_had_beam_blanked = self.beam_is_blank()
        if not user_had_beam_blanked:
            self.blank_beam()
        user_column_valve_position = self.get_column_valve_position()
        if user_column_valve_position == "closed":
            self.open_column_valve()
        user_screen_position = self.get_screen_position()
        if user_screen_position == "inserted":
            self.retract_screen()

        # Find out if we are tilting
        tilting = False  # Assume we are not tilting
        if tilt_bounds is not None:
            # Then we expect an array, either of length 0 or num_acquisitions + 1.
            if len(tilt_bounds) == 0:
                pass
            if len(tilt_bounds) == num + 1:
                tilting = True  # We need to tilt.

                # Ensure we are at the starting tilt angle.
                if not math.isclose(self.get_stage_position_alpha(), tilt_bounds[0], abs_tol=0.01):
                    if verbose:
                        print("Moving the stage to the start angle, \u03B1=" + str(tilt_bounds[0]))
                    self.set_stage_position_alpha(alpha=tilt_bounds[0], speed=0.25, movement_type="go")
            else:
                raise Exception("Error: The length of the non-empty tilt_bounds array (" + str(len(tilt_bounds))
                                + ") received by blanker_tilt_control() is inconsistent with the requested number of "
                                  "requested acquisitions (" + str(num) + ").")

        # Blanker optimization and tilting while acquiring both require multitasking.
        multitasking_required = blanker_optimization or tilting
        blanker_tilt_process, barriers = None, None  # Warning suppression
        if multitasking_required:
            # Then we either need to optimize the blanker or tilt while acquiring. Either way, we need to spawn a
            #  parallel process.

            # Create an array of barriers that can be used to keep the blanking/tilting process synchronized with the
            #  main thread.
            barriers = np.full(shape=num, fill_value=np.nan)
            for i in range(len(barriers)):
                barriers[i] = mp.Barrier(2)  # 1 for the main process + 1 for the blanker/tilt process = 2

            if tilting is None:
                tilt_bounds = None  # No tilting

            if verbose:
                print("This acquisition series requires multitasking, creating an separate blanking/tilting process.")

            blanker_tilt_args = {'num_acquisitions': num, 'barriers': barriers, 'exposure_time': exposure_time,
                                 'blanker_optimization': blanker_optimization, 'tilt_bounds': tilt_bounds,
                                 'verbose': verbose}
            blanker_tilt_process = mp.Process(target=blanker_tilt_control, kwargs=blanker_tilt_args)

            if verbose:
                print("Starting the blanking/tilting process.")

            blanker_tilt_process.start()

        acq_series = AcquisitionSeries()
        for i in range(num):

            if shifts is not None:
                # Apply the requested image shift
                self.set_image_shift(x=shifts[i, 0], y=shifts[i, 1])

            # Set up the acquisition
            acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
            supported_cameras = acquisition.SupportedCameras

            # Try and select the requested camera
            try:
                acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
            except ValueError:
                raise Exception("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") "
                                "could not be selected. Please use the get_available_cameras() method to get a list of "
                                "the available cameras.")

            # Configure camera settings
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

            if multitasking_required:
                barriers[i].wait()  # Wait for the blanker/tilt process.
            else:
                # No multitasking required, just unblank ourselves
                self.unblank_beam()

            # Actually perform an acquisition
            core_acquisition_start_time = time.time()
            acq = acquisition.Acquire()
            core_acquisition_end_time = time.time()

            if multitasking_required:
                pass
            else:
                # No multitasking required, we have to re-blank the beam ourselves.
                self.blank_beam()

            acq_series.append(acq=acq)

            if verbose:
                print("\nAcquisition #: " + str(i))
                print("Core acquisition started at: " + str(core_acquisition_start_time))
                print("Core acquisition returned at: " + str(core_acquisition_end_time))
                print("Core acquisition time: " + str(core_acquisition_end_time - core_acquisition_start_time))

        if multitasking_required:
            # We are now done multitasking, collect the beam blanker processes before returning.
            blanker_tilt_process.join()

        # Housekeeping: Leave the blanker, column value, and screen the way they were when we started.
        if user_column_valve_position == "closed":
            self.close_column_valve()
        if user_screen_position == "inserted":
            self.insert_screen()
        if not user_had_beam_blanked:
            self.unblank_beam()

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

        If they are not already, the column valve will be opened and the screen retracted. They will be returned to
         the position in which the were found upon completion of the series.

         # TODO: This method remains untested.

        :param camera_name: str:
            The name of the camera you want use.
            For a list of available cameras, please use the get_available_cameras() method.
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
             one interval of exposure_time and then records for the next interval of exposure_time. Therefore the full
             acquisition takes 2 * exposure_time + some communication delays. In order to minimize sample exposure
             (material are often beam sensitive), we control the blanker in a parallel process where we only unblank
             when the camera is actually recording. This optional beam blanker control can be controlled via this
             optional parameter. One of:
                True: Minimize dose by means of blanking while the camera is not actually recording.
                False: Proceed without optimized blanker control, the beam will be unblanked for the full
                        2 * exposure_time + some communication delays.

        :param tilt_destination: float (optional; default is None):
            The angle to which you would like to tilt to over the duration of the acquisition.
            If provided, then acquire-while-tilting functionality is enabled and the stage will tilt from its
             current location to the provided tilt_destination over the course of the acquisition. Tilt speed is
             determined automatically from the exposure_time (which when tilting is really more of an integration time).
            Upon return the stage is left at the tilt_destination.
            If None, then no tilting is performed.

        :return:
            Acquisition: A single acquisition.
            (float, float): The core acquisition start and end times.
        """
        # Make sure the beam is blank, column valve is open, and the screen is removed.
        user_had_beam_blanked = self.beam_is_blank()
        if not user_had_beam_blanked:
            self.blank_beam()
        user_column_valve_position = self.get_column_valve_position()
        if user_column_valve_position == "closed":
            self.open_column_valve()
        user_screen_position = self.get_screen_position()
        if user_screen_position == "inserted":
            self.retract_screen()

        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            raise Exception("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") "
                            "could not be selected. Please use the get_available_cameras() method to get a list of "
                            "the available cameras.")

        # Configure camera settings
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

        # Blanker optimization and tilting while acquiring both require multitasking.
        multitasking_required = blanker_optimization or tilt_destination is not None
        blanker_tilt_process = None  # Warning suppression
        if multitasking_required:
            # Then we either need to optimize the blanker or tilt while acquiring. Either way, we need to spawn a
            #  parallel process.

            # Create a barrier to help improve synchronization.
            barrier = mp.Barrier(2)  # 1 for the main process + 1 for the blanker/tilt process = 2

            if tilt_destination is None:
                tilt_bounds = None  # No tilting
            else:
                # We want to tilt from our current position to the provided destination.
                tilt_bounds = [self.get_stage_position_alpha(), tilt_destination]

            if verbose:
                print("This acquisition requires multitasking, creating an separate blanking/tilting process.")

            blanker_tilt_args = {'num_acquisitions': 1, 'barriers': [barrier], 'exposure_time': exposure_time,
                                 'blanker_optimization': blanker_optimization, 'tilt_bounds': tilt_bounds,
                                 'verbose': verbose}
            blanker_tilt_process = mp.Process(target=blanker_tilt_control, kwargs=blanker_tilt_args)

            if verbose:
                print("Starting the blanking/tilting process.")

            blanker_tilt_process.start()
            barrier.wait()  # Wait for the blanker/tilt process to initialize.

        else:
            # No multitasking required, just unblank ourselves.
            self.unblank_beam()

        # Actually perform the acquisition.
        core_acquisition_start_time = time.time()
        acq = acquisition.Acquire()
        core_acquisition_end_time = time.time()

        if multitasking_required:
            blanker_tilt_process.join()
        else:
            self.blank_beam()

        # Housekeeping: Leave the blanker, column value, and screen the way they were when we started.
        if user_column_valve_position == "closed":
            self.close_column_valve()
        if user_screen_position == "inserted":
            self.insert_screen()
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
    A microscope interface with only acquisition (and by extension beam blanker and stage) controls.
    """

    def __init__(self):
        try:
            self._tem_advanced = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e


def acquisition_testing():
    """
    Test the acquisition() method.
    :return: None
    """
    requested_exposure_time = 1  # s

    interface = AcquisitionInterface()
    available_cameras = interface.get_available_cameras()
    interface.print_camera_capabilities(available_cameras[0])


    """ Perform an acquisition with no multitasking """
    print("\n\n## Performing an acquisition with no multitasking ##")
    overall_start_time = time.time()
    test_acq, (core_acq_start, core_acq_end) = interface.acquisition(camera_name="BM-Ceta",
                                                                     exposure_time=requested_exposure_time,
                                                                     sampling='1k',
                                                                     blanker_optimization=False,
                                                                     tilt_destination=None,
                                                                     verbose=True)
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


    """ Perform an acquisition with blanker optimization but no tilting """
    print("\n\n## Performing an acquisition with blanking optimization but no tilting ##")
    overall_start_time = time.time()
    test_acq, (core_acq_start, core_acq_end) = interface.acquisition(camera_name="BM-Ceta",
                                                                     exposure_time=requested_exposure_time,
                                                                     sampling='1k',
                                                                     blanker_optimization=True,
                                                                     tilt_destination=None,
                                                                     verbose=True)
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


    """ Perform an acquisition with tilting but no blanker optimization """
    print("\n\n## Performing an acquisition with titling (0 deg -> 2 deg) but no blanker optimization ##")
    interface.set_stage_position_alpha(alpha=0)

    overall_start_time = time.time()
    test_acq, (core_acq_start, core_acq_end) = interface.acquisition(camera_name="BM-Ceta",
                                                                     exposure_time=requested_exposure_time,
                                                                     sampling='1k',
                                                                     blanker_optimization=True,
                                                                     tilt_destination=2,
                                                                     verbose=True)
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


    """ Perform an acquisition with both tilting and blanker optimization """
    print("\n\n## Performing an acquisition with titling (0 deg -> 2 deg) AND blanker optimization ##")
    interface.set_stage_position_alpha(alpha=0)

    overall_start_time = time.time()
    test_acq, (core_acq_start, core_acq_end) = interface.acquisition(camera_name="BM-Ceta",
                                                                     exposure_time=requested_exposure_time,
                                                                     sampling='1k',
                                                                     blanker_optimization=True,
                                                                     tilt_destination=2,
                                                                     verbose=True)
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


def acquisition_series_testing():
    """
    Test the acquisition series method.
    """
    out_dir = package_directory.parent.resolve() / "test" / "interface" / "test_images"
    print("out_dir: " + str(out_dir))

    requested_exposure_time = 1  # s

    interface = AcquisitionInterface()
    available_cameras = interface.get_available_cameras()
    interface.print_camera_capabilities(available_cameras[0])


    """ Perform an acquisition series with no multitasking """
    print("\n\n## Performing an acquisition series with no multitasking ##")
    acq_series = interface.acquisition_series(num=3, camera_name="BM-Ceta",
                                              exposure_time=requested_exposure_time,
                                              sampling='1k',
                                              blanker_optimization=False,
                                              tilt_bounds=None,
                                              verbose=True)

    print("Length of the obtained series: " + str(acq_series.length()))
    print("Showing the first image in the obtained series:")
    print(acq_series[0].get_image())
    acq_series[0].show_image()

    out_file_ = out_dir / "test_series_no_multitasking.mrc"
    print("Saving series as " + str(out_file_))
    acq_series.save_as_mrc(out_file=out_file_)


    """ Perform an acquisition with blanker optimization but no tilting """
    print("\n\n## Performing an acquisition with blanking optimization but no tilting ##")
    acq_series = interface.acquisition_series(num=3, camera_name="BM-Ceta",
                                              exposure_time=requested_exposure_time,
                                              sampling='1k',
                                              blanker_optimization=True,
                                              tilt_bounds=None,
                                              verbose=True)

    print("Length of the obtained series: " + str(acq_series.length()))
    print("Showing the first image in the obtained series:")
    print(acq_series[0].get_image())
    acq_series[0].show_image()

    out_file_ = out_dir / "test_series_only_blanker_optimization.mrc"
    print("Saving series as " + str(out_file_))
    acq_series.save_as_mrc(out_file=out_file_)


    """ Perform an acquisition with tilting but no blanker optimization """
    print("\n\n## Performing an acquisition with titling (-2 deg -> 2 deg) but no blanker optimization ##")

    tilt_bounds = np.ararray([-2, -1, 0, 1, 2])

    acq_series = interface.acquisition_series(num=len(tilt_bounds - 1), camera_name="BM-Ceta",
                                              exposure_time=requested_exposure_time,
                                              sampling='1k',
                                              blanker_optimization=False,
                                              tilt_bounds=tilt_bounds,
                                              verbose=True)

    print("Length of the obtained series: " + str(acq_series.length()))
    print("Showing the first image in the obtained series:")
    print(acq_series[0].get_image())
    acq_series[0].show_image()

    out_file_ = out_dir / "test_series_only_tilting.mrc"
    print("Saving series as " + str(out_file_))
    acq_series.save_as_mrc(out_file=out_file_)



    """ Perform an acquisition with both tilting and blanker optimization """
    print("\n\n## Performing an acquisition with titling (-2 deg -> 2 deg) AND blanker optimization "
          "(with dummy shifts) ##")
    tilt_bounds = np.ararray([-2, -1, 0, 1, 2])
    shifts_ = np.full(shape=len(tilt_bounds - 1), dtype=(float, 2), fill_value=0.0)

    acq_series = interface.acquisition_series(num=len(tilt_bounds - 1), camera_name="BM-Ceta",
                                              exposure_time=requested_exposure_time,
                                              sampling='1k',
                                              blanker_optimization=False,
                                              tilt_bounds=tilt_bounds,
                                              shifts=shifts_,
                                              verbose=True)

    print("Length of the obtained series: " + str(acq_series.length()))
    print(acq_series[0].get_image())
    acq_series[0].show_image()

    out_file_ = out_dir / "test_series_blanking_and_tilting.mrc"
    print("Saving series as " + str(out_file_))
    acq_series.save_as_mrc(out_file=out_file_)


if __name__ == "__main__":

    acquisition_testing()
    # acquisition_series_testing()
