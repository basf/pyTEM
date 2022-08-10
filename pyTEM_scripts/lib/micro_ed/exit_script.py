"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import sys
import warnings

from typing import Union

from pyTEM.Interface import Interface


def exit_script(microscope: Union[Interface, None], status: int) -> None:
    """
    Return the microscope to a safe state, zero the alpha tilt, zero the image and beam shifts, and restore the
     projection mode to 'imaging'.

    :param microscope: pyTEM.Interface (or None):
        The microscope interface.

    :param status: int:
        Exit status, one of:
            0: Success
            1: Early exit (script not yet complete) / Failure
    """
    if microscope is not None:
        warnings.warn("Returning the microscope to a safe state, zeroing the alpha tilt, "
                      "zeroing the image and beam shifts, and restoring the projection mode to 'imaging'...")
        microscope.make_safe()
        microscope.set_projection_mode(new_projection_mode="imaging")
        microscope.set_stage_position_alpha(alpha=0)
        microscope.zero_shifts()

    sys.exit(status)
