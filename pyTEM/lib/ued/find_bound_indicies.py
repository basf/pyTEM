"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

from typing import Any, Tuple

import numpy as np
from numpy.typing import ArrayLike


def find_bound_indices(array: ArrayLike, value: Any) -> Tuple[float, float]:
    """
    Find the indices of the elements in array that bound the value.

    :param array: np.array:
        A sorted array of values (least -> greatest).
    :param value:
        A value in array.

    :return:
        lower_idx: float: The index of array that bounds value from the bottom.
        upper_idx: float: The index of array that bounds value from the top.
    """
    insertion_idx = np.searchsorted(array, value, side="right")
    return insertion_idx - 1, insertion_idx
