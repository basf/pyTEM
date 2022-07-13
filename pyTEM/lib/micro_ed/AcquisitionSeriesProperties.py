"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

from numpy.typing import ArrayLike

from pyTEM.lib.interface.tem_tilt_speed import tem_tilt_speed


class AcquisitionSeriesProperties:
    """
    Basically just a datastructure to hold tilt series acquisition properties.

    Public Attributes:
        camera_name:      str:              The name of the camera being used.
        alpha_arr:        array of floats:  An complete array of the tilt acquisition's alpha start-stop values.
        alpha_step:       float:            Degrees between adjacent acquisitions.
        alphas:           array of floats:  The middle alpha values of the tilt acquisition.
        integration_time: int:              Total exposure time for a single image in seconds.
        sampling:         str:              Photo resolution.
        tilt_speed:       float:            Alpha fractional tilt speed required by Interface.set_stage_position().

    Protected Attributes:
        None.

    Private Attributes:
        None.
    """

    def __init__(self, camera_name: str, alpha_arr: ArrayLike, integration_time: float = 3, sampling: str = '1k'):
        """
        :param camera_name: str:
            The name of the camera being used.
        :param alpha_arr: array of floats:
            An array of alpha start-stop values in the tilt acquisition.
        :param sampling: str (optional; default is '1k'):
            Photo resolution, one of:
                - '4k' for 4k images (4096 x 4096; sampling=1)
                - '2k' for 2k images (2048 x 2048; sampling=2)
                - '1k' for 1k images (1024 x 1024; sampling=3)
                - '0.5k' for 05.k images (512 x 512; sampling=8)
        :param integration_time: float (optional; default is 3):
            Total exposure time for a single image in seconds.
        """
        self.alpha_step = alpha_arr[1] - alpha_arr[0]
        self.camera_name = camera_name
        self.alpha_arr = alpha_arr
        self.integration_time = integration_time
        self.sampling = sampling
        self.alphas = alpha_arr[0:-1] + self.alpha_step / 2
        time_tilting = len(self.alphas) * self.integration_time  # s
        distance_tilting = abs(self.alpha_arr[-1] - self.alpha_arr[0])  # deg
        tilt_velocity = distance_tilting / time_tilting  # deg / s
        self.tilt_speed = tem_tilt_speed(tilt_velocity)

    def __str__(self):
        return "-- Acquisition Properties -- " \
               "\nName of the camera being used: " + str(self.camera_name) + \
               "\nAn array of the tilt acquisition's alpha start-stop values: " + str(self.alpha_arr) + \
               "\nThe middle alpha values of the tilt acquisition: " + str(self.alphas) + \
               "\nTotal exposure time for a single image: " + str(round(self.integration_time, 4)) + " [seconds]" + \
               "\nPhoto resolution: " + str(self.sampling) + \
               "\nAlpha tilt speed: " + str(round(self.tilt_speed, 4)) + " [Thermo Fisher speed units]"


if __name__ == "__main__":

    import numpy as np

    start_alpha = -35
    stop_alpha = 30
    step_alpha = 1
    num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
    alpha_arr_ = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)

    acq_prop = AcquisitionSeriesProperties(camera_name="BM-Ceta", alpha_arr=alpha_arr_, integration_time=3,
                                           sampling='1k')

    print(acq_prop)
