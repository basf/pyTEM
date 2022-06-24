"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import warnings
import numpy as np
import comtypes.client as cc

from numpy.typing import ArrayLike

# TODO: Still requires testing


class BeamShiftMixin:
    """
    Microscope beam shift controls.

    This mixin was developed in support of pyTEM.pyTEM, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem: type(cc.CreateObject("TEMScripting.Instrument"))
    except OSError:
        pass
    _beam_shift_matrix: type(np.empty(shape=(2, 2)))

    # Note: For precise shifting, an offset vector is required to account for hysteresis in the len's magnets. However,
    #  this is negligible for most applications.
    # _beam_shift_vector: type(np.empty(shape=(2, 1)))

    def get_projection_submode(self) -> str:
        """
        :return: str:
            The current projection sub-mode.
        """
        return self._tem.Projection.SubModeString

    def get_beam_shift_matrix(self) -> np.ndarray:
        """
        :return: numpy.ndarray
            The new 2x2 matrix used to translate between the stage-plane and the beam-plane
        """
        return self._beam_shift_matrix

    def _set_beam_shift_matrix(self, a: ArrayLike) -> None:
        """
        Update the beam shift matrix.
        :param a: numpy.ndarray:
            The new 2x2 used to translate between the stage-plane and the beam-plane.
        :return: None
        """
        self._stage_position = a

    def get_beam_shift(self) -> np.array:
        """
        :return: [x, y]: 2-element numpy.array:
            The x and y values of the beam shift, in micrometres.
        """
        if self._tem.Projection.SubModeString != "SA":
            warnings.warn("Beam shift functions only tested for magnifications in SA range (4300 x -> 630 kx Zoom), "
                          "but the current projection submode is " + self._tem.Projection.SubModeString +
                          ". Magnifications in this range may require a different transformation matrix.")

        beam_shift = self._tem.Illumination.Shift

        # Notice we need to use the beam shift matrix to translate from the beam plane back to the stage plane.
        # Beam shift along y is in the wrong direction (IDK why), for now we just invert the user input.
        temp = 1e6 * np.matmul(self.get_beam_shift_matrix(), np.asarray([beam_shift.X, beam_shift.Y]))
        return np.asarray([temp[0], - temp[1]])

    def set_beam_shift(self, x: float = None, y: float = None) -> None:
        """
        Move the beam shift to the provided x and y values.

        :param x: float:
            The new beam shift location, along the x-axis, in micrometres.
        :param y:
            The new beam shift location, along the y-axis, in micrometres.

        :return: None
        """
        if self._tem.Projection.SubModeString != "SA":
            warnings.warn("Beam shift functions only tested for magnifications in SA range (4300 x -> 630 kx Zoom), "
                          "but the current projection submode is " + self._tem.Projection.SubModeString +
                          ". Magnifications in this range may require a different transformation matrix.")

        a = self.get_beam_shift_matrix()

        u = self.get_beam_shift()  # Start from the current beam shift location

        if x is not None:
            u[0] = x / 1e6  # Update our x-value (convert um -> m)
        if y is not None:
            # Beam shift along y is in the wrong direction (IDK why), for now we just invert the user input.
            u[1] = -y / 1e6  # update our y-value (convert um -> m)

        # Translate back to the microscope plane and perform the shift
        u_prime = np.matmul(np.linalg.inv(a), u)
        new_beam_shift = self._tem.Illumination.Shift  # Just to get the required ThermoFisher Vector object
        new_beam_shift.X = u_prime[0]
        new_beam_shift.Y = u_prime[1]
        self._tem.Illumination.Shift = new_beam_shift
