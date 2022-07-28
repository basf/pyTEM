"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import time
import warnings

import comtypes.client as cc
import numpy as np
import multiprocessing as mp

from typing import List, Tuple, Union
from numpy.typing import ArrayLike, NDArray

# Mixins
from pyTEM.lib.interface.mixins.ImageShiftMixin import ImageShiftMixin
from pyTEM.lib.interface.mixins.ScreenMixin import ScreenMixin
from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerMixin
from pyTEM.lib.interface.mixins.StageMixin import StageMixin
from pyTEM.lib.interface.mixins.VacuumMixin import VacuumMixin

# Other library imports
from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
from pyTEM.lib.interface.Acquisition import Acquisition
from pyTEM.lib.interface.blanker_control import blanker_control
from pyTEM.lib.interface.tilt_control import tilt_control


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
                           exposure_time: float = 1,
                           sampling: str = '1k',
                           readout_area: int = 0,
                           blanker_optimization: bool = True,
                           tilt_bounds: Union[ArrayLike, None] = None,
                           shifts: np.ndarray = None,
                           alphas: NDArray[float] = None,
                           verbose: bool = False
                           ) -> AcquisitionSeries:
        """
        Perform (and return the results of) an acquisition series.

        If they are not already, the column valve will be opened and the screen retracted. They will be returned to
         the position in which the were found upon completion of the series.

        :param num: int:
            The number of acquisitions to perform.
        :param camera_name: str:
            The name of the camera you want use.
            For a list of available cameras, please use the get_available_cameras() method.
        :param exposure_time: float (optional; default is 1 second):
            Exposure time, in seconds. Please expose responsibly.
            About 0.015 seconds is the minimum exposure time required to get a clear image.
        :param sampling: str (optional; default is '1k'):
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
            If provided, len(shifts) must equal num.
            While there are other applications, image shifts can be used to compensation for lateral image shift while
             tilting or moving.
        :param alphas: np.array of floats (optional; default is None):
            An array of alpha tilt angles at which to perform the acquisitions. These are angles we tilt to and then
             stop and acquire. If you want to acquire and tilt simultaneously, please use tilt_bounds.
            If provided, len(shifts) must equal num.
            One of alphas and tilt_bounds must be None.
        :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging.

        This function provides the following optional controls by means of multitasking. Utilizing either of these
         functionalities results in the spawning of a separate parallel process to handle it.
        # TODO: Eliminate the additional runtime caused by process creation and interface creation (maybe by switching
            to threading, or perhaps creating the parallel process right when the user first connects to the microscope
            and grabbing barriers from a Manager).
            Illumination controls (including beam blanker controls) can only be called from the thread in which they
            were marshalled, so right now we just perform all multitasking with a separate process. Maybe could use
            pythoncom.CoMarshalInterThreadInterfaceInStream() to sort the issue.

        :param blanker_optimization: bool (optional; default is True):
            When we call the core Thermo Fisher acquisition command, the camera is blind for
             one interval of exposure_time and then records for the next interval of exposure_time. Therefore, the full
             acquisition takes 2 * exposure_time + some communication delays. In order to minimize sample exposure
             (material are often beam sensitive), we can opt to control the blanker in a parallel process where we
             only unblank when the camera is actually recording.
            One of:
                True: Minimize dose by means of blanking while the camera is not actually recording. The beam is only
                 unblanked for exposure_time + 0.05 seconds for each image.
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
            If None, or an array of length 0, then no tilting is performed. One of alphas and tilt_bounds must be None.

        :return: AcquisitionSeries:
            An acquisition series.
        """
        if num <= 0:
            raise Exception("Error: acquisition_series() requires we perform at least one acquisition.")

        if shifts is not None:
            # Then we expect an array.
            if len(shifts) == 0:
                shifts = None  # Empty list.
            if len(shifts) != num:
                raise Exception("Error: The shifts array passed to acquisition_series() has a length of "
                                + str(shifts) + ", but it should have a length of num=" + str(num) + ".")
        if alphas is not None:
            # Then we expect an array, either of length 0 or num.
            if len(alphas) == 0:
                alphas = None  # Empty list.
            if len(alphas) != num:
                raise Exception("Error: The alphas array passed to acquisition_series() has a length of "
                                + str(alphas) + ", but it should have a length of num=" + str(num) + ".")

        # Find out if we are tilting.
        tilting = False  # Assume we are not tilting.
        if tilt_bounds is not None:
            # Then we expect an array, either of length 0 or num + 1.
            if len(tilt_bounds) == 0:
                pass  # Empty list.
            if len(tilt_bounds) == num + 1:
                tilting = True  # We need to tilt.
            else:
                raise Exception("Error: The length of the non-empty tilt_bounds array (" + str(len(tilt_bounds))
                                + ") received by acquisition_series() is inconsistent with the requested number of "
                                  "requested acquisitions (" + str(num) + ").")

        if tilting and alphas is not None:
            raise Exception("Error: acquisition_series() cannot take stationary images at alphas if also "
                            "tilting while acquiring. One of alphas and tilt_bounds should be None.")

        blanker_process, tilt_process, barriers = None, None, None  # Warning suppression.

        if verbose:
            print("Performing a series acquisition of " + str(num) + " acquisitions...")

        # Make sure the beam is blank, column valve is open, and the screen is retracted.
        user_had_beam_blanked = self.beam_is_blank()
        if not user_had_beam_blanked:
            self.blank_beam()
        user_column_valve_position = self.get_column_valve_position()
        if user_column_valve_position == "closed":
            self.open_column_valve()
        user_screen_position = self.get_screen_position()
        if user_screen_position == "inserted":
            self.retract_screen()

        if blanker_optimization or tilting:
            # We need an array of barriers that can be used to keep the blanking/tilting processes synchronized with
            #  the main thread.
            if verbose:
                print("Multitasking required, creating an array of " + str(num) + " barriers.")

            barriers = []
            for i in range(num):
                barriers.append(mp.Barrier(1 + blanker_optimization + tilting))  # 1 party for each process

        if blanker_optimization:
            # Then we need to spawn a parallel process from which we control the blanker.
            if verbose:
                print("The user has requested we optimize the beam blanker, creating an separate blanking process...")

            blanker_args = {'num_acquisitions': num, 'barriers': barriers, 'exposure_time': exposure_time,
                            'verbose': verbose}
            blanker_process = mp.Process(target=blanker_control, kwargs=blanker_args)

            if verbose:
                print("Starting the blanking process...")

            blanker_process.start()

        if tilting:
            # Then we need to spawn a parallel process from which we can tilt
            if verbose:
                print("This acquisition series requires tilting, creating an separate tilt process...")

            tilt_args = {'num_acquisitions': num, 'barriers': barriers, 'integration_time': exposure_time,
                         'tilt_bounds': tilt_bounds, 'verbose': verbose}
            tilt_process = mp.Process(target=tilt_control, kwargs=tilt_args)

            if verbose:
                print("Starting the tilt process...")

            tilt_process.start()

        acq_series = AcquisitionSeries()
        for i in range(num):

            if shifts is not None:
                # Apply the requested image shift.
                self.set_image_shift(x=shifts[i, 0], y=shifts[i, 1])

            if alphas is not None:
                # Apply the requested alpha tilt, go slow to reduce unnecessary error.
                self.set_stage_position_alpha(alpha=alphas[i], speed=0.25)

            # Set up the acquisition.
            acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
            supported_cameras = acquisition.SupportedCameras

            # Try and select the requested camera.
            try:
                acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
            except ValueError:
                raise Exception("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") "
                                "could not be selected. Please use the get_available_cameras() method to get a list of "
                                "the available cameras.")

            # Configure camera settings.
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

            if not blanker_optimization:
                # No separate blanker control, we have to unblank ourselves.
                self.unblank_beam()

            if blanker_optimization or tilting:
                barriers[i].wait()  # Wait for the blanker and/or tilt process(es) to synchronize.

            # Actually perform an acquisition
            core_acquisition_start_time = time.time()
            acq = acquisition.Acquire()
            core_acquisition_end_time = time.time()

            if not blanker_optimization:
                # No separate blanker control, we have to re-blank ourselves.
                self.blank_beam()

            acq_series.append(acq=Acquisition(acq))

            if verbose:
                print("\nAcquisition #: " + str(i))
                print("Core acquisition started at: " + str(core_acquisition_start_time))
                print("Core acquisition returned at: " + str(core_acquisition_end_time))
                print("Core acquisition time: " + str(core_acquisition_end_time - core_acquisition_start_time))

        if blanker_optimization:
            # Collect the beam blanker process.
            blanker_process.join()

        if tilting:
            # Collect the tilting process
            tilt_process.join()

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
                    exposure_time: float = 1,
                    sampling: str = '1k',
                    readout_area: int = 0,
                    blanker_optimization: bool = True,
                    tilt_destination: float = None,
                    verbose: bool = False
                    ) -> Acquisition:
        """
        Perform (and return the results of) a single acquisition.

        If they are not already, the column valve will be opened and the screen retracted. They will be returned to
         the position in which they were found upon completion of the acquisition.

        :param camera_name: str:
            The name of the camera you want use.
            For a list of available cameras, please use the get_available_cameras() method.
        :param exposure_time: float (optional; default is 1 second):
            Exposure time, in seconds. Please expose responsibly.
            About 0.015 seconds is the minimum exposure time required to get a clear image.
        :param sampling: str (optional; default is '1k'):
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
           One of the things printed is the core time required by the underlying Thermo Fisher acquisition command -
            this is the closest we can get to the actual acquisition time (the actual time the camera is recording
            useful information).

        This function provides the following optional controls by means of multitasking. Utilizing either of these
         functionalities results in the spawning of a separate parallel process to handle it.

        :param blanker_optimization: bool (optional; default is True):
            When we call the core Thermo Fisher acquisition command, the camera is blind for
             one interval of exposure_time and then records for the next interval of exposure_time. Therefore the full
             acquisition takes 2 * exposure_time + some communication delays. In order to minimize sample exposure
             (material are often beam sensitive), we can opt to control the blanker in a parallel process where we
             only unblank when the camera is actually recording.
            One of:
                True: Minimize dose by means of blanking while the camera is not actually recording. The beam is only
                 unblanked for exposure_time + 0.05 seconds for each image.
                False: Proceed without optimized blanker control, the beam will be unblanked for the full
                        2 * exposure_time + some communication delays.

        :param tilt_destination: float (optional; default is None):
            The angle to which you would like to tilt to over the duration of the acquisition, in degrees.
            If provided, then acquire-while-tilting functionality is enabled and the stage will tilt from its
             current location to the provided tilt_destination over the course of the acquisition. Tilt speed is
             determined automatically from the exposure_time (which when tilting is really more of an integration time).
            Upon return the stage is left at the tilt_destination.
            If None, then no tilting is performed.

        :return:
            Acquisition: A single acquisition.
        """
        if verbose:
            print("Performing an acquisition...")

        if tilt_destination is not None:
            # Tilt from the current location to the provided tilt_destination
            tilt_bounds = [self.get_stage_position_alpha(), tilt_destination]
        else:
            # No tilting
            tilt_bounds = None

        single_acq_series = self.acquisition_series(num=1, camera_name=camera_name, exposure_time=exposure_time,
                                                    sampling=sampling, readout_area=readout_area,
                                                    blanker_optimization=blanker_optimization, tilt_bounds=tilt_bounds,
                                                    shifts=None, alphas=None, verbose=verbose)

        return single_acq_series[0]

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

        print("\nCamera Supports EER")
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
            self._tem = cc.CreateObject("TEMScripting.Instrument")
            self._tem_advanced = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e


