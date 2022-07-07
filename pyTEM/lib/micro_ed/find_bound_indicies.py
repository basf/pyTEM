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
        A sorted array of values. Can be sorted either least -> greatest (results when titling neg -> pos) or
         greatest -> least (results when tilting pos -> neg).
    :param value:
        A value in array.

    :return:
        lower_idx: float: The index of the element of array that bounds value on one side.
        upper_idx: float: The index of the element of array that bounds value on the other side.
    """
    if array.ndim != 1:
        raise Exception("Error: find_bound_indices() only works for 1-dimensional arrays.")

    is_sorted = np.all(array[:-1] <= array[1:])
    is_reverse_sorted = np.all(array[:-1] >= array[1:])

    if is_sorted:
        # Find the index at which insertion would persevere the ordering, we need this index and the one before
        insertion_idx = np.searchsorted(array, value, side="right")
        return insertion_idx - 1, insertion_idx

    elif is_reverse_sorted:
        # Find the index at which insertion would persevere the ordering, we need this index and the one before
        # Notice we need to search the reverse array and subtract the result from the length of the array
        insertion_idx = len(array) - np.searchsorted(np.flip(array), value, side="right")
        return insertion_idx - 1, insertion_idx

    else:
        raise Exception("Error: array is not sorted.")
