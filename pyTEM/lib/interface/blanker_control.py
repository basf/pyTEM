"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import time

from numpy.typing import ArrayLike

from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerInterface


def blanker_control(num_acquisitions: int, barriers: ArrayLike, exposure_time: float, verbose: bool = False) -> None:
    """
    Support pyTEM.Interface.acquisition() with simultaneous blanker control. For more information on why this
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
    :param exposure_time: float:
        Exposure time for a single acquisition, in seconds. # TODO: Allow variable exposure times

    :param verbose: (optional; default is False):
           Print out extra information. Useful for debugging and timing analysis.

    :return: None.
    """
    if num_acquisitions <= 0:
        raise Exception("Error: blanker_control() requires we perform at least one acquisition.")

    if len(barriers) != num_acquisitions:
        raise Exception("Error: blanker_control() didn't receive the expected number of barriers. Expected "
                        + str(num_acquisitions) + ", but received " + str(len(barriers)) + ".")

    # Build an interface to access blanker controls.
    interface = BeamBlankerInterface()

    # Loop through the requested number of acquisitions.
    for i in range(num_acquisitions):

        barriers[i].wait()  # Synchronize with the main thread/process.

        # Wait while the camera is blind.
        time.sleep(exposure_time)

        # Unblank while the acquisition is active.
        interface.unblank_beam()
        beam_unblank_time = time.time()

        # Wait while the camera is recording.
        time.sleep(exposure_time)

        # Re-blank the beam.
        interface.blank_beam()
        beam_reblank_time = time.time()

        if verbose:
            print("-- Timing results from blanker_control() for acquisition #" + str(i) + " --")

            print("\nUnblanked the beam at: " + str(beam_unblank_time))
            print("Re-blanked the beam at: " + str(beam_reblank_time))
            print("Total time spent with the beam unblanked: " + str(beam_reblank_time - beam_unblank_time))
