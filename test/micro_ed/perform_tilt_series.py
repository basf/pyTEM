"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

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
    from pyTEM.lib.micro_ed.AcquisitionSeriesProperties import AcquisitionSeriesProperties
except Exception as ImportException:
    raise ImportException


def perform_tilt_series(microscope: Interface, acquisition_properties: AcquisitionSeriesProperties,
                        shifts: np.array, verbose: bool) -> AcquisitionSeries:
    """
    Test performing a tilt-and-acquire series.

    :param microscope: pyTEM.Interface:
        A pyTEM interface to the microscope.
    :param acquisition_properties: AcquisitionSeriesProperties:
        The acquisition properties.
    :param shifts: np.array of float tuples:
        An array of tuples of the form (x, y) where x and y are the required image shifts (in microns) required to
         align the image at the corresponding tilt.
     :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: AcquisitionSeries.
        The results of the tilt series acquisition.
    """
    # Make sure the column valve is open nad the screen is removed.
    column_valve_position = microscope.get_column_valve_position()
    if column_valve_position == "closed":
        microscope.open_column_valve()
    screen_position = microscope.get_screen_position()
    if screen_position == "inserted":
        microscope.retract_screen()

    acq_stack = AcquisitionSeries()

    if verbose:
        print("Tilting to the start position.")
    microscope.set_stage_position(alpha=acquisition_properties.alpha_arr[0])  # Move to the start angle

    # Fill in the image stack array
    for i, alpha in enumerate(acquisition_properties.alphas):
        # So that both tilting and acquiring can happen simultaneously, tilt in a separate thread
        tilting_thread = TiltingThread(microscope=microscope, destination=acquisition_properties.alpha_arr[i + 1],
                                       integration_time=acquisition_properties.integration_time,
                                       speed=acquisition_properties.tilt_speed, verbose=verbose)

        # Apply the appropriate shift
        microscope.set_image_shift(x=shifts[i][0], y=shifts[i][1])

        tilting_thread.start()  # Start tilting

        # The acquisition must be performed here in the main thread where the COM interface was marshalled.
        overall_acq_start_time = time.time()
        acq, (core_acq_start, core_acq_end) = microscope.acquisition(
            camera_name=acquisition_properties.camera_name, sampling=acquisition_properties.sampling,
            exposure_time=acquisition_properties.integration_time)
        overall_acq_end_time = time.time()

        # Okay, wait for the tilting thread to return, and then we are done this one.
        tilting_thread.join()

        if verbose:
            print("\nCore acquisition started at: " + str(core_acq_start))
            print("Core acquisition returned at: " + str(core_acq_end))
            print("Core acquisition time: " + str(core_acq_end - core_acq_start))

            print("\nOverall acquisition() method call started at: " + str(overall_acq_start_time))
            print("Overall acquisition() method returned at: " + str(overall_acq_end_time))
            print("Total overall time spent in acquisition(): " + str(overall_acq_end_time - overall_acq_start_time))

        acq_stack.append(acq)

    # Housekeeping: Restore the column value and screen to the positions they were in before we started.
    if column_valve_position == "closed":
        microscope.close_column_valve()
    if screen_position == "inserted":
        microscope.insert_screen()

    return acq_stack


class TiltingThread(Thread):

    def __init__(self, microscope: Interface, destination: float, integration_time: float, speed: float,
                 verbose: bool = False):
        """
        :param microscope: pyTEM.Interface:
            A pyTEM interface to the microscope.
        :param destination: float:
            The alpha angle to which we will tilt.
        :param integration_time: float:
            The requested exposure time for the tilt image, in seconds.
        :param speed: float:
            Tilt speed, in TEM fractional tilt speed units.
        :param verbose: bool:
            Print out extra information. Useful for debugging.
        """
        Thread.__init__(self)
        self.microscope = microscope
        self.destination = destination
        self.speed = speed
        self.integration_time = integration_time
        self.verbose = verbose

    def run(self):
        # We need to give the acquisition thread a bit of a head start before we start tilting
        time.sleep(0.355 + self.integration_time)

        start_time = time.time()
        self.microscope.set_stage_position_alpha(alpha=self.destination, speed=self.speed, movement_type="go")
        stop_time = time.time()

        if self.verbose:
            print("\nStarting tilting at: " + str(start_time))
            print("Stopping tilting at: " + str(stop_time))
            print("Total time spent tilting: " + str(stop_time - start_time))


if __name__ == "__main__":
    """
    Testing
    """

    try:
        scope = Interface()
    except BaseException as e:
        print(e)
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    out_file = "C:/Users/Supervisor.TALOS-9950969/Downloads/test_series"

    start_alpha_ = -20
    stop_alpha_ = 20
    step_alpha_ = 1

    num_alpha = int((stop_alpha_ - start_alpha_) / step_alpha_ + 1)
    alpha_arr = np.linspace(start=start_alpha_, stop=stop_alpha_, num=num_alpha, endpoint=True)

    print("alpha_arr:")
    print(alpha_arr)

    aqc_props = AcquisitionSeriesProperties(camera_name='BM-Ceta', alpha_arr=alpha_arr,
                                            integration_time=0.5, sampling='1k')

    shifts_ = np.full(shape=len(aqc_props.alphas), dtype=(float, 2), fill_value=0.0)

    print("Shifts:")
    print(shifts_)

    acq_series = perform_tilt_series(microscope=scope, acquisition_properties=aqc_props, shifts=shifts_, verbose=True)

    # Save the image series to file.
    print("Saving image series to file as: " + out_file + ".mrc")
    acq_series.save_as_mrc(out_file + ".mrc")

    # Also, save each image individually as a jpeg for easy viewing.
    for counter, acquisition in enumerate(acq_series):
        out_file_temp = out_file + "_" + str(counter) + ".jpeg"
        print("Saving image #" + str(counter) + "to file as: " + out_file_temp)
        acquisition.save_to_file(out_file=out_file_temp, extension=".jpeg")
