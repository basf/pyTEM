"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import comtypes.client as cc

from Interface.lib.Acquisition import Acquisition

# TODO: Still requires testing


class AcquisitionMixin:
    """
    Microscope acquisition controls, including those for taking images.

    This mixin was developed in support of Interface.TEMInterface, but can be included in other projects where helpful.
    """
    _tem_advanced: type(cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument"))

    def single_acquisition(self, camera_name, binning=None, exposure_time=None, readout_area=None):
        """
        Perform (and return) the results of a single acquisition.

        :param camera_name: str:
            The camera you want use, one of:
            - 'BM-Ceta'
            - 'BM-Falcon' (use this camera carefully!)
        :param binning: str:
            One of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
        :param exposure_time: float:
            Exposure time is in seconds. Please expose responsibly.
        :param readout_area: int:
             Sets the area to be read from the camera sensor; the area is defined around the center of the sensor,
             horizontally as well as vertically. Basically this will chop the image (like an extra binning). One of:
            - 0: full-size
            - 1: half-size
            - 2: quarter-size

        :return: Acquisition:
            The single acquisition
        """

        camera_single_acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = camera_single_acquisition.SupportedCameras

        # Select the requested camera
        camera_single_acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(camera_name)]

        camera_settings = camera_single_acquisition.CameraSettings

        if readout_area is not None:
            camera_settings.ReadoutArea = readout_area

        if binning is not None:  # if a binning keyword argument was entered
            supported_binnings = camera_single_acquisition.CameraSettings.Capabilities.SupportedBinnings
            if binning == '4k':
                camera_settings.Binning = supported_binnings[0]  # 4k images (4096 x 4096)
            elif binning == '2k':
                camera_settings.Binning = supported_binnings[1]  # 2k images (2048 x 2048)
            elif binning == '1k':
                camera_settings.Binning = supported_binnings[2]  # 1k images (1024 x 1024)
            elif binning == '0.5k':
                camera_settings.Binning = supported_binnings[3]  # 0.5k images (512 x 512)
            else:
                print('Unknown Binning Type. Binning not changed.')

        if exposure_time is not None:
            camera_settings.ExposureTime = exposure_time

        acquisition = Acquisition(camera_single_acquisition.Acquire())

        return acquisition

    def print_camera_capabilities(self, camera_name):
        """
        Print out the capabilities of the requested camera.

        :param camera_name: str:
            The camera of which you want to know the capabilities:
            - 'BM-Ceta'
            - 'BM-Falcon'

        :return: None.
        """
        camera_single_acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = camera_single_acquisition.SupportedCameras

        # Select the requested camera
        camera_single_acquisition.Camera = supported_cameras[[c.name for c in supported_cameras].index(camera_name)]

        print("\nSupported Binnings:")
        print(camera_single_acquisition.CameraSettings.Capabilities.SupportedBinnings)

        print("\nExpose Time Range:")
        print(camera_single_acquisition.CameraSettings.Capabilities.ExposureTimeRange)

        print("\nSupports Dose Fractions:")
        print(camera_single_acquisition.CameraSettings.Capabilities.SupportsDoseFractions)

        print("\nMaximum Number of Dose Fractions:")
        print(camera_single_acquisition.CameraSettings.Capabilities.MaximumNumberOfDoseFractions)

        print("\nSupports Drift Correction:")
        print(camera_single_acquisition.CameraSettings.Capabilities.SupportsDriftCorrection)

        print("\nSupports Electron Counting:")
        print(camera_single_acquisition.CameraSettings.Capabilities.SupportsElectronCounting)

        print("\nSupports EER")
        print(camera_single_acquisition.CameraSettings.Capabilities.SupportsEER)

        print("\nSupports Recording Duration:")
        print(camera_single_acquisition.CameraSettings.Capabilities.SupportsRecordingDuration)

    def get_available_cameras(self):
        """
        Get a list of the available cameras.
        :return: list of strings:
            A list of the available cameras, by name.
        """
        camera_single_acquisition = self._tem_advanced.Acquisitions.CameraSingleAcquisition
        supported_cameras = camera_single_acquisition.SupportedCameras
        return supported_cameras
