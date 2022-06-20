"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import comtypes.client as cc


class BeamBlankerMixin:
    """
    Microscope beam blanker controls, including functions to blank and unblank the beam.

    This mixin was developed in support of TEMInterface.TEMInterface, but can be included in other projects where helpful.
    """
    _tem: type(cc.CreateObject("TEMScripting.Instrument"))

    def beam_is_blank(self):
        """
        Check if the beam is blanked.
        :return: Beam status: bool:
             True: Beam is blanked.
             False: Beam is unblanked.
        """
        return self._tem.Illumination.BeamBlanked

    def blank_beam(self):
        """
        Blank the beam.
        :return: None.
        """
        if self.beam_is_blank():
            print("The beam is already blanked.. no changes made.")
            return

        # Go ahead and blank the beam
        self._tem.Illumination.BeamBlanked = True

    def unblank_beam(self):
        """
        Unblank the beam.
        :return: None.
        """
        if not self.beam_is_blank():
            print("The beam is already unblanked.. no changes made.")
            return

        self._tem.Illumination.BeamBlanked = False
