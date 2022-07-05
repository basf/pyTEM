"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math

import numpy as np

from typing import Union
from numpy.typing import ArrayLike
from scipy.interpolate import interp1d

from pyTEM.lib.ued.find_bound_indicies import find_bound_indices


def build_full_shift_array(alphas: ArrayLike, samples: ArrayLike, shifts_at_samples: ArrayLike, verbose: bool = False,
                           interpolation_scope: str = "local", kind: Union[str, int] = "linear") -> np.ndarray:
    """
    We need compensatory image shifts at all values of alphas, but right now we only have shifts at for a sample of
     values. Using linear interpolation, build up the full shifts array.

    Interpolation is performed using scipy.interpolate.interp1d(). Refer to these docs for more info regarding the
     different kinds of interpolation that are supported.

    :param alphas: array of floats:
        Array of angles (in degrees) at which we need image shifts.
    :param samples: array of floats:
        Array of angles (in degrees) at which we have taken sample images and have image shifts.
        (usually computed directly from calibration images by obtain_shifts()).
    :param shifts_at_samples: array of float tuples:
        Array of tuples of the form (x, y) where x and y are the x-axis and y-axis image shifts (respectively) at the
         corresponding angle in samples.

    :param kind: str or int (optional; default is 'linear'):
        Specifies the kind of interpolation as a string or as an integer specifying the order of the spline
         interpolator to use.
    :param interpolation_scope: str (optional; default is 'local'):
        Interpolation scope, one of:
            - 'linear': Interpolate using only the adjacent (local) values from the sample array that bracket alpha.
                Because we only use two values, interpolation will always end up linear, regardless of kind.
            - 'global': Interpolate using all the values in the sample array.
    :param verbose: bool (optional; default is False):
        Print out extra information. Useful for debugging.

    :return: array:
        Array of tuples of the form (x, y) where x and y are the x-axis and y-axis image shifts (respectively) at the
         corresponding angle in alphas. The returned array of shifts is the same length as the provided alpha array.
    """
    interpolation_scope = str(interpolation_scope).lower()
    shifts = np.full(shape=len(alphas), dtype=(float, 2), fill_value=np.nan)  # Preallocate

    # Build global interpolators for both the x-axis and y-axis image shifts
    global_x_shift_interpolator = None  # Warning suppression
    global_y_shift_interpolator = None
    if interpolation_scope == "global":
        global_x_shift_interpolator = interp1d(x=samples, y=shifts_at_samples[:, 0], kind=kind)
        global_y_shift_interpolator = interp1d(x=samples, y=shifts_at_samples[:, 1], kind=kind)

    for alpha_shift_idx, alpha in enumerate(alphas):
        if alpha in samples:
            # Then we already know what the shift needs to be, just find it and insert it into the array.
            sample_idx = np.where(samples == alpha)
            shifts[alpha_shift_idx] = shifts_at_samples[sample_idx]

            if verbose:
                print(str(alpha) + " is in the samples array, inserting directly inserting the corresponding shifts "
                      "into the array at " + str(alpha_shift_idx))

        else:
            if verbose:
                print(str(alpha) + " is not in the samples array, performing a " + interpolation_scope
                      + " interpolation of kind: " + str(kind))

            if interpolation_scope == "global":
                # Use the global interpolators built above
                shifts[alpha_shift_idx] = (global_x_shift_interpolator(alpha), global_y_shift_interpolator(alpha))

            elif interpolation_scope == "local":

                # Build and use interpolators using only the local (adjacent) values in sample.
                lower_bound_idx, upper_bound_idx = find_bound_indices(array=samples, value=alpha)

                local_x_shift_interpolator = interp1d(x=samples[lower_bound_idx:upper_bound_idx + 1],
                                                      y=shifts_at_samples[lower_bound_idx:upper_bound_idx + 1, 0],
                                                      kind=kind)
                local_y_shift_interpolator = interp1d(x=samples[lower_bound_idx:upper_bound_idx + 1],
                                                      y=shifts_at_samples[lower_bound_idx:upper_bound_idx + 1, 1],
                                                      kind=kind)
                shifts[alpha_shift_idx] = (local_x_shift_interpolator(alpha), local_y_shift_interpolator(alpha))

            else:
                raise Exception("Error: interpolation_scope not recognized.")

    return shifts


if __name__ == "__main__":

    # TODO: Check for tilt ranges from pos -> neg

    start_alpha = 23
    stop_alpha = -35
    step_alpha = 1

    num_alpha = abs(int((stop_alpha - start_alpha) / step_alpha + 1))
    alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)
    # alphas_ = alpha_arr[0:-1] + step_alpha / 2
    alphas_ = alpha_arr

    print("\n Alphas:")
    print(alphas_)

    # Build pretend samples information (the x data)
    correction_shift_interval = 5  # deg
    total_tilt_range = abs(stop_alpha - start_alpha)
    num_images_required = math.ceil(total_tilt_range / correction_shift_interval) + 1
    samples_, step = np.linspace(start=start_alpha, stop=stop_alpha, num=num_images_required,
                                 endpoint=True, retstep=True)

    print("\nSamples:")
    print(samples_)

    # Build pretend shifts at samples information (the y data)
    x_shifts = np.linspace(start=-50, stop=40, num=num_images_required, endpoint=True)
    y_shifts = np.linspace(start=35, stop=-37, num=num_images_required, endpoint=True)
    shifts_at_samples_ = np.full(shape=num_images_required, dtype=(float, 2), fill_value=0.0)  # All zero.
    for i in range(len(samples_)):
        shifts_at_samples_[i] = (x_shifts[i], y_shifts[i])

    print("\nShifts at samples:")
    print(shifts_at_samples_)

    full_shift_array = build_full_shift_array(alphas=alphas_, samples=samples_, shifts_at_samples=shifts_at_samples_,
                                              kind='linear', interpolation_scope='global', verbose=True)
    print("Using global interpolation:")
    print(full_shift_array)

    full_shift_array = build_full_shift_array(alphas=alphas_, samples=samples_, shifts_at_samples=shifts_at_samples_,
                                              kind='linear', interpolation_scope='local', verbose=True)
    print("Using local interpolation:")
    print(full_shift_array)
