"""
We need shifts at all values of alphas, but right now we only compute shifts at samples
"""

import math
from typing import Any, Tuple

import numpy as np
import pandas

# np.set_printoptions(threshold=1000)
from numpy.typing import ArrayLike
from scipy.interpolate import interp1d


def find_bound_indices(array: ArrayLike[Any], value: Any) -> Tuple[float, float]:
    """
    Find the indices of the elements in array that bound the value.

    :param array: np.array:
        An array of values
    :param value:
        A value in array.

    :return:
        lower_idx: float: The index of array that bounds value from the bottom.
        upper_idx: float: The index of array that bounds value from the top.
    """
    insertion_idx = np.searchsorted(array, value, side="right")
    return insertion_idx - 1, insertion_idx


def build_full_shift_array(alphas: ArrayLike, samples: ArrayLike, shifts_at_samples: ArrayLike):
    """
    We need compensatory image shifts at all values of alphas, but right now we only have shifts at for a sample of
     values. Using linear interpolation, build up the full shifts array.

    The returned array of shifts is the same length as the provided alpha array.

    :param alphas: array:
        Array of angles
    :param samples:
    :param shifts_at_samples:
    :return:
    """
    shifts = np.full(shape=len(alphas), dtype=(float, 2), fill_value=np.nan)  # Preallocate

    for alpha_shift_idx, alpha in enumerate(alphas):
        if alpha in samples:
            # Then we already know what the shift needs to be, just find it and insert it into the array.
            sample_idx = np.where(samples == alpha)
            shifts[alpha_shift_idx] = shifts_at_samples[sample_idx]

        else:
            # We don't have a shift, so we will need to linearly interpolate
            lower_samples_idx, upper_samples_idx = find_bounds_indices(samples, alpha)
            y_interp = interp1d(x=samples, y=shifts_at_samples)
            x = alpha
            print(y_interp(x))





if __name__ == "__main__":

    start_alpha = -30
    stop_alpha = 30
    step_alpha = 1

    num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
    alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)
    # alphas = alpha_arr[0:-1] + step_alpha / 2
    alphas = alpha_arr

    print("\n Alphas:")
    print(alphas)

    correction_shift_interval = 5  # deg

    total_tilt_range = abs(stop_alpha - start_alpha)
    num_images_required = math.ceil(total_tilt_range / correction_shift_interval) + 1
    samples, step = np.linspace(start=start_alpha, stop=stop_alpha, num=num_images_required, endpoint=True, retstep=True)

    # Build sample information and put it into a dataframe
    x_shifts = np.linspace(start=-50, stop=40, num=num_images_required, endpoint=True)
    y_shifts = np.linspace(start=35, stop=-37, num=num_images_required, endpoint=True)
    shifts = np.full(shape=num_images_required, dtype=(float, 2), fill_value=0.0)  # All zero.
    for i in range(len(samples)):
        shifts[i][0] = x_shifts[i]
        shifts[i][1] = y_shifts[i]

    df = pandas.DataFrame(data={'alpha': samples,
                                'x_shift': x_shifts,
                                'y_shift': y_shifts,
                                'interpolated': len(samples) * [False]})
    print("\n Samples (as obtained from the user with shift_correction_info()")
    print(df)

    for i, alpha in enumerate(alphas):
        idx_list = df[df["alpha"] == alpha].index.values
        if len(idx_list) <= 0 or len(idx_list) > 1:
            print(str(alpha) + " was not found in the dataframe...")

            # This value is not in the dataframe, we have to add it!
            lower_bound, upper_bound = find_bound_indices(array=samples, value=alpha)
            print("Lower bound: idx=" + str(lower_bound) + ", value=" + str(samples[lower_bound]))
            print("Upper bound: idx=" + str(upper_bound) + ", value=" + str(samples[upper_bound]))


        elif len(idx_list) == 1:
            print(str(alpha) + " is already in the dataframe at index " + str(idx_list[0]) + " ...")

        else:
            raise Exception("Index list has length of " + str(len(idx_list)))

        # if alpha in df['alpha'].values:
        #     print(str(alpha) + " is already in the dataframe...")
        #
        # else:

    print("\n")

