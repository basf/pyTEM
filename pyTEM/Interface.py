"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import pathlib
import sys

import numpy as np
import comtypes.client as cc

package_directory = pathlib.Path().resolve().parent.resolve()
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

except Exception as e:
    raise e


class Interface(ModeMixin,  # Microscope mode controls, including those for projection and illuminations
                StageMixin,  # Stage controls
                MagnificationMixin,  # Magnification controls
                VacuumMixin,  # Vacuum system controls and pressure readouts
                BeamBlankerMixin,  # Blank/unblank the beam
                ImageShiftMixin,  # Image shift controls
                BeamShiftMixin,  # Beam Shift controls
                AcquisitionMixin  # Microscope acquisition controls, including those for taking images.
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
        self._tem = cc.CreateObject("TEMScripting.Instrument")

        self._tem_advanced = cc.CreateObject("TEMAdvancedScripting.AdvancedInstrument")

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

    def normalize(self):
        """
        Normalizes all lenses.
        :return: None.
        """
        self._tem.NormalizeAll()

    def make_safe(self):
        """
        Return the microscope to a safe state.
        :return: None
        """
        self.close_column_valve()
        self.blank_beam()
        self.insert_screen()

    """
    When multiple of the same methods exist across mixins, override to ensure we get the one we want.
    """

    def get_mode(self):
        return ModeMixin.get_mode(self)

    def get_projection_mode(self):
        return ModeMixin.get_projection_mode(self)

    def get_projection_submode(self):
        return ModeMixin.get_projection_submode(self)
