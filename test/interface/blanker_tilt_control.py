"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import time

import comtypes.client as cc

from typing import Union
from numpy.typing import ArrayLike

from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerMixin
from pyTEM.lib.interface.mixins.StageMixin import StageMixin
from pyTEM.lib.interface.tem_tilt_speed import tem_tilt_speed


def blanker_tilt_control(num_acquisitions: int,
                         barriers: ArrayLike,
                         exposure_time: float,
                         blanker_optimization: bool,
                         tilt_bounds: Union[ArrayLike, None],
                         verbose: bool = False) -> None:
    """
    Support pyTEM.Interface.acquisition() with the control of blanking and/or tilting. For more information on why this
     is helpful, please refer to pyTEM.Interface.acquisition().

     This function is to be run in a parallel thread or process while an acquisition (or acquisition series) is being
     performed from the main thread/process.

    :param num_acquisitions: int:
        The number of acquisitions to perform. Must be at least 1.
    :param barriers: Array of mp.Barrier:
        An array of multiprocessing barriers, these are used to synchronize with the main thread/process before each
         acquisition.
    :param exposure_time: float:
        Exposure time for a single acquisition, in seconds. If tilting, then this can be thought of more as an
         integration time.  # TODO: Allow variable exposure times

    :param blanker_optimization: bool:
        Whether to perform blanker optimization or not.
    :param tilt_bounds: float (optional; default is None):
        An array of alpha start-stop values for the tilt acquisition(s), in degrees.
        len(tilt_bounds) should equal num_acquisitions + 1
        Doesn't need to be evenly spaced, the tilt speed will adapt for each individual acquisition.
        We will ensure we are at the starting angle (tilt_bounds[0]) before performing the first acquisition.
        Upon return the stage is left at the final destination -> tilt_bounds[-1].
        If None, or an array of length 0, then no tilting is performed.

    :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging.

    :return: None.
    """
    if num_acquisitions <= 0:
        raise Exception("Error: blanker_tilt_control() requires we perform at least one acquisition.")

    if len(barriers) != num_acquisitions:
        raise Exception("Error: blanker_tilt_control() didn't receive the expected number of barriers. Expected "
                        + str(num_acquisitions) + ", but received " + str(len(barriers)) + ".")

    # Build an interface with stage and blanker controls that this process can use to control the microscope.
    interface = StageAndBlankerInterface()

    tilting = False  # Assume we are not tilting
    if tilt_bounds is not None:
        # Then we expect an array, either of length 0 or num_acquisitions + 1.
        if len(tilt_bounds) == 0:
            pass
        if len(tilt_bounds) == num_acquisitions + 1:
            tilting = True  # We need to tilt.

            # Ensure we are at the starting tilt angle.
            if not math.isclose(interface.get_stage_position_alpha(), tilt_bounds[0], abs_tol=0.01):
                if verbose:
                    print("Moving the stage to the start angle, \u03B1=" + str(tilt_bounds[0]))
                interface.set_stage_position_alpha(alpha=tilt_bounds[0], speed=0.25, movement_type="go")
        else:
            raise Exception("Error: The length of the non-empty tilt_bounds array (" + str(len(tilt_bounds))
                            + ") received by blanker_tilt_control() is inconsistent with the requested number of "
                              "requested acquisitions (" + str(num_acquisitions) + ").")

    # Declarations for warning suppression
    beam_unblank_time, beam_reblank_time, tilt_start_time, tilt_stop_time = None, None, None, None

    # Loop through the requested number of acquisitions.
    for i in range(num_acquisitions):

        if tilting:
            # Compute tilt speed
            distance_tilting = abs(tilt_bounds[i + 1] - tilt_bounds[i])  # deg
            tilt_speed = distance_tilting / exposure_time  # deg / s
            tilt_speed = tem_tilt_speed(tilt_speed)  # convert to fractional speed as required by the stage setters.

        barriers[i].wait()  # Synchronize with the main process.

        # Wait while the camera is blind.
        time.sleep(exposure_time)

        if blanker_optimization:
            # Unblank while the acquisition is active.
            interface.unblank_beam()
            beam_unblank_time = time.time()

        if tilting:
            # Perform a tilt, this blocks the program for the full integration time so no need to sleep.
            tilt_start_time = time.time()
            interface.set_stage_position_alpha(alpha=tilt_bounds[i + 1], speed=tilt_speed, movement_type="go")
            tilt_stop_time = time.time()
        else:
            # Otherwise, we have to wait while the camera is recording.
            time.sleep(exposure_time)

        if blanker_optimization:
            # Re-blank the beam.
            interface.blank_beam()
            beam_reblank_time = time.time()

        if verbose:
            print("-- Timing results from blanker_tilt_control() for acquisition #" + str(i) + " --")
            if blanker_optimization:
                print("\nUnblanked the beam at: " + str(beam_unblank_time))
                print("Re-blanked the beam at: " + str(beam_reblank_time))
                print("Total time spent with the beam unblanked: " + str(beam_reblank_time - beam_unblank_time))
            if tilting:
                print("\nStarted titling at: " + str(tilt_start_time))
                print("Stopped tilting at: " + str(tilt_stop_time))
                print("Total time spent tilting: " + str(tilt_stop_time - tilt_start_time))


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