def acquisition_testing():
    """
    Test the acquisition() method.
    :return: None
    """
    requested_exposure_time = 0.1  # s

    interface = AcquisitionInterface()
    available_cameras = interface.get_available_cameras()
    interface.print_camera_capabilities(available_cameras[0])


    """ Perform an acquisition with no multitasking """
    print("\n\n## Performing an acquisition with no multitasking ##")
    overall_start_time = time.time()
    test_acq = interface.acquisition(camera_name="BM-Ceta", exposure_time=requested_exposure_time, sampling='4k',
                                     blanker_optimization=False, tilt_destination=None, verbose=True)
    overall_stop_time = time.time()

    print("\nRequested Exposure time: " + str(requested_exposure_time))

    print("\nOverall acquisition() method call started at: " + str(overall_start_time))
    print("Overall acquisition() method returned at: " + str(overall_stop_time))
    print("Total overall time spent in acquisition(): " + str(overall_stop_time - overall_start_time))

    print(test_acq.get_image())
    test_acq.show_image()

    # Comparing the intensity of images taken with and without automated blanker control allows us to ensure that the
    #  beam is unblanked for the full time the camera is acquiring.
    print(np.mean(test_acq.get_image()))


    """ Perform an acquisition with blanker optimization but no tilting """
    print("\n\n## Performing an acquisition with blanking optimization but no tilting ##")
    overall_start_time = time.time()
    test_acq = interface.acquisition(camera_name="BM-Ceta", exposure_time=requested_exposure_time, sampling='4k',
                                     blanker_optimization=True, tilt_destination=None, verbose=True)
    overall_stop_time = time.time()

    print("\nRequested Exposure time: " + str(requested_exposure_time))

    print("\nOverall acquisition() method call started at: " + str(overall_start_time))
    print("Overall acquisition() method returned at: " + str(overall_stop_time))
    print("Total overall time spent in acquisition(): " + str(overall_stop_time - overall_start_time))

    print(test_acq.get_image())
    test_acq.show_image()

    # Comparing the intensity of images taken with and without automated blanker control allows us to ensure that the
    #  beam is unblanked for the full time the camera is acquiring.
    print(np.mean(test_acq.get_image()))


    """ Perform an acquisition with tilting but no blanker optimization """
    # print("\n\n## Performing an acquisition with titling (0 deg -> 2 deg) but no blanker optimization ##")
    # interface.set_stage_position_alpha(alpha=0)
    #
    # overall_start_time = time.time()
    # test_acq = interface.acquisition(camera_name="BM-Ceta", exposure_time=requested_exposure_time, sampling='1k',
    #                                  blanker_optimization=False, tilt_destination=1, verbose=True)
    # overall_stop_time = time.time()
    #
    # print("\nRequested Exposure time: " + str(requested_exposure_time))
    #
    # print("\nOverall acquisition() method call started at: " + str(overall_start_time))
    # print("Overall acquisition() method returned at: " + str(overall_stop_time))
    # print("Total overall time spent in acquisition(): " + str(overall_stop_time - overall_start_time))
    #
    # print(test_acq.get_image())
    # test_acq.show_image()


    """ Perform an acquisition with both tilting and blanker optimization """
    # print("\n\n## Performing an acquisition with titling (0 deg -> 2 deg) AND blanker optimization ##")
    # interface.set_stage_position_alpha(alpha=0)
    #
    # overall_start_time = time.time()
    # test_acq = interface.acquisition(camera_name="BM-Ceta", exposure_time=requested_exposure_time, sampling='1k',
    #                                  blanker_optimization=True, tilt_destination=1, verbose=True)
    # overall_stop_time = time.time()
    #
    # print("\nRequested Exposure time: " + str(requested_exposure_time))
    #
    # print("\nOverall acquisition() method call started at: " + str(overall_start_time))
    # print("Overall acquisition() method returned at: " + str(overall_stop_time))
    # print("Total overall time spent in acquisition(): " + str(overall_stop_time - overall_start_time))
    #
    # print(test_acq.get_image())
    # test_acq.show_image()


