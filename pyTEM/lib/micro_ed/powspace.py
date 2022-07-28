"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import numpy as np


def powspace(start, stop, power, num):
    """
    Like numpy.linspace - except returns numbers spaced on a power scale.

    Only works for positive start/stop values!

    :param start: float:
        The starting value of the sequence.
    :param stop: float:
        The end value of the sequence
    :param power: float:
        The power scale to use. Notice,
         - powers greater than 1 result in values spaced increasingly farther apart towards end the array near 'stop',
         - power = 1 results in evenly (linearly) spaced values,
         - and powers less than 1 result in values spaced increasingly closer together towards end the array near
            'start'.
    :param num: int:
        Number of samples to generate.

    :return: np.array:
        An array of values from start to stop (inclusive) with num values spaced on a power scale.
    """
    if start < 0 or start < 0:
        raise Exception("Error: powspace() requires positive start/stop values.")
    if power <= 0:
        raise Exception("Error: powspace() requires a positive (non-zero) power.")

    start = np.power(start, 1/float(power))
    stop = np.power(stop, 1/float(power))

    return np.power(np.linspace(start, stop, num=num), power)
