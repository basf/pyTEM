"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import warnings

import numpy as np
import pandas as pd

import hyperspy.api as hs
from scipy.signal import find_peaks

# TODO: Still requires testing


def obtain_shifts(microscope, alphas, camera_name, verbose=False):
    """
    Automatically obtain the image shifts required to keep the currently centered section of the specimen centered at
     all alpha tilt angles.

    Image shifts are estimated using Hyperspy's estimate_shift2D() function. This function uses a phase correlation
     algorithm based on the following paper:
        Schaffer, Bernhard, Werner Grogger, and Gerald Kothleitner. “Automated Spatial Drift Correction for EFTEM
        Image Series.” Ultramicroscopy 102, no. 1 (December 2004): 27–36.

    :param microscope: TEMInterface:
        A TEMInterface interface to the microscope.
    :param alphas: np.array:
        An array of tilt angles at which to compute shifts.
    :param camera_name: str:
        The name of the camera to be used in the image shift calculation - probably want to use the same camera you are
         using for the tilt series itself.
     :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: np.array: shifts:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt with the reference image (reference image taken with an alpha tilt
         of 0 degrees).
        Note: len(shifts) = len(alphas)
    """
    # Start with the no tilt and no image shift
    if verbose:
        print("\nZeroing the stage position and image shift in preparation for negative tilt shift obtainment...")
    microscope.set_stage_position(alpha=0, speed=0.5)  # Zero the stage tilt
    microscope.set_image_shift(x=0, y=0)  # Zero the image shift

    # Compute shifts in batches
    # Limiting the number of images per batch can help make sure the image doesn't change too much, and also helps
    #  ensure that we don't use too much RAM
    max_images_per_batch = 10

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
    negative_shifts = _complete_one_sign(microscope=microscope, this_signs_alphas=negative_alphas, verbose=verbose,
                                         max_images_per_batch=max_images_per_batch, camera_name=camera_name)

    # Reset the image shift and tilt to 0 deg
    if verbose:
        print("\nRe-zeroing the stage position and image shift in preparation for positive tilt shift obtainment...")
    microscope.set_stage_position(alpha=0, speed=0.5)  # Zero the stage tilt
    microscope.set_image_shift(x=0, y=0)  # Zero the image shift

    # Compute the required shifts for the positive tilt angles
    if verbose:
        print("\nComputing shifts at positive tilt angles using the following alphas: " + str(positive_alphas))
    positive_shifts = _complete_one_sign(microscope=microscope, this_signs_alphas=positive_alphas, verbose=verbose,
                                         max_images_per_batch=max_images_per_batch, camera_name=camera_name)

    # One array of shifts will need to be flipped back (because it will have been built from a flipped array)
    if alphas[0] > 0:
        # Then we are tilting pos -> neg, flip the positive array and merge the two shift arrays
        positive_shifts = np.flip(positive_shifts, axis=0)
        shifts = np.concatenate((positive_shifts, negative_shifts))
    else:
        # We are tilting neg -> pos, flip the negative array and merge the two shift arrays
        negative_shifts = np.flip(negative_shifts, axis=0)
        shifts = np.concatenate((negative_shifts, positive_shifts))

    x_peaks, _ = find_peaks(shifts[:, 0])
    y_peaks, _ = find_peaks(shifts[:, 1])
    if verbose:
        print("\nAnalysing peaks to assess the quality of the results...")
        print("Number of x-peaks: " + str(x_peaks))
        print("Number of y-peaks: " + str(y_peaks))
    if x_peaks > 4 or y_peaks > 4:
        # Then we were probably unsuccessful, warn the user
        warnings.warn("Based on the number of peaks, it is unlikely that the automated shift determination was "
                      "successful. Please ensure the specimen is at the eucentric height and try again (you may need "
                      "to reduce the number of images per batch).")
        raise Exception("obtain_shifts(): Automated shift alignment failed, unsafe to proceed.")

    if verbose:
        # Put the obtained shifts in a dataframe for easy viewing
        df = pd.DataFrame({'alpha': alphas, 'x-shift': shifts[:, 0], 'y-shift': shifts[:, 1]})
        print("\nObtained shifts:")
        print(df.to_string())  # Required to see the whole dataframe

    return shifts


