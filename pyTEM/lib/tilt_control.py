"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import time

from typing import Union
from numpy.typing import ArrayLike

from pyTEM.lib.mixins.StageMixin import StageInterface
from pyTEM.lib.tem_tilt_speed import tem_tilt_speed


def tilt_control(num_acquisitions: int, barriers: ArrayLike, integration_time: float,
                 tilt_bounds: Union[ArrayLike, None], verbose: bool = False) -> None:
    """
    Support pyTEM.Interface.acquisition() with the simultaneous tilt control. For more information on why this
     is helpful, please refer to pyTEM.Interface.acquisition().

     This function is to be run in a parallel thread or process while an acquisition (or acquisition series) is being
     performed from the main thread/process.

    :param num_acquisitions: int:
        The number of acquisitions to perform. Must be at least 1.
    :param barriers: Array of mp.Barrier:
        An array of barriers, these are used to synchronize with the main thread/process before each
         acquisition.
        If this is being run in a parallel thread, this should be an array of threading.Barrier objects or similar. And
         if it is being run in a parallel process then this should be an array of multiprocessing.Barrier objects or
         similar. Either way, the barriers need to have a party allocated for the process/thread in which this function
         is running.
    :param integration_time: float:
        Exposure time for a single acquisition, in seconds. # TODO: Allow variable integration times

    :param tilt_bounds: float (optional; default is None):
        An array of alpha start-stop values for the tilt acquisition(s), in degrees.
        len(tilt_bounds) should equal num_acquisitions + 1
        Doesn't need to be evenly spaced, the tilt speed will adapt for each individual acquisition.
        We will ensure we are at the starting angle (tilt_bounds[0]) before performing the first acquisition.
        Upon return the stage is left at the final destination -> tilt_bounds[-1].

    :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging.

    :return: None.
    """
    if num_acquisitions <= 0:
        raise Exception("Error: tilt_control() requires we perform at least one acquisition.")

    if len(barriers) != num_acquisitions:
        raise Exception("Error: tilt_control() didn't receive the expected number of barriers. Expected "
                        + str(num_acquisitions) + ", but received " + str(len(barriers)) + ".")

    if len(tilt_bounds) != num_acquisitions + 1:
        raise Exception("Error: The length of the tilt_bounds array (" + str(len(tilt_bounds))
                        + ") received by tilt_control() is inconsistent with the requested number of "
                          "requested acquisitions (" + str(num_acquisitions) + ").")

    # Build an interface with stage and blanker controls that this process can use to control the microscope.
    interface = StageInterface()

    # Ensure we are at the starting tilt angle.
    if not math.isclose(interface.get_stage_position_alpha(), tilt_bounds[0], abs_tol=0.01):
        if verbose:
            print("Moving the stage to the start angle, \u03B1=" + str(tilt_bounds[0]))
        interface.set_stage_position_alpha(alpha=tilt_bounds[0], speed=0.25, movement_type="go")

    # Loop through the requested number of acquisitions.
    for i in range(num_acquisitions):

        # Compute tilt speed
        distance_tilting = abs(tilt_bounds[i + 1] - tilt_bounds[i])  # deg
        tilt_speed = distance_tilting / integration_time  # deg / s
        tilt_speed = tem_tilt_speed(tilt_speed)  # convert to fractional speed as required by the stage setters.

        barriers[i].wait()  # Synchronize with the main process.

        # Wait while the camera is blind. Notice we wait a little longer than the integration time, this is because
        #  the acquisition command takes a little longer to issue than the tilt command.
        time.sleep(0.03 + integration_time)

        # Perform tilt. This blocks the program for the full integration time so no need to sleep.
        tilt_start_time = time.time()
        interface.set_stage_position_alpha(alpha=tilt_bounds[i + 1], speed=tilt_speed, movement_type="go")
        tilt_stop_time = time.time()

        if verbose:
            print("-- Timing results from tilt_control() for acquisition #" + str(i) + " --")

            print("\nStarted titling at: " + str(tilt_start_time))
            print("Stopped tilting at: " + str(tilt_stop_time))
            print("Total time spent tilting: " + str(tilt_stop_time - tilt_start_time))
