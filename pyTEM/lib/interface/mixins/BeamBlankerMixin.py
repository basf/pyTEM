"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import comtypes.client as cc


class BeamBlankerMixin:
    """
    Microscope beam blanker controls, including functions to blank and unblank the beam.
    This mixin was developed in support of pyTEM.pyTEM, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem: type(cc.CreateObject("TEMScripting.Instrument"))
    except OSError:
        pass

    def beam_is_blank(self) -> None:
        """
        Check if the beam is blanked.
        :return: Beam status: bool:
             True: Beam is blanked.
             False: Beam is unblanked.
        """
        return self._tem.Illumination.BeamBlanked

    def blank_beam(self) -> None:
        """
        Blank the beam.
        :return: None.
        """
        if self.beam_is_blank():
            print("The beam is already blanked.. no changes made.")
            return

        # Go ahead and blank the beam
        self._tem.Illumination.BeamBlanked = True

    def unblank_beam(self) -> None:
        """
        Unblank the beam.
        :return: None.
        """
        if not self.beam_is_blank():
            print("The beam is already unblanked.. no changes made.")
            return

        self._tem.Illumination.BeamBlanked = False


class BeamBlankerInterface(BeamBlankerMixin):
    """
    A microscope interface with only beam blanker controls.
    """

    def __init__(self):
        try:
            self._tem = cc.CreateObject("TEMScripting.Instrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e
