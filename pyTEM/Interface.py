"""
 Author:  Michael Luciuk
 Date:    Summer 2022

This is BASF's in-house TEM scripting interface. Bolted directly on top of a COM interface, this is just a Python
 wrapper for the scripting interface of Thermo Fisher Scientific and FEI microscopes.

This is not a complete interface in that it does not provide access to all the functionality of the underlying Thermo
 Fisher Scientific and FEI scripting interface. However, it provides access to all basic microscope functions as well
 as all those required by other pyTEM automation scripts.
"""

import math
import pathlib
import sys
import warnings

import numpy as np
import comtypes.client as cc

# Add the pyTEM package directory to path
package_directory = pathlib.Path().resolve()
sys.path.append(str(package_directory))

try:
    # Mixins
    from pyTEM.lib.interface.mixins.ModeMixin import ModeMixin
    from pyTEM.lib.interface.mixins.StageMixin import StageMixin
    from pyTEM.lib.interface.mixins.MagnificationMixin import MagnificationMixin
    from pyTEM.lib.interface.mixins.VacuumMixin import VacuumMixin
    from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerMixin
    from pyTEM.lib.interface.mixins.ImageShiftMixin import ImageShiftMixin
    from pyTEM.lib.interface.mixins.BeamShiftMixin import BeamShiftMixin
    from pyTEM.lib.interface.mixins.AcquisitionMixin import AcquisitionMixin

    # Other library imports
    from pyTEM.lib.interface.pascal_to_log import pascal_to_log
    from pyTEM.lib.interface.StagePosition import StagePosition

except Exception as ImportException:
    raise ImportException


class Interface(ModeMixin,           # Microscope mode controls, including those for projection and illuminations.
                StageMixin,          # Stage controls.
                MagnificationMixin,  # Magnification controls.
                VacuumMixin,         # Vacuum system controls and pressure readouts.
                BeamBlankerMixin,    # Blank/unblank the beam.
                ImageShiftMixin,     # Image shift controls.
                BeamShiftMixin,      # Beam Shift controls.
                AcquisitionMixin     # Microscope acquisition controls, including those for taking images.
                ):
    """
    An interface for the Thermo-Fisher TEM microscopes.

    This is basically just a "user-friendly" wrapper for the Thermo-Fisher 'Instrument' object that is used to
     actually interact with and control the microscope. Note that there is a COM interface (a middle man of sorts)
     facilitating communication between the "user-friendly" wrapper and the underlying Thermo-Fisher 'Instrument'
     object.

    Public Attributes:
        None.

    Protected Attributes:
        _tem: Thermo Fisher 'Instrument' object:
            This is used "under-the-hood" to actually interact with and control a subset the microscope's features
        _tem_advanced: Thermo Fisher 'AdvancedInstrument' object
            This is used "under-the-hood" to actually interact with and control a remainder of the microscope's
             features.
        _stage_position: An instance of the simplified, forward facing StagePosition class:
            The current stage position.
        _image_shift_matrix: 2D numpy.ndarray:
            Matrix used to translate between the stage-plane and the image-plane.
            This matrix is based on a manual calibration, it is not perfect, but it does a reasonable job.
        _beam_shift_matrix: 2D numpy.ndarray:
            Matrix used to translate between the stage-plane and the beam-plane.
            This matrix is based on the image shift matrix.

    Private Attributes:
        None.  Note: pyTEM attributes required by another mixin cannot be made private otherwise the mixins
                        will not be able to access them through the COM interface.
    """

    def __init__(self):
        try:
            self._tem = cc.CreateObject("TEMScripting.Instrument")
            self._tem_advanced = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")
        except OSError as e:
            print("Unable to connect to microscope.")
            raise e

        scope_position = self._tem.Stage.Position  # ThermoFisher StagePosition object

        self._stage_position = StagePosition(x=scope_position.X * 1e6,  # m -> um
                                             y=scope_position.Y * 1e6,  # m -> um
                                             z=scope_position.Z * 1e6,  # m -> um
                                             alpha=math.degrees(scope_position.A),  # rad -> deg
                                             beta=math.degrees(scope_position.B))  # rad -> deg

        self._image_shift_matrix = np.asarray([[1.010973981, 0.54071542],
                                               [-0.54071542, 1.010973981]])

        # TODO: Perform some experiment to validate this beam shift matrix
        self._beam_shift_matrix = np.asarray([[1.010973981, 0.54071542],
                                              [0.54071542, -1.010973981]])

    def normalize(self) -> None:
        """
        Normalizes all lenses.
        :return: None.
        """
        self._tem.NormalizeAll()

    def make_safe(self) -> None:
        """
        Return the microscope to a safe state.
        :return: None.
        """
        self.close_column_valve()
        self.blank_beam()
        self.insert_screen()

    def prepare_for_holder_removal(self) -> None:
        """
        Prepare the TEM for holder removal.
        :return: None.
        """
        self.close_column_valve()

        # Sometimes it takes a couple tries to fully reset the stage
        num_tries = 3
        for t in range(num_tries):
            if self.stage_is_home():
                break  # Then we are good
            else:
                self.reset_stage_position()  # Try to send it home

            if t == num_tries - 1:
                # Then the stage has still not gone back, and we are out of tries, panik
                raise Exception("Unable to reset the stage.")

        self.set_image_shift(x=0, y=0)
        self.set_beam_shift(x=0, y=0)

        # Set the magnification somewhere in the SA range
        if self.get_mode() == "TEM":
            self.set_tem_magnification(new_magnification_index=23)  # 8600.0 x Zoom
        elif self.get_mode() == "STEM":
            self.set_stem_magnification(new_magnification=8600.0)
        else:
            raise Exception("Error: Current microscope mode unknown.")

        warnings.warn("prepare_for_holder_removal() not fully implemented, please retract the camera "
                      "before removing the holder.")  # TODO: Retract camera

    def zero_shifts(self):
        """
        Zero the image and beam shifts.
        :return: None.
        """
        self.set_beam_shift(x=0, y=0)
        self.set_image_shift(x=0, y=0)


if __name__ == "__main__":
    scope = Interface()
