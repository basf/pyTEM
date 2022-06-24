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
    Return the microscope to a safe state and exit the MicroED script.
    :param microscope: pyTEM (or None):
        The microscope interface.
    :param status: int:
        Exit status, one of:
            1: Early exit (script not yet complete)
            0: Success
            -1: Failure
    """
    if microscope is not None:
        warnings.warn("Returning the microscope to a safe state...")
        microscope.make_safe()
    sys.exit(status)
