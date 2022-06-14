"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import warnings

import comtypes.client as cc

from Interface.lib.Acquisition import Acquisition


class AcquisitionMixin:
    """
    Microscope image acquisition controls.

    This mixin was developed in support of Interface.TEMInterface, but can be included in other projects where helpful.
    """
    _tem_advanced: type(cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument"))

    def acquisition(self, camera_name, sampling=None, exposure_time=None, readout_area=None):
        """
        Perform (and return) the results of a single acquisition.

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

        :return: Acquisition:
            A single acquisition.
        """
        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            warnings.warn("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") could "
                          "not be selected. Please use the get_available_cameras() method to confirm that the "
                          "requested camera is actually available. Returning None.")
            return None

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
                              + " seconds. Returning None.")
                return None

        return Acquisition(acquisition.Acquire())

    def print_camera_capabilities(self, camera_name):
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
            warnings.warn("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") could "
                          "not be selected. Please use the get_available_cameras() method to confirm that the "
                          "requested camera is actually available.")
            return None

        capabilities = acquisition.CameraSettings.Capabilities

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

    def get_available_cameras(self):
        """
        Get a list of the available cameras.
        :return: list of strings:
            A list with the names of the available cameras.
        """
        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras
        return [c.name for c in supported_cameras]

    def get_exposure_time_range(self, camera_name):
        """
        Get the supported exposure time range, in seconds.

        :param camera_name: str:
            The name of the camera of which you want to get the supported exposure time range. For a list of available
              cameras, please use the get_available_cameras() method.
        :return:
        """
        acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = acquisition.SupportedCameras

        # Try and select the requested camera
        try:
            acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(str(camera_name))]
        except ValueError:
            warnings.warn("Unable to perform acquisition because the requested camera (" + str(camera_name) + ") could "
                          "not be selected. Please use the get_available_cameras() method to confirm that the "
                          "requested camera is actually available. Returning None.")
            return None

        exposure_time_range = acquisition.CameraSettings.Capabilities.ExposureTimeRange

        return exposure_time_range.Begin, exposure_time_range.End
