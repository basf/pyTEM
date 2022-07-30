"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import numpy as np


def rgb_to_greyscale(rgb_image: np.ndarray) -> np.ndarray:
    """
    Use the luminosity method (standard matplotlib formula) to perform the conversion from RGB (or RGBA or RGBX) to
     unsigned 8-bit greyscale.

    :param rgb_image: 3-dimensional array:
        The RGB image, as a 3-dimensional array.
    :return: 2-dimensional array:
        The provided array, but as a greyscale image.
    """
    if rgb_image.ndim != 3:
        raise Exception("Error: rgb_to_greyscale() input should be 3-dimensional but it is "
                        + str(rgb_image.ndim) + ".")
    if np.shape(rgb_image)[2] not in {3, 4}:
        # If 4 channels it is RGBA or RGBX in which case the 4th channel is ignored in the conversion.
        raise Exception("Error: rgb_to_greyscale() input should contain 3 or 4 channels in the last dimension, but "
                        "there are " + str(np.shape(rgb_image)[2]) + ".")

    r, g, b = rgb_image[:, :, 0], rgb_image[:, :, 1], rgb_image[:, :, 2]
    return 0.2989 * r + 0.5870 * g + 0.1140 * b
