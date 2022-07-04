"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import pathlib
import time
import sys

import numpy as np
from threading import Thread

package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.Interface import Interface
    from pyTEM.lib.interface.Acquisition import Acquisition
    from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
    from pyTEM.lib.ued.AcquisitionSeriesProperties import AcquisitionSeriesProperties
except Exception as ImportException:
    raise ImportException


def perform_tilt_series(microscope: Interface, acquisition_properties: AcquisitionSeriesProperties,
                        shifts: np.array, verbose: bool) -> None:
    """
    Actually perform a tilt series and save the results to file.

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
    acq_stack = AcquisitionSeries()

    if verbose:
        print("Tilting to the start position.")
    microscope.set_stage_position(alpha=acquisition_properties.alpha_arr[0])  # Move to the start angle

    # Fill in the image stack array
    for i, alpha in enumerate(acquisition_properties.alphas):
        # So that both tilting and acquiring can happen simultaneously, perform these tasks in separate threads
        tilting_thread = TiltingThread(microscope=microscope, destination=acquisition_properties.alpha_arr[i + 1],
                                       speed=acquisition_properties.tilt_speed, verbose=verbose)

        acquisition_thread = AcquisitionThread(microscope=microscope, acquisition_properties=acquisition_properties,
                                               verbose=verbose)

        # Apply the appropriate shift
        microscope.set_image_shift(x=shifts[i][0], y=shifts[i][1])

        acquisition_thread.start()  # Start the acquisition

        # We need to give the acquisition thread a bit of a head start before we start tilting
        time.sleep(0.355 + acquisition_properties.integration_time)

        tilting_thread.start()  # Start tilting

        # Okay, collect our threads and proceed
        tilting_thread.join()
        acq = acquisition_thread.join()

        acq_stack.append(acq)

    if acquisition_properties.downsample:
        if verbose:
            print("Downsampling images...")
        acq_stack.downsample()

    # Save each image individually as a jpeg for easy viewing.
    file_name_base, file_extension = os.path.splitext(acquisition_properties.out_file)
    for i, acq in enumerate(acq_stack):
        out_file = file_name_base + "_" + str(i) + ".jpeg"
        if verbose:
            print("Saving image #" + str(i) + "to file as: " + out_file)
        acq.save_to_file(out_file=out_file, extension=".jpeg")

    # Save the image stack to file.
    # if verbose:
    #     print("Saving image stack to file as: " + acquisition_properties.out_file)
    # image_stack.save_as_mrc(acquisition_properties.out_file)


class TiltingThread(Thread):

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
        Thread.__init__(self)
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


class AcquisitionThread(Thread):

    def __init__(self, microscope: Interface, acquisition_properties: AcquisitionSeriesProperties,
                 verbose: bool = False):
        """
        :param microscope: pyTEM.Interface:
            A pyTEM interface to the microscope.
        :param acquisition_properties: AcquisitionSeriesProperties:
            The acquisition properties.
        :param verbose: bool:
            Print out extra information. Useful for debugging.
        """
        Thread.__init__(self)
        self.microscope = microscope
        self.acquisition_properties = acquisition_properties
        self.verbose = verbose
        self.acq = None

    def run(self):
        overall_start_time = time.time()
        self.acq, (core_acq_start, core_acq_end) = self.microscope.acquisition(
            camera_name=self.acquisition_properties.camera_name,
            sampling=self.acquisition_properties.sampling,
            exposure_time=self.acquisition_properties.integration_time)
        overall_stop_time = time.time()

        if self.verbose:
            print("\nCore acquisition started at: " + str(core_acq_start))
            print("Core acquisition returned at: " + str(core_acq_end))
            print("Core acquisition time: " + str(core_acq_end - core_acq_start))

            print("\nOverall acquisition() method call started at: " + str(overall_start_time))
            print("Overall acquisition() method returned at: " + str(overall_stop_time))
            print("Total overall time spent in acquisition(): " + str(overall_stop_time - overall_start_time))

    def join(self, *args) -> Acquisition:
        Thread.join(self, *args)
        return self.acq


if __name__ == "__main__":

    try:
        scope = Interface()
    except BaseException as e:
        print(e)
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    start_alpha_ = -20
    stop_alpha_ = 20
    step_alpha_ = 1

    num_alpha = int((stop_alpha_ - start_alpha_) / step_alpha_ + 1)
    alpha_arr = np.linspace(start=start_alpha_, stop=stop_alpha_, num=num_alpha, endpoint=True)

    aqc_props = AcquisitionSeriesProperties(camera_name='BM-Ceta', alpha_arr=alpha_arr,
                                            integration_time=0.5, sampling='1k',
                                            out_file='C:/Users/Supervisor.TALOS-9950969/Downloads/test_series.jpeg')

    shifts_ = np.full(shape=len(aqc_props.alphas), dtype=(float, 2), fill_value=0.0)

    print("Shifts:")
    print(shifts_)

    perform_tilt_series(microscope=scope, acquisition_properties=aqc_props, shifts=shifts_, verbose=True)
