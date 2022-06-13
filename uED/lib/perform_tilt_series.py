"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import math


def perform_tilt_series(microscope, camera, integration_time, binning, alpha_arr, shifts, out_file):
    """
    Actually perform a tilt series and save the returns to file.

    :param microscope: TEMInterface:
        A TEMInterface interface to the microscope.
    :param camera: str:
        The name of the camera being
    :param integration_time: float:
        Total exposure time for a single image in seconds.
    :param binning: Photo resolution, one of:
        - '4k' for 4k images (4096 x 4096; sampling=1)
        - '2k' for 2k images (2048 x 2048; sampling=2)
        - '1k' for 1k images (1024 x 1024; sampling=3)
        - '0.5k' for 05.k images (512 x 512; sampling=8)
    :param alpha_arr:
    :param shifts:
    :param out_file:
    :return:
    """
    # microscope.set_stage_position(alpha=alpha_arr[0])  # Move to the start angle

    # reference = microscope.single_acquisition(camera_name=camera, binning=binning, exposure_time=None, readout_area=None)

    raise NotImplementedError
