"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import threading
import pathlib
import time
import sys

import numpy as np

package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.Interface import Interface
    from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
    from pyTEM.lib.ued.AcquisitionSeriesProperties import AcquisitionSeriesProperties
except Exception as ImportException:
    raise ImportException


def perform_tilt_series(microscope: Interface, acquisition_properties: AcquisitionSeriesProperties,
                        shifts: np.array, verbose: bool) -> None:
    """
    Actually perform a tilt series and save the returns to file.

    :param microscope: pyTEM.Interface:
        A pyTEM interface to the microscope.
    :param acquisition_properties: AcquisitionSeriesProperties:
        The acquisition properties.
    :param shifts: np.array of float tuples:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt.
     :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: None.
        Tilt series results are automatically saved to file.
    """
    image_stack = AcquisitionSeries()

    if verbose:
        print("Tilting to the start position.")
    microscope.set_stage_position(alpha=acquisition_properties.alpha_arr[0])  # Move to the start angle

    # Fill in the image stack array
    for i, alpha in enumerate(acquisition_properties.alphas):

        # So that tilting can happen simultaneously, it will be performed in a separate thread
        tilting_thread = TiltingThread(microscope=microscope, destination=acquisition_properties.alpha_arr[i + 1],
                                       speed=acquisition_properties.tilt_speed, verbose=verbose)

        # Apply the appropriate shift
        microscope.set_image_shift(x=shifts[i][0], y=shifts[i][1])

        tilting_thread.start()  # Start tilting

        # Take an image
        acq = microscope.acquisition(camera_name=acquisition_properties.camera_name,
                                     sampling=acquisition_properties.sampling,
                                     exposure_time=acquisition_properties.integration_time)

        tilting_thread.join()

        image_stack.append(acq.get_image())

    if verbose:
        print("Saving image stack to file as: " + acquisition_properties.out_file)
    image_stack.save_as_mrc(acquisition_properties.out_file)


class TiltingThread (threading.Thread):

    def __init__(self, microscope: Interface, destination: float, speed: float, verbose: bool = False):
        """
        :param microscope: pyTEM.Interface:
            A pyTEM interface to the microscope.
        :param destination: float:
            The alpha angle to which we will tilt.
        :param speed: float:
            Tilt speed, in TEM fractional tilt speed units.
        :param verbose: bool:
            Print out extra information. Useful for debugging.
        """
        threading.Thread.__init__(self)
        self.microscope = microscope
        self.destination = destination
        self.speed = speed
        self.verbose = verbose

    def run(self):

        start_time = time.time()
        self.microscope.set_stage_position_alpha(alpha=self.destination, speed=self.speed, movement_type="go")
        stop_time = time.time()

        if self.verbose:
            print("\nStarting tilting at: " + str(start_time))
            print("Stopping tilting at: " + str(stop_time))
            print("Total time spent tilting: " + str(stop_time - start_time))


if __name__ == "__main__":

    try:
        scope = Interface()
    except BaseException as e:
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    start_alpha_ = -20
    stop_alpha_ = 20
    step_alpha_ = 1

    num_alpha = int((stop_alpha_ - start_alpha_) / step_alpha_ + 1)
    alpha_arr = np.linspace(start=start_alpha_, stop=stop_alpha_, num=num_alpha, endpoint=True)

    aqc_props = AcquisitionSeriesProperties(camera_name='BM-Ceta', alpha_arr=alpha_arr, integration_time=0.5,
                                            sampling='1k', out_file=None)

    shifts_ = np.full(shape=len(aqc_props.alphas), dtype=(float, 2), fill_value=0.0)

    print("Shifts:")
    print(shifts_)

    perform_tilt_series(microscope=scope, acquisition_properties=aqc_props, shifts=shifts_, verbose=True)
