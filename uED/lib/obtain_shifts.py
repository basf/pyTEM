"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import numpy as np
import hyperspy.api as hs

# TODO: Still requires testing


def obtain_shifts(microscope, camera, alphas, exposure_time=3, sampling='1k'):
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
    :param camera: str:
        The name of the camera being used.
    :param sampling: str (default is '1k', this should be sufficient for just taking alignment photos):
        Photo resolution of the alignment images provided to hyperspy, one of:
        - '4k' for 4k images (4096 x 4096; sampling=1)
        - '2k' for 2k images (2048 x 2048; sampling=2)
        - '1k' for 1k images (1024 x 1024; sampling=3)
        - '0.5k' for 05.k images (512 x 512; sampling=8)
    :param exposure_time: float:
        Camera shutter speed, in seconds.

    :return: np.array: shifts:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt with the reference image (reference image taken with an alpha tilt
         of 0 degrees).
        Note: len(shifts) = len(alphas)
    """
    # Start with the no tilt and no image shift
    microscope.set_stage_position(alpha=0)  # Zero the stage tilt
    microscope.set_image_shift(x=0, y=0)  # Zero the image shift

    # Compute shifts in batches
    # Limiting the number of images per batch can help make sure the image doesn't change too much, and also helps
    #  make sure that we don't use too much RAM
    max_images_per_batch = 10

    negative_alphas = alphas[alphas < 0]
    positive_alphas = alphas[alphas >= 0]

    if alphas[0] > 0:
        # Then we are tilting pos -> neg, flip the positive array.
        positive_alphas = np.flip(positive_alphas)  # Now it will start with the least negative values
    else:
        # We are tilting neg -> pos, flip the negative array.
        negative_alphas = np.flip(negative_alphas)  # Now it will start with the least positive values

    print("\nComputing negative shifts using the following alphas: " + str(negative_alphas))
    # Compute the required shifts at negative alphas
    negative_shifts = _complete_one_sign(microscope=microscope, this_signs_alphas=negative_alphas, camera=camera,
                                         sampling=sampling, exposure_time=exposure_time,
                                         max_images_per_batch=max_images_per_batch)

    # Reset the image shift and tilt to 0 deg
    microscope.set_stage_position(alpha=0)  # Zero the stage tilt
    microscope.set_image_shift(x=0, y=0)  # Zero the image shift

    # Compute the required shifts at positive alphas
    print("\nComputing positive shifts using the following alphas: " + str(positive_alphas))
    positive_shifts = _complete_one_sign(microscope=microscope, this_signs_alphas=positive_alphas, camera=camera,
                                         sampling=sampling, exposure_time=exposure_time,
                                         max_images_per_batch=max_images_per_batch)

    # One array of shifts will need to be flipped back (because it will have been built from a flipped array)
    if alphas[0] > 0:
        # Then we are tilting pos -> neg, flip the positive array and merge the two shift arrays
        positive_shifts = np.flip(positive_shifts)
        shifts = np.concatenate((positive_shifts, negative_shifts))
    else:
        # We are tilting neg -> pos, flip the negative array and merge the two shift arrays
        negative_shifts = np.flip(negative_shifts)
        shifts = np.concatenate((negative_shifts, positive_shifts))

    return shifts


def _complete_one_sign(microscope, this_signs_alphas, max_images_per_batch, camera, sampling, exposure_time):
    """
    Because we want the user to center the specimen at 0 degrees (to reduce the overall shift), we need to separately
     compute:
     - the shifts at positive tilt angles
     - the shifts at negative tilt angles

    This function computes the shifts for just one sign, and by calling it twice we are able to compute all the shifts.

    :param microscope: TEMInterface:
        A TEMInterface interface to the microscope.
    :param this_signs_alphas: np.array:
        An array with either the positive alphas or the negative alphas.
    :param max_images_per_batch: int:

    :param camera: str:
        The name of the camera being used.
    :param sampling: str (default is '1k', this should be sufficient for most applications):
        Photo resolution of the image-shift calibration images, one of:
        - '4k' for 4k images (4096 x 4096; sampling=1)
        - '2k' for 2k images (2048 x 2048; sampling=2)
        - '1k' for 1k images (1024 x 1024; sampling=3)
        - '0.5k' for 05.k images (512 x 512; sampling=8)
    :param exposure_time: float:
        Camera shutter speed, in seconds.

    :return: np.array:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt.
    """
    # Preallocate
    this_signs_shifts = np.full(shape=len(this_signs_alphas), dtype=(float, 2), fill_value=np.nan)

    # We will start filling in this_signs_shifts at the beginning
    current_index = 0

    # When computing the number of batches, we subtract one to make room for the reference image
    number_of_batches = int(len(this_signs_alphas) / (max_images_per_batch - 1))
    alpha_batches = np.split(this_signs_alphas, number_of_batches)

    print("\nHere are the alpha_batches: ")
    print(alpha_batches)

    # Loop through the batches, computing the image shifts one batch at a time
    for i, batch in enumerate(alpha_batches):
        print("\nBatch #" + str(i) + ": " + str(batch))

        # Reset the reference image-shift
        reference_image_shift = microscope.get_image_shift()

        # Take a reference image
        reference_acq = microscope.acquisition(camera_name=camera, sampling=sampling, exposure_time=exposure_time)
        reference_image = reference_acq.get_image()

        # Preallocate
        print("\nPreallocate...")
        number_images = len(batch) + 1  # Plus one to make room for the reference image
        image_shape = np.shape(reference_image)
        image_stack_arr = np.full(shape=(number_images, image_shape[0], image_shape[1]), fill_value=np.nan)
        image_stack_arr[0] = reference_image  # put the reference image at the start of the array (top of the stack)

        # Obtain the pixel size from the reference acquisition
        print("\nGrab pixel size from metadata..")
        reference_metadata = reference_acq.get_metadata()
        pixel_size_x = reference_metadata['PixelSize'][0] * 1e6  # m -> um
        pixel_size_y = reference_metadata['PixelSize'][1] * 1e6

        # Loop through each tilt angle in the batch.
        for j, alpha in enumerate(batch):
            print("Taking image at index j=" + str(j))
            microscope.set_stage_position(alpha=alpha)  # Tilt the stage to the required alpha
            acq = microscope.acquisition(camera_name=camera, sampling=sampling, exposure_time=exposure_time)
            image_stack_arr[j + 1] = acq.get_image()

        print(np.shape(image_stack_arr))
        print(image_stack_arr[0])

        # Use Hyperspy to compute shifts for this batch's stack
        # image_stack = hs.stack([image for image in image_stack_arr])
        image_stack = hs.stack(signal_list=image_stack_arr, axis=0)  # TODO: StopIteration Error
        batch_shifts = image_stack.estimate_shift2D()
        batch_shifts = np.delete(batch_shifts, 0)  # The first shift corresponds to the reference image, throw it away.

        # Log the rest of shifts in the array, make sure to multiply by the pixel size so the result is in microns.
        for j in batch_shifts:
            this_signs_shifts[current_index] = (pixel_size_x * (batch_shifts[j][0]) + reference_image_shift[0],
                                                pixel_size_y * (batch_shifts[j][1]) + reference_image_shift[1])
            current_index = current_index + 1

        # reset the image shift and reference image to be the last image in the batch
        reference_image_shift = this_signs_shifts[current_index - 1]
        microscope.set_image_shift(x=reference_image_shift[0], y=reference_image_shift[1])

    return this_signs_shifts


if __name__ == "__main__":

    import pathlib
    import sys

    package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve()
    sys.path.append(str(package_directory))

    try:
        from Interface.TEMInterface import TEMInterface
        scope = TEMInterface()
    except:
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    start_alpha = -10  # TODO: Doesn't work with less than 10 deg
    stop_alpha = 10
    step_alpha = 1

    num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
    alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)
    middle_alphas = alpha_arr[0:-1] + step_alpha / 2

    print("\nWhole alpha array: " + str(alpha_arr))
    print("\nAlphas at which shifts will be computed: " + str(middle_alphas))

    print("\nObtaining shifts...")
    obtain_shifts(microscope=scope, camera='BM-Ceta', alphas=middle_alphas, exposure_time=1, sampling='1k')
