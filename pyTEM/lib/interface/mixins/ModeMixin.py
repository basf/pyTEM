"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import comtypes.client as cc


class ModeMixin:
    """
    Microscope mode controls, including those for projection and illumination.

    This mixin was developed in support of pyTEM.pyTEM, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem: type(cc.CreateObject("TEMScripting.Instrument"))
    except OSError:
        pass

    def get_mode(self) -> str:
        """
        :return: str:
            The current microscope mode, one of:
            - "TEM" (normal imaging mode)
            - "STEM" (Scanning TEM)
        """
        if self._tem.InstrumentModeControl.InstrumentMode == 0:
            return "TEM"

        elif self._tem.InstrumentModeControl.InstrumentMode == 1:
            return "STEM"  # Scanning TEM

        else:
            raise Exception("Error: Microscope mode unknown.")

    def set_mode(self, new_mode: str) -> None:
        """
        Change the operational mode of the microscope.

        :param new_mode: str:
            The new microscope mode, one of:
             - "STEM" (scanning TEM; the beam is focused at a large angle and is converged into a focal point)
             - "TEM" (parallel electron beams are focused perpendicular to the sample plane)
        :return: None.
        """
        new_mode = str(new_mode).upper()

        if self.get_mode() == new_mode:
            print("The microscope is already in '" + new_mode + "' mode.. no changes made.")
            return

        if new_mode == "TEM":
            self._tem.InstrumentModeControl.InstrumentMode = 0  # Switch microscope into TEM Mode (normal imaging mode)

        elif new_mode == "STEM":
            self._tem.InstrumentModeControl.InstrumentMode = 1  # Switch microscope into STEM Mode (scanning TEM)

        else:
            print("The requested mode (" + new_mode + ") isn't recognized.. no changes made.")

    def get_projection_mode(self) -> str:
        """
        :return: str:
            The current projection mode, either "Diffraction" or "Imaging".
        """
        if self._tem.Projection.Mode == 1:
            return "Imaging"

        elif self._tem.Projection.Mode == 2:
            return "Diffraction"

        else:
            raise Exception("Error: Projection mode unknown.")

    def set_projection_mode(self, new_projection_mode: str) -> None:
        """
        :param new_projection_mode: str:
            The new projection mode, one of:
            - "Diffraction" (reciprocal space)
            - "Imaging" (real space)
        :return: None
        """
        new_projection_mode = str(new_projection_mode).title()

        if self.get_projection_mode() == new_projection_mode.title():
            print("The microscope is already in '" + new_projection_mode + "' mode.. no changes made.")
            return

        screen_position = self.get_screen_position()

        if screen_position == 'Removed':
            # Insert the screen before switching moves to avoid damaging the camera
            self.insert_screen()

        if new_projection_mode in {"Imaging", "I"}:
            self._tem.Projection.Mode = 1  # Switch microscope into imaging mode
            if screen_position == 'Removed':
                # Put the screen back where the user had it
                self.remove_screen()

        elif new_projection_mode in {"Diffraction", "D"}:
            self._tem.Projection.Mode = 2  # Switch microscope into diffraction mode
            if screen_position == 'Removed':
                # Put the screen back where the user had it
                self.remove_screen()

        else:
            print("The requested projection mode (" + new_projection_mode + ") isn't recognized.. no changes made.")

    def get_projection_submode(self) -> str:
        """
        :return: str:
            The current projection sub-mode.
        """
        return self._tem.Projection.SubModeString

    def print_projection_submode(self):
        """
        :return: str:
            The current projection submode, along with the zoom range.
        """
        submode = self._tem.Projection.SubMode
        if submode == 1:
            print("LM: 25 x -> 2300 x Zoom")
        elif submode == 2:
            print("M: 2050 x -> 3300 x Zoom")
        elif submode == 3:
            print("SA: 4300 x -> 630 kx Zoom")  # When in STEM mode, this is the only allowed submode
        elif submode == 4:
            print("MH: 650 kx -> 1.05 Mx Zoom")
        elif submode == 5:
            print("LAD: 4.6 m -> 1,400 m Diffraction")
        elif submode == 6:
            print("D: 14 mm -> 5.7 m Diffraction")
        else:
            print("Submode " + str(submode) + " (" + str(self._tem.Projection.SubModeString) + ") not recognized.")

    def get_illumination_mode(self):
        """
        :return: str:
            The current illumination mode, one of:
            - "Nanoprobe" (used to get a small convergent electron beam)
            - "Microprobe" (provides a nearly parallel illumination at the cost of a larger probe size)
        """
        if self._tem.Illumination.Mode == 0:
            return "Nanoprobe"

        elif self._tem.Illumination.Mode == 1:
            return "Microprobe"

        else:
            raise Exception("Error: Projection mode '" + str(self._tem.Illumination.Mode) + "' not recognized.")

    def set_illumination_mode(self, new_mode: str) -> None:
        """
        Change the illumination mode of the microscope.
        Note: (Nearly) no effect for low magnifications (LM).

        :param new_mode: str:
            The new illumination mode, one of:
             - "Nanoprobe" (used to get a small convergent electron beam)
             - "Microprobe" (provides a nearly parallel illumination at the cost of a larger probe size)
        :return: None.
        """
        new_mode = str(new_mode).title()

        if self.get_illumination_mode() == new_mode:
            print("The microscope is already in '" + new_mode + "' mode.. no changes made.")
            return

        if new_mode == "Nanoprobe":
            self._tem.Illumination.Mode = 0

        elif new_mode == "Microprobe":
            self._tem.Illumination.Mode = 1

        else:
            print("The requested illumination mode (" + new_mode + ") isn't recognized.. no changes made.")

    def get_screen_position(self) -> str:
        """
        :return: str: The position of the FluCam's fluorescent screen, one of:
            - 'Removed' (required to take images)
            - 'Inserted' (required to use the FluCam to view the live image)
        """
        if self._tem.Camera.MainScreen == 2:
            return "Removed"

        elif self._tem.Camera.MainScreen == 3:
            return "Inserted"

        else:
            raise Exception("Error: Current screen position (" + str(self._tem.Camera.MainScreen) + ") not recognized.")

    def insert_screen(self) -> None:
        """
        Insert the FluCam's fluorescent screen.
        This is required to use the FluCam to view the live image.
        :return: None.
        """
        if self.get_screen_position() == "Inserted":
            print("The microscope screen is already inserted.. no changes made.")
            return

        self._tem.Camera.MainScreen = 3  # Insert the screen

    def remove_screen(self) -> None:
        """
        Remove the FluCam's fluorescent screen.
        This is required to take images.
        :return: None.
        """
        if self.get_screen_position() == "Removed":
            print("The microscope screen is already removed.. no changes made.")
            return

        self._tem.Camera.MainScreen = 2  # Remove the screen
