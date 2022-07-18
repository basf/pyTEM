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

    To ensure beam is unblanked in time, we unblank 0.025 seconds early. And to ensure the beam remains unblanked for
     the whole time the camera is recording, we re-blank 0.025 seconds late. This means the beam is unblanked for
     exposure_time + 0.05 seconds.

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

        # Wait while the camera is blind. Notice we wait a little longer than the integration time, this is because
        #  the acquisition command takes a little longer to issue than the unblank command. We should wait about an
        #  extra 0.45 seconds, but we unblank 0.025 seconds early to ensure the beam is unblanked in time.
        time.sleep(0.425 + exposure_time)

        # Unblank while the acquisition is active.
        beam_unblank_time = time.time()
        interface.unblank_beam()  # Command takes 0.15 s

        # Wait while the camera is recording.
        # Notice we wait a little extra just to be sure the beam is unblanked for whole time the camera is recording.
        time.sleep(0.025 + exposure_time)

        # Re-blank the beam.
        beam_reblank_time = time.time()
        interface.blank_beam()  # Command takes 0.15 s

        if verbose:
            print("-- Timing results from blanker_control() for acquisition #" + str(i) + " --")

            print("\nIssued the command to unblanked the beam at: " + str(beam_unblank_time))
            print("Issued the command to re-blanked the beam at: " + str(beam_reblank_time))
            # Extra 0.15 for unblank command + 0.05 extra unblanked time
            print("Total time spent with the beam unblanked: " + str(beam_reblank_time - beam_unblank_time - 0.20))
