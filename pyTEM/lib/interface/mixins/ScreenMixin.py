"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import comtypes.client as cc


class ScreenMixin:
    """
    Microscope FluCam screen controls.

    This mixin was developed in support of pyTEM.Interface, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem: type(cc.CreateObject("TEMScripting.Instrument"))
    except OSError:
        pass

    def get_screen_position(self) -> str:
        """
        :return: str: The position of the FluCam's fluorescent screen, one of:
            - 'retracted' (required to take images)
            - 'inserted' (required to use the FluCam to view the live image)
        """
        if self._tem.Camera.MainScreen == 2:
            return "retracted"

        elif self._tem.Camera.MainScreen == 3:
            return "inserted"

        else:
            raise Exception("Error: Current screen position (" + str(self._tem.Camera.MainScreen) + ") not recognized.")

    def insert_screen(self) -> None:
        """
        Insert the FluCam's fluorescent screen.
        This is required to use the FluCam to view the live image.
        :return: None.
        """
        if self.get_screen_position() == "inserted":
            print("The microscope screen is already inserted.. no changes made.")
            return

        self._tem.Camera.MainScreen = 3  # Insert the screen

    def retract_screen(self) -> None:
        """
        Retract the FluCam's fluorescent screen.
        This is required to take images.
        :return: None.
        """
        if self.get_screen_position() == "retracted":
            print("The microscope screen is already removed.. no changes made.")
            return

        self._tem.Camera.MainScreen = 2  # Remove the screen
