"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import threading
import time

import numpy as np
from tifffile import tifffile


def perform_tilt_series(microscope, acquisition_properties, shifts, verbose):
    """
    Actually perform a tilt series and save the returns to file.

    :param microscope: pyTEM:
        A pyTEM interface to the microscope.
    :param acquisition_properties: AcquisitionProperties:
        The acquisition properties.
    :param shifts: np.array of float tuples:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt.
     :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: None.
        Tilt series results are automatically saved to file.
    """
    # Take a quick test image just to get the image size
    if verbose:
        print("Taking a reference image to get the image size...")
    reference_acq = microscope.acquisition(camera_name=acquisition_properties.camera_name,
                                           sampling=acquisition_properties.sampling, exposure_time=0.5)
    reference_image = reference_acq.get_image()
    image_shape = np.shape(reference_image)
    image_stack_arr = np.full(shape=(len(acquisition_properties.alphas), image_shape[0], image_shape[1]),
                              fill_value=np.nan)

    microscope.set_stage_position(alpha=acquisition_properties.alpha_arr[0])  # Move to the start angle

    # So that tilting can happen simultaneously, it will be performed in a separate thread
    tilting_thread = TiltingThread(microscope=microscope, acquisition_properties=acquisition_properties,
                                   verbose=verbose)
    tilting_thread.start()  # Start tilting

    # Iterate through the angles, taking pictures
    for i, alpha in enumerate(acquisition_properties.alphas):
        if verbose:
            print("Taking image number " + str(i) + " at \u03B1=" + str(alpha))
        microscope.set_image_shift(x=shifts[i][0], y=shifts[i][1])
        acq = microscope.acquisition(camera_name=acquisition_properties.camera_name,
                                     sampling=acquisition_properties.sampling,
                                     exposure_time=acquisition_properties.integration_time)
        image_stack_arr[i] = acq.get_image()

    tilting_thread.join()

    if verbose:
        print("Saving image stack to file.")
    tifffile.imwrite(acquisition_properties.out_file, image_stack_arr, metadata=reference_acq.get_metadata())


class TiltingThread (threading.Thread):

    def __init__(self, microscope, acquisition_properties, verbose):
        threading.Thread.__init__(self)
        self.microscope = microscope
        self.acquisition_properties = acquisition_properties
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("Starting tilting at " + str(time.ctime(time.time())))

        self.microscope.set_stage_position_alpha(self, alpha=self.acquisition_properties.alpha_arr[-1],
                                                 speed=self.acquisition_properties.tilt_speed, movement_type="go")

        if self.verbose:
            print("Stopping tilting at " + str(time.ctime(time.time())))


if __name__ == "__main__":
    import pathlib
    import sys

    from pyTEM.lib.ued.AcquisitionProperties import AcquisitionProperties

    package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve()
    sys.path.append(str(package_directory))

    try:
        from pyTEM.Interface import Interface

        scope = Interface()
    except BaseException as e:
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    start_alpha = -10
    stop_alpha = 10
    step_alpha = 1

    num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
    alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)

    aqc_props = AcquisitionProperties(camera_name='BM-Ceta', alpha_arr=alpha_arr, integration_time=3, sampling='1k',
                                      out_file=None)

    shifts_ = np.full(shape=len(aqc_props.alphas), dtype=(float, 2), fill_value=0.0)

    print("Shifts:")
    print(shifts_)

    perform_tilt_series(microscope=scope, acquisition_properties=aqc_props, shifts=shifts_, verbose=True)

