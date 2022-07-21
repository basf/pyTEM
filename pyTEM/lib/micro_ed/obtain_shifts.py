"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import warnings

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.signal import argrelextrema

from pyTEM.Interface import Interface

try:
    import matplotlib  # import matplotlib for the GUI backend HyperSpy needs
    matplotlib.rcParams["backend"] = "Agg"
    import hyperspy.api as hs
except Exception as ImportException:
    raise ImportException


def obtain_shifts(microscope: Interface,
                  alphas: NDArray[float],
                  camera_name: str,
                  sampling: str,
                  exposure_time: float = 0.25,
                  verbose: bool = False,
                  batch_wise: bool = False
                  ) -> np.array:
    """
    Automatically obtain the image shifts required to compensate for lateral specimen movement introduced by tilting.
    The returned shifts can then be used to keep the currently centered section of the specimen centered during a
     tilt acquisition series.

    Calibration images are taken while stationary at the tilt values listed in alphas. We don't take these images
     while tilting because, depending on the ratio of tilt range to exposure time, this may result in very blurry
     images.

    This function does not compensate for things like backlash and gear hysteresis. # TODO: Compensate for them

    Image shifts are estimated using Hyperspy's estimate_shift2D() function. This function uses a phase correlation
     algorithm based on the following paper:
        Schaffer, Bernhard, Werner Grogger, and Gerald Kothleitner. “Automated Spatial Drift Correction for EFTEM
        Image Series.” Ultramicroscopy 102, no. 1 (December 2004): 27–36.

    :param microscope: pyTEM.Interface:
        A pyTEM interface to the microscope.
    :param alphas: np.array:
        An array of tilt angles at which to compute shifts.
    :param camera_name: str:
        The name of the camera to be used in the image shift calculation - probably want to use the same camera you are
         using for the tilt series itself.
    :param sampling: str:
        One of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)

    :param exposure_time: float: (optional; default is 0.25)
        The exposure time, in seconds, to use for the shift calibration images.
        This should be as small as possible to limit the dose the sample receives.
    :param batch_wise: bool (optional; default is False):
        Compute image shifts in batches, readjusting the image shift after each batch. Limiting the number of images
         per batch can help make sure the image doesn't change too much, and also helps limit our RAM usage. One of:
            - True: Compute image shifts batch-wise.
            - False: Compute all image shifts in one go.
        Computing image shifts batch-wise requires a change in tilt direction. This might introduce additional error.
     :param verbose: bool (optional; default is False):
        Print out extra information. Useful for debugging.

    :return: np.array: shifts:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt with the reference image (reference image taken with an alpha tilt
         of 0 degrees).
        Note: len(shifts) = len(alphas)
    """
    # Make sure the beam is blank, column valve is open, and the screen is removed.
    user_had_beam_blanked = microscope.beam_is_blank()
    if not user_had_beam_blanked:
        microscope.blank_beam()
    user_column_valve_position = microscope.get_column_valve_position()
    if user_column_valve_position == "closed":
        microscope.open_column_valve()
    user_screen_position = microscope.get_screen_position()
    if user_screen_position == "inserted":
        microscope.retract_screen()

    if verbose:
        print("\nAcquisition parameters for the shift determination images:"
              "\nSampling=" + str(sampling) + ", Exposure time=" + str(exposure_time))

    # Start with the no tilt and no image shift
    if verbose:
        print("\nZeroing the stage position and image shift in preparation for negative tilt shift obtainment...")
    microscope.set_stage_position(alpha=0, speed=0.25)  # Zero the stage tilt
    microscope.set_image_shift(x=0, y=0)  # Zero the image shift

    if batch_wise:
        # Compute shifts in batches. Limiting the number of images per batch can help make sure the image doesn't
        #  change too much, and also helps limit our RAM usage.
        max_images_per_batch = 5

        if verbose:
            print("Computing correctional shifts batch-wise in batches of " + str(max_images_per_batch) + ".")

        negative_alphas = alphas[alphas < 0]
        positive_alphas = alphas[alphas >= 0]

        if alphas[0] > 0:
            # Then we are tilting pos -> neg, flip the positive array.
            positive_alphas = np.flip(positive_alphas)  # Now it will start with the smallest values
        else:
            # We are tilting neg -> pos, flip the negative array.
            negative_alphas = np.flip(negative_alphas)  # Now it will start with the least negative values

        # Compute the required shifts for the negative tilt angles
        if verbose:
            print("\nComputing shifts at negative tilt angles using the following alphas: " + str(negative_alphas))
        negative_shifts = _complete_one_sign(microscope=microscope, sampling=sampling, exposure_time=exposure_time,
                                             camera_name=camera_name, this_signs_alphas=negative_alphas,
                                             max_images_per_batch=max_images_per_batch, verbose=verbose)

        # Reset the image shift and tilt back to 0 deg
        if verbose:
            print("\nRe-zeroing the stage position and image shift in preparation for positive tilt shift "
                  "obtainment...")
        microscope.set_stage_position(alpha=0, speed=0.25)  # Zero the stage tilt
        microscope.set_image_shift(x=0, y=0)  # Zero the image shift

        # Compute the required shifts for the positive tilt angles
        if verbose:
            print("\nComputing shifts at positive tilt angles using the following alphas: " + str(positive_alphas))
        positive_shifts = _complete_one_sign(microscope=microscope, sampling=sampling, exposure_time=exposure_time,
                                             camera_name=camera_name, this_signs_alphas=positive_alphas,
                                             max_images_per_batch=max_images_per_batch, verbose=verbose)

        # One array of shifts will need to be flipped back (because it will have been built from a flipped array)
        if alphas[0] > 0:
            # Then we are tilting pos -> neg, flip the positive array and merge the two shift arrays
            positive_shifts = np.flip(positive_shifts, axis=0)
            shifts = np.concatenate((positive_shifts, negative_shifts))
        else:
            # We are tilting neg -> pos, flip the negative array and merge the two shift arrays
            negative_shifts = np.flip(negative_shifts, axis=0)
            shifts = np.concatenate((negative_shifts, positive_shifts))

    else:
        # Just go ahead and take all the calibration images at once.

        # We need to take our first image at zero degrees, this is where the user has centered the particle.
        alphas = np.insert(arr=alphas, obj=0, values=0)
        if verbose:
            print("Obtaining shifts for the following alphas: " + str(alphas))

        # Perform a series acquisition
        acq_series = microscope.acquisition_series(num=len(alphas), camera_name=camera_name,
                                                   exposure_time=exposure_time, sampling=sampling,
                                                   blanker_optimization=True, tilt_bounds=None,
                                                   shifts=None, alphas=alphas, verbose=verbose)

        # Compute image shifts from the results of the series acquisition.
        image_stack_arr = acq_series.get_image_stack()
        image_stack = hs.signals.Signal2D(image_stack_arr)
        batch_shifts = image_stack.estimate_shift2D().astype('float64')  # in pixels

        # The first alpha/shift corresponds to the 0 deg reference image, throw it away.
        shifts = np.delete(batch_shifts, 0, axis=0)
        alphas = np.delete(alphas, 0)

        # Obtain the pixel size from the first acquisition
        metadata = acq_series[0].get_metadata()
        pixel_size_x = metadata['PixelSize'][0] * 1e6  # m -> um
        pixel_size_y = metadata['PixelSize'][1] * 1e6
        if verbose:
            print("\nGrabbing pixel size from reference image metadata..")
            print("pixel-size x: " + str(pixel_size_x) + " um")
            print("pixel-size y: " + str(pixel_size_y) + " um")

        # Multiply by the pixel size to obtain shifts in micrometers.
        # Notice that the required image shifts are the negative of the pixel shifts found with hyperspy (converting
        #  to a Hyperspy signal already took care of the y-inversion for us). Also, notice that somewhere x and y
        #  directions got switched so just switch them back.
        y_shifts_in_pixels = shifts[:, 0].copy()
        shifts[:, 0] = -1 * pixel_size_x * shifts[:, 1]
        shifts[:, 1] = pixel_size_y * y_shifts_in_pixels

    # Housekeeping: Leave the blanker, column value, and screen the way they were when we started.
    if user_column_valve_position == "closed":
        microscope.close_column_valve()
    if user_screen_position == "inserted":
        microscope.insert_screen()
    if not user_had_beam_blanked:
        microscope.unblank_beam()

    # Re-zero the image shift and stage tilt
    microscope.set_image_shift(x=0, y=0)
    microscope.set_stage_position_alpha(alpha=0, speed=0.25)

    # To get an idea of whether we were successful, analyse the number of local optima in the resultant shifts array.
    # Ideally, these image shifts should be monotonic. However, sometimes they are choppy. This choppiness indicates
    #  a failure in the shift estimations.
    local_minima_x = argrelextrema(shifts[:, 0], np.less)[0]
    local_maxima_x = argrelextrema(shifts[:, 0], np.greater)[0]
    optima_x = np.concatenate((local_minima_x, local_maxima_x))
    local_minima_y = argrelextrema(shifts[:, 1], np.less)[0]
    local_maxima_y = argrelextrema(shifts[:, 1], np.greater)[0]
    optima_y = np.concatenate((local_minima_y, local_maxima_y))

    if verbose:
        print("\nAnalysing the number of optima to assess the quality of the results...")
        print("Number of optima in x-shifts array: " + str(len(optima_x)))
        print("Number of optima in y-shifts array: " + str(len(optima_y)))

        # Put the results in a dataframe for easy viewing
        df = pd.DataFrame({'alpha': alphas, 'x-shift': shifts[:, 0], 'y-shift': shifts[:, 1]})
        print("\nObtained shifts:")
        print(df.to_string())  # .to_string() is required to see the whole dataframe

    if len(optima_x) > 2 or len(optima_y) > 2:
        # Then our automated correctional shift determination was probably unsuccessful.

        if batch_wise:
            # Then there isn't really much else we can do... just return None.
            warnings.warn("Based on the number of local optima in the obtained shifts, it is unlikely that the "
                          "batch-wise automated correctional shift determination was successful. Returning None...")
            shifts = None

        else:
            # Try recomputing batch-wise.
            warnings.warn("Based on the number of local optima in the obtained shifts, it is unlikely that the "
                          "automated correctional shift determination was successful. Re-trying batch-wise...")
            # Try re-computing batch-wise, this might work better if there is significant particle drift
            shifts = obtain_shifts(microscope=microscope, alphas=alphas, camera_name=camera_name, sampling=sampling,
                                   exposure_time=exposure_time, verbose=verbose, batch_wise=True)

    return shifts