def acquisition_series_testing():
    """
    Test the acquisition series method.
    """
    out_dir = package_directory.resolve() / "test" / "interface" / "test_images"
    print("out_dir: " + str(out_dir))

    requested_exposure_time = 1  # s

    interface = AcquisitionInterface()
    available_cameras = interface.get_available_cameras()
    interface.print_camera_capabilities(available_cameras[0])


    """ Perform an acquisition series with no multitasking """
    # print("\n\n## Performing an acquisition series of 3 images with no multitasking ##")
    # acq_series = interface.acquisition_series(num=num, camera_name="BM-Ceta",
    #                                           exposure_time=requested_exposure_time,
    #                                           sampling='4k',
    #                                           blanker_optimization=False,
    #                                           tilt_bounds=None,
    #                                           verbose=True)
    #
    # print("\nLength of the obtained series: " + str(acq_series.length()))
    # print("Mean exposures:")
    # for i in range(num):
    #     print(np.mean(acq_series[i].get_image()))
    # print("Showing the first image in the obtained series:")
    # print(acq_series[0].get_image())
    # acq_series[0].show_image()
    #
    # out_file_ = out_dir / "test_series_no_multitasking.mrc"
    # print("Saving series as " + str(out_file_))
    # acq_series.save_as_mrc(out_file=out_file_)


    """ Perform an acquisition with blanker optimization but no tilting """
    # print("\n\n## Performing an acquisition with blanking optimization but no tilting ##")
    # acq_series = interface.acquisition_series(num=3, camera_name="BM-Ceta",
    #                                           exposure_time=requested_exposure_time,
    #                                           sampling='4k',
    #                                           blanker_optimization=True,
    #                                           tilt_bounds=None,
    #                                           verbose=True)
    #
    # print("\nLength of the obtained series: " + str(acq_series.length()))
    # print("Mean exposures:")
    # for i in range(num):
    #     print(np.mean(acq_series[i].get_image()))
    # print("\nShowing the first image in the obtained series:")
    # print(acq_series[0].get_image())
    # acq_series[0].show_image()
    #
    # out_file_ = out_dir / "test_series_only_blanker_optimization.mrc"
    # print("Saving series as " + str(out_file_))
    # acq_series.save_as_mrc(out_file=out_file_)


    """ Perform an acquisition with tilting but no blanker optimization """
    print("\n\n## Performing an acquisition with titling (-2 deg -> 2 deg) but no blanker optimization ##")

    tilt_bounds = np.asarray([-2, -1, 0, 1, 2])

    acq_series = interface.acquisition_series(num=len(tilt_bounds) - 1, camera_name="BM-Ceta",
                                              exposure_time=requested_exposure_time,
                                              sampling='4k',
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
    # print("\n\n## Performing an acquisition with titling (-2 deg -> 2 deg) AND blanker optimization "
    #       "(with dummy shifts) ##")
    # tilt_bounds = np.ararray([-2, -1, 0, 1, 2])
    # shifts_ = np.full(shape=len(tilt_bounds - 1), dtype=(float, 2), fill_value=0.0)
    #
    # acq_series = interface.acquisition_series(num=len(tilt_bounds) - 1, camera_name="BM-Ceta",
    #                                           exposure_time=requested_exposure_time,
    #                                           sampling='1k',
    #                                           blanker_optimization=False,
    #                                           tilt_bounds=tilt_bounds,
    #                                           shifts=shifts_,
    #                                           verbose=True)
    #
    # print("Length of the obtained series: " + str(acq_series.length()))
    # print(acq_series[0].get_image())
    # acq_series[0].show_image()
    #
    # out_file_ = out_dir / "test_series_blanking_and_tilting.mrc"
    # print("Saving series as " + str(out_file_))
    # acq_series.save_as_mrc(out_file=out_file_)


if __name__ == "__main__":

    # acquisition_testing()
    acquisition_series_testing()
