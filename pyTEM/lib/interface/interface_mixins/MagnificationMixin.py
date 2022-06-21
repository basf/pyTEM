"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import warnings
import comtypes.client as cc


class MagnificationMixin:
    """
    Microscope magnification controls, including those for getting and setting the current microscope magnification and
     magnification index.

    This mixin was developed in support of pyTEM.pyTEM, but can be included in other projects where helpful.
    """
    _tem: type(cc.CreateObject("TEMScripting.Instrument"))

    def get_mode(self):
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

    def get_projection_mode(self):
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

    def get_magnification(self):
        """
        :return: float:
            The current magnification value.
            Note: Returns Nan when the instrument is in TEM diffraction mode.
        """
        if self.get_mode() == "TEM":
            if self.get_projection_mode() == "Imaging":
                return self._tem.Projection.Magnification
            elif self.get_projection_mode() == "Diffraction":
                warnings.warn("Since we are in TEM diffraction mode, get_magnification() is returning Nan...")
                return math.nan
            else:
                raise Exception("Projection mode (" + str(self._tem.Projection.Mode) + ") not recognized.")

        elif self.get_mode() == "STEM":
            # TODO: Figure out how to reliably obtain the magnification while in STEM mode.
            warnings.warn("get_magnification() is not working as expected while the instrument is in STEM mode.")
            return self._tem.Illumination.StemMagnification

        else:
            raise Exception("Projection mode (" + str(self._tem.Projection.Mode) + ") not recognized.")

    def set_stem_magnification(self, new_magnification):
        """
        Update the STEM microscope magnification.

        This method requires the microscope be in TEM mode. For magnification updates while in TEM mode, please use
         set_tem_magnification().

        If the input is not one of the preset values, then the TEM will automatically set the magnification to the next
         nearest defined magnification value.

        :param new_magnification: float:
            The new STEM magnification. Available magnifications in STEM mode (SA) range from 4,300 to 630,000.
        :return: None.
        """
        if self.get_mode() == "TEM":
            print("The microscope is currently in TEM mode. To adjust the magnification in TEM mode, please use "
                  "set_magnification_tem().. no changes made.")

        elif self.get_mode() == "STEM":
            # TODO: Figure out how to reliably set the magnification while in STEM mode.
            warnings.warn("set_stem_magnification() is not working as expected. STEM magnification may or may not have"
                          " been updated.")
            self._tem.Illumination.StemMagnification = new_magnification

        else:
            raise Exception("Error: Current microscope mode unknown.")

    def set_tem_magnification(self, new_magnification_index):
        """
        Update the TEM microscope magnification.

        The method requires the microscope be in TEM mode. For magnification updates while in STEM mode, please use
         set_stem_magnification().

        :param new_magnification_index: int:
            Magnification index; an integer value between 1 (25 x Zoom) and 44 (1.05 Mx Zoom).

        :return: None.
        """
        new_magnification_index = int(new_magnification_index)
        if self.get_mode() == "STEM":
            print("The microscope is currently in STEM mode. To adjust the magnification in STEM mode, please use "
                  "set_magnification_stem().. no changes made.")

        elif self.get_mode() == "TEM":
            if new_magnification_index > 44:  # Upper bound (Very zoomed in; 1.05 Mx Zoom)
                warnings.warn(
                    "The requested TEM magnification index (" + str(new_magnification_index) + ") is greater than "
                    "the maximum allowable value of 44. Therefore, the magnification index is being set to 44 "
                    "(1.05 Mx Zoom).")
                new_magnification_index = 44
            elif new_magnification_index < 1:  # Lower bound (Very zoomed out; 25 x Zoom)
                warnings.warn("The requested TEM magnification index (" + str(new_magnification_index) + ") is less "
                              "than the minimum allowable value of 1. Therefore, the magnification index is being set "
                              "to 1 (25 x Zoom).")
                new_magnification_index = 1
            self._tem.Projection.MagnificationIndex = new_magnification_index

        else:
            raise Exception("Error: Current microscope mode unknown.")

    def shift_tem_magnification(self, magnification_shift):
        """
        Shift the TEM magnification up or down by the provided magnification_shift. This is equivalent to turning the
         magnification nob by magnification_shift notches clockwise (negative values of magnification_shift are
         equivalent to counterclockwise nob rotations)

        :param magnification_shift: float
            An up/down shift from current magnification; Examples: 7, -2, 10
            Should the request shift exceed the magnification bounds (1 to 44), magnification will default to the
            nearest bound.

        :return: None
        """
        if self.get_mode() == "STEM":
            print("The microscope is currently in STEM mode. To adjust the magnification in STEM mode, please use "
                  "set_magnification_stem().. no changes made.")

        elif self.get_mode() == "TEM":
            current_magnification_index = self.get_magnification_index()
            new_magnification_index = current_magnification_index + int(magnification_shift)

            if new_magnification_index > 44:  # Upper bound (Very zoomed in; 1.05 Mx Zoom)
                warnings.warn("The requested TEM magnification index shift (" + str(magnification_shift) + ") would "
                              "cause the instrument to exceed the maximum allowable value of 44. Therefore, the "
                              "magnification index is being set to 44 (1.05 Mx Zoom).")
                new_magnification_index = 44
            elif new_magnification_index < 1:  # Lower bound (Very zoomed out; 25 x Zoom)
                warnings.warn("The requested TEM magnification index shift (" + str(magnification_shift) + ") would "
                              "cause the instrument to exceed the minimum allowable value of 1. Therefore, the "
                              "magnification index is being set to 1 (25 x Zoom).")
                new_magnification_index = 1

            self._tem.Projection.MagnificationIndex = new_magnification_index

        else:
            raise Exception("Error: Current microscope mode unknown.")

    def get_magnification_index(self):
        """
        :return: int:
            The magnification index (this is what sets the magnification when the microscope is in TEM mode).
        """
        if self.get_mode() == "STEM":
            warnings.warn("Magnification index is not relevant for STEM mode.")

        return self._tem.Projection.MagnificationIndex

    def print_available_magnifications(self):
        """
        Print a list of available magnifications (when in TEM Imaging mode, magnification indices are also printed out).

        :return: None.
        """
        print("The microscope is currently in " + self.get_mode() + " " + self.get_projection_mode() + " mode. "
              "Available magnifications are as follows:")

        if self.get_mode() == "TEM":

            if self.get_projection_mode() == "Imaging":
                available_magnifications = [25.0, 34.0, 46.0, 62.0, 84.0, 115.0, 155.0, 210.0, 280.0, 380.0,
                                            510.0, 700.0, 940.0, 1300.0, 1700.0, 2300.0, 2050.0, 2600.0, 3300.0,
                                            4300.0, 5500.0, 7000.0, 8600.0, 11000.0, 14000.0, 17500.0, 22500.0,
                                            28500.0, 36000.0, 46000.0, 58000.0, 74000.0, 94000.0, 120000.0,
                                            150000.0, 190000.0, 245000.0, 310000.0, 390000.0, 500000.0, 630000.0,
                                            650000.0, 820000.0, 1050000.0]

                print("{:<20} {:<20}".format("Magnification Index", "Magnification [x Zoom]"))
                for i, magnification in enumerate(available_magnifications):
                    print("{:<20} {:<20}".format(i + 1, magnification))

            elif self.get_projection_mode() == "Diffraction":
                warnings.warn("Magnification not relevant in TEM diffraction mode.")  # TODO: Is this true?

            else:
                warnings.warn("Projection mode not recognized.. no available magnifications found.")

        elif self.get_mode() == "STEM":

            if self.get_projection_mode() == "Imaging":
                available_magnifications = [4300.0, 5500.0, 7000.0, 8600.0, 11000.0, 14000.0, 17500.0, 22500.0,
                                            28500.0, 36000.0, 46000.0, 58000.0, 74000.0, 94000.0, 120000.0,
                                            150000.0, 190000.0, 245000.0, 310000.0, 390000.0, 500000.0, 630000.0]

            elif self.get_projection_mode() == "Diffraction":
                available_magnifications = [320.0, 450.0, 630.0, 900.0, 1250.0, 1800.0, 2550.0, 3600.0, 5100.0, 7200.0,
                                            10000.0, 14500.0, 20500.0, 28500.0, 41000.0, 57000.0, 81000.0, 115000.0,
                                            160000.0, 230000.0, 320000.0, 460000.0, 650000.0, 920000.0, 1300000.0,
                                            5000, 7000, 9900, 14000, 20000, 28000, 40000, 56000, 79000, 110000.0,
                                            160000.0, 225000.0, 320000.0, 450000.0, 630000.0, 900000.0, 1250000.0,
                                            1800000.0, 2550000.0, 3600000.0, 5100000.0, 7200000.0, 10000000.0,
                                            14500000.0, 20500000.0, 28500000.0, 41000000.0, 57000000.0, 81000000.0,
                                            115000000.0, 160000000.0, 230000000.0, 320000000.0]
            else:
                warnings.warn("Projection mode not recognized.. no available magnifications found.")
                available_magnifications = []

            print("Magnification [x Zoom]")
            for magnification in available_magnifications:
                print(magnification)

        else:
            raise Exception("Error: Microscope mode unknown.")
