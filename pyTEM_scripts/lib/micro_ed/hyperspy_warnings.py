"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import hyperspy.api as hs


def turn_off_hyperspy_warnings():
    """
    By default, HyperSpy warns the user if one of the GUI packages is not installed.
    This function turns these warnings off.
    :return: None.
    """
    hs.preferences.GUIs.warn_if_guis_are_missing = False
    hs.preferences.save()


def turn_on_hyperspy_warnings():
    """
    Turn on Hyperspy warnings for missing GUI packages.
    :return: None.
    """
    hs.preferences.GUIs.warn_if_guis_are_missing = True
    hs.preferences.save()