def _complete_one_sign(microscope: Interface,
                       camera_name: str,
                       exposure_time: float,
                       sampling: str,
                       this_signs_alphas: NDArray[float],
                       max_images_per_batch: int = 10,
                       verbose: bool = False
                       ) -> np.array:
    """
    A helper function needed when computing shifts batch-wise. Because we want the user to center the specimen at
     0 degrees (to reduce the overall shift), we need to separately compute:
     - the shifts at positive tilt angles
     - the shifts at negative tilt angles

    This function computes the shifts for just one sign, and by calling it twice we are able to compute all the shifts.

    :param microscope: pyTEM.Interface:
        A pyTEM interface to the microscope.
    :param camera_name: str:
        The name of the camera to be used for shift calculation - probably the same camera you are using for the tilt
         series itself.
    :param exposure_time: float:
        The exposure time, in seconds, to use for the shift determination images.
    :param sampling: str:
            One of:
                - '4k' for 4k images (4096 x 4096; sampling=1)
                - '2k' for 2k images (2048 x 2048; sampling=2)
                - '1k' for 1k images (1024 x 1024; sampling=3)
                - '0.5k' for 05.k images (512 x 512; sampling=8)
    :param this_signs_alphas: np.array:
        An array with either the positive alphas or the negative alphas.
    :param max_images_per_batch: int (optional; default is 10):
        To make sure that the images don't deviate too far from the reference image, we are computing image shifts in
         batches. This parameter controls the maximum number of images per batch.
    :param verbose: bool (optional; default is False):
        Useful for debugging.

    :return: np.array of float tuples:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt.
    """
    # Preallocate.
    this_signs_image_shifts = np.full(shape=len(this_signs_alphas), dtype=(float, 2), fill_value=np.nan)
    current_index = 0  # We will start filling in this_signs_image_shifts at the beginning.

    number_of_batches = math.ceil(len(this_signs_alphas) / max_images_per_batch)
    alpha_batches = np.array_split(this_signs_alphas, number_of_batches)
    if verbose:
        print("\nShifts are being computed in batches, here are the alpha_batches:")
        print(alpha_batches)
        print("Number of batches: " + str(number_of_batches))

    # Loop through the batches, computing the image shifts one batch at a time
    for i, batch in enumerate(alpha_batches):
        if verbose:
            print("\nComputing shifts for batch #" + str(i) + ": " + str(batch))

        # Reset the reference image-shift, this is where we are at the start of the batch
        reference_image_shift = microscope.get_image_shift()

        # We need to take our first image at the current location (either 0 or the last tilt in the previous batch)
        alphas = np.insert(arr=batch, obj=0, values=microscope.get_stage_position_alpha())

        # Perform a series acquisition
        acq_series = microscope.acquisition_series(num=len(batch) + 1, camera_name=camera_name,
                                                   exposure_time=exposure_time, sampling=sampling,
                                                   blanker_optimization=True, tilt_bounds=None,
                                                   shifts=None, alphas=alphas, verbose=verbose)
        image_stack_arr = acq_series.get_image_stack()

        # Obtain the pixel size from the first acquisition
        metadata = acq_series[0].get_metadata()
        pixel_size_x = metadata['PixelSize'][0] * 1e6  # m -> um
        pixel_size_y = metadata['PixelSize'][1] * 1e6
        if verbose:
            print("\nGrabbing pixel size from reference image metadata..")
            print("pixel-size x: " + str(pixel_size_x) + " um")
            print("pixel-size y: " + str(pixel_size_y) + " um")

        # Use hyperspy (cross-correlation) to compute shifts for this batch's stack
        image_stack = hs.signals.Signal2D(image_stack_arr)
        if verbose:
            print("\nHyperspy Image stack: " + str(image_stack))

        batch_shifts = image_stack.estimate_shift2D().astype('float64')  # in pixels
        # The first shift corresponds to the reference image, so we will throw it away.
        batch_shifts = np.delete(batch_shifts, 0, axis=0)
        if verbose:
            print("\nThis batches shifts (in pixels):")
            print(batch_shifts)

        # Log the rest of shifts in the array, make sure to multiply by the pixel size so the result is in microns.
        for j in range(np.shape(batch_shifts)[0]):
            # Image shifts are the negative of the pixel shifts found with hyperspy.
            this_signs_image_shifts[current_index] = (-pixel_size_x * (batch_shifts[j][1]) + reference_image_shift[0],
                                                      pixel_size_y * (batch_shifts[j][0]) + reference_image_shift[1])
            current_index = current_index + 1

        # Advance the image shift so the specimen is centered at the most extreme tilt of the batch
        if verbose:
            print("\nMoving the image shift to prepare for the next batch...")
        microscope.set_image_shift(x=this_signs_image_shifts[current_index - 1][0],
                                   y=this_signs_image_shifts[current_index - 1][1])

    return this_signs_image_shifts


if __name__ == "__main__":

    try:
        scope = Interface()
    except BaseException as e:
        print(e)
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    start_alpha = -15
    stop_alpha = 15
    step_alpha = 2

    exp_time = 0.25
    sampling_ = '1k'

    num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
    alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)
    middle_alphas = alpha_arr[0:-1] + step_alpha / 2

    print("\nWhole alpha array: " + str(alpha_arr))
    print("\nAlphas at which shifts will be computed: " + str(middle_alphas))

    print("\nObtaining shifts all in one go (not batch-wise)...")
    obtain_shifts(microscope=scope, camera_name='BM-Ceta', alphas=middle_alphas, sampling=sampling_,
                  exposure_time=exp_time, batch_wise=False, verbose=True)

    # print("\nObtaining shifts batch-wise...")
    # obtain_shifts(microscope=scope, camera_name='BM-Ceta', alphas=middle_alphas, sampling=sampling_,
    #               exposure_time=exp_time, batch_wise=True, verbose=True)