def _complete_one_sign(microscope, camera_name, this_signs_alphas, max_images_per_batch=10, verbose=False):
    """
    Because we want the user to center the specimen at 0 degrees (to reduce the overall shift), we need to separately
     compute:
     - the shifts at positive tilt angles
     - the shifts at negative tilt angles

    This function computes the shifts for just one sign, and by calling it twice we are able to compute all the shifts.

    :param microscope: TEMInterface:
        A TEMInterface interface to the microscope.
    :param camera_name: str:
        The name of the camera to be used for shift calculation - probably the same camera you are using for the tilt
         series itself.
    :param this_signs_alphas: np.array:
        An array with either the positive alphas or the negative alphas.
    :param max_images_per_batch: int (optional; default is 10):
        # TODO: Adjust based on number of peaks in results.
        To make sure that the images don't deviate too far from the reference image, image shifts are computed in
         batches. This parameter controls the maximum number of images per batch.
    :param verbose: bool:
        Useful for debugging.

    :return: np.array of float tuples:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt.
    """
    # Define acquisition parameters, these should be sufficient for alignment photos
    sampling = '1k'
    exposure_time = 1
    if verbose:
        print("\nAcquisition parameters: Sampling=" + str(sampling) + ", Exposure time=" + str(exposure_time))

    # Preallocate
    this_signs_image_shifts = np.full(shape=len(this_signs_alphas), dtype=(float, 2), fill_value=np.nan)
    current_index = 0  # We will start filling in this_signs_image_shifts at the beginning

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

        # Take a reference image
        reference_acq = microscope.acquisition(camera_name=camera_name, sampling=sampling, exposure_time=exposure_time)
        reference_image = reference_acq.get_image()

        # Preallocate
        number_images = len(batch) + 1  # Plus one to make room for the reference image
        image_shape = np.shape(reference_image)
        image_stack_arr = np.full(shape=(number_images, image_shape[0], image_shape[1]), fill_value=np.nan)
        image_stack_arr[0] = reference_image  # Put the reference image at the start of the array (top of the stack)

        # Obtain the pixel size from the reference acquisition
        reference_metadata = reference_acq.get_metadata()
        pixel_size_x = reference_metadata['PixelSize'][0] * 1e6  # m -> um
        pixel_size_y = reference_metadata['PixelSize'][1] * 1e6
        if verbose:
            print("\nGrabbing pixel size from reference image metadata..")
            print("pixel-size x: " + str(pixel_size_x) + " um")
            print("pixel-size y: " + str(pixel_size_y) + " um")

        # Loop through each tilt angle in the batch.
        for j, alpha in enumerate(batch):
            if verbose:
                print("Taking image at alpha=" + str(round(alpha, 2)))
            microscope.set_stage_position(alpha=alpha)  # Tilt the stage to the required alpha
            acq = microscope.acquisition(camera_name=camera_name, sampling=sampling, exposure_time=exposure_time)
            image_stack_arr[j + 1] = acq.get_image()

        # Use hyperspy (cross-correlation) to compute shifts for this batch's stack
        image_stack = hs.signals.Signal2D(image_stack_arr)
        if verbose:
            print("\nHyperspy Image stack: " + str(image_stack))

        batch_shifts = image_stack.estimate_shift2D()
        # The first shift corresponds to the reference image, so we will throw it away.
        batch_shifts = np.delete(batch_shifts, 0, axis=0)
        if verbose:
            print("\nThis batches shifts (in pixels):")
            print(batch_shifts)

        # Log the rest of shifts in the array, make sure to multiply by the pixel size so the result is in microns.
        for j in range(np.shape(batch_shifts)[0]):
            # Image shifts are the negative of the pixel shifts found with hyperspy.
            this_signs_image_shifts[current_index] = (-pixel_size_x * (batch_shifts[j][0]) + reference_image_shift[0],
                                                      -pixel_size_y * (batch_shifts[j][1]) + reference_image_shift[1])
            current_index = current_index + 1

        # Advance the image shift so the specimen is centered at the most extreme tilt of the batch
        if verbose:
            print("\nMoving the image shift to prepare for the next batch...")
        microscope.set_image_shift(x=this_signs_image_shifts[current_index - 1][0],
                                   y=this_signs_image_shifts[current_index - 1][1])

    return this_signs_image_shifts


if __name__ == "__main__":

    import pathlib
    import sys

    package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve()
    sys.path.append(str(package_directory))

    try:
        from Interface.TEMInterface import TEMInterface

        scope = TEMInterface()
    except BaseException as e:
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    start_alpha = -35
    stop_alpha = 30
    step_alpha = 1

    num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
    alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)
    middle_alphas = alpha_arr[0:-1] + step_alpha / 2

    print("\nWhole alpha array: " + str(alpha_arr))
    print("\nAlphas at which shifts will be computed: " + str(middle_alphas))

    print("\nObtaining shifts...")
    found_shifts = obtain_shifts(microscope=scope, camera_name='BM-Ceta', alphas=middle_alphas, verbose=True)
