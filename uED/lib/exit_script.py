"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import sys
import warnings


def exit_script(microscope, status):
    """
    Return the microscope to a safe state and exit the MicroED script.
    :param microscope: 
    :param status: int:
    Exit status, one of:
        -1: Failure
        0: Success
        1: Early exit (script not yet complete)
    """
    if microscope is not None:
        warnings.warn("Returning the microscope to a safe state...")
        microscope.make_safe()
    sys.exit(status)
