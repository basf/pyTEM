"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import warnings
import numpy as np
import comtypes.client as cc

from numpy.typing import ArrayLike

from pyTEM.lib.interface.mixins.ModeMixin import ModeMixin


class ImageShiftMixin(ModeMixin):
    """
    Microscope image shift controls.

    This mixin was developed in support of pyTEM.Interface, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem: type(cc.CreateObject("TEMScripting.Instrument"))
    except OSError:
        pass
    _image_shift_matrix: type(np.empty(shape=(2, 2)))

    # Note: For precise shifting, an offset vector is required to account for hysteresis in the len's magnets. However,
    #  this is negligible for most applications.
    # _image_shift_vector: type(np.empty(shape=(2, 1)))

    def get_image_shift_matrix(self) -> np.ndarray:
        """
        :return: numpy.ndarray:
            The 2x2 matrix used to translate between the stage-plane and the image-plane.
        """
        return self._image_shift_matrix

    def _set_image_shift_matrix(self, a: ArrayLike) -> None:
        """
        Update the image shift matrix.
        :param a: numpy.ndarray:
            The new 2x2 matrix used to translate between the stage-plane and the image-plane.
        :return: None.
        """
        self._stage_position = a

    def get_image_shift(self) -> np.array:
        """
        :return: [x, y]: 2-element numpy.array:
            The x and y values of the image shift, in micrometres.
        """
        if self.get_projection_submode() != "SA":
            warnings.warn("Image shift functions only tested for magnifications in SA range (4300 x -> 630 kx Zoom), "
                          "but the current projection submode is " + self._tem.Projection.SubModeString +
                          ". Magnifications in this range may require a different transformation matrix.")

        image_shift = self._tem.Projection.ImageShift

        # Notice we need to use the image shift matrix to translate from the image plane back to the stage plane.
        # Image shift along y is in the wrong direction (IDK why), for now we just invert the user input.
        temp = 1e6 * np.matmul(self.get_image_shift_matrix(), np.asarray([image_shift.X, image_shift.Y]))
        return np.asarray([temp[0], - temp[1]])

    def set_image_shift(self, x: float = None, y: float = None) -> None:
        """
        Move the image shift to the provided x and y values.

        :param x: float:
            The new image shift location, along the x-axis, in micrometres.
        :param y:
            The new image shift location, along the y-axis, in micrometres.

        :return: None.
        """
        if self.get_projection_submode() != "SA":
            warnings.warn("Image shift functions only tested for magnifications in SA range (4300 x -> 630 kx Zoom), "
                          "but the current projection submode is " + self._tem.Projection.SubModeString +
                          ". Magnifications in this range may require a different transformation matrix.")

        a = self.get_image_shift_matrix()

        u = self.get_image_shift()  # Start from the current image shift location

        if x is not None:
            u[0] = x / 1e6  # Update our x-value (convert um -> m)
        if y is not None:
            # Image shift along y is in the wrong direction (IDK why), for now we just invert the user input.
            u[1] = -y / 1e6  # update our y-value (convert um -> m)

        # Translate back to the microscope plane and perform the shift
        u_prime = np.matmul(np.linalg.inv(a), u)
        new_image_shift = self._tem.Projection.ImageShift  # Just to get the required ThermoFisher Vector object
        new_image_shift.X = u_prime[0]
        new_image_shift.Y = u_prime[1]
        self._tem.Projection.ImageShift = new_image_shift
