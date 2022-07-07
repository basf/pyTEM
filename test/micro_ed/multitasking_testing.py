"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import threading
import multiprocessing
import pathlib
import time
import sys

import numpy as np
import comtypes.client as cc
import pythoncom

package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve().parent.resolve()
print(package_directory)
sys.path.append(str(package_directory))
try:
    from pyTEM.Interface import Interface
    from pyTEM.lib.interface.AcquisitionSeries import AcquisitionSeries
    from pyTEM.lib.micro_ed.AcquisitionSeriesProperties import AcquisitionSeriesProperties
    from pyTEM.lib.interface.mixins.BeamBlankerMixin import BeamBlankerInterface
except Exception as ImportException:
    raise ImportException

# https://stackoverflow.com/questions/3246525/why-cant-i-create-a-com-object-in-a-new-thread-in-python


def multitasking_testing(microscope: Interface, acquisition_properties: AcquisitionSeriesProperties,
                         shifts: np.array) -> None:
    """
    Test to see which microscope systems can be controlled concurrently.
    """
    image_stack = AcquisitionSeries()

    print("Tilting to the start position.")
    microscope.set_stage_position(alpha=acquisition_properties.alpha_arr[0])  # Move to the start angle

    # Fill in the image stack array
    for i, alpha in enumerate(acquisition_properties.alphas):
        # So that tilting can happen simultaneously, it will be performed in a separate thread
        # tilting_thread = TiltingThread(microscope=microscope, destination=acquisition_properties.alpha_arr[i + 1],
        #                                speed=acquisition_properties.tilt_speed, verbose=verbose)
        blanking_process = multiprocessing.Process(target=blanker, args=(acquisition_properties.alpha_arr[i + 1],
                                                                         acquisition_properties.tilt_speed))

        # Apply the appropriate shift
        microscope.set_image_shift(x=shifts[i][0], y=shifts[i][1])

        # Start tilting
        # tilting_thread.start() 
        blanking_process.start()

        time.sleep(3)

        # Take an image
        acq, (core_acq_start, core_acq_end) = microscope.acquisition(
            camera_name=acquisition_properties.camera_name, sampling=acquisition_properties.sampling,
            exposure_time=acquisition_properties.integration_time)

        # tilting_thread.join()
        blanking_process.join()

        print("\nCore acquisition started at: " + str(core_acq_start))
        print("Core acquisition returned at: " + str(core_acq_end))
        print("Core acquisition time: " + str(core_acq_end - core_acq_start))

        image_stack.append(acq)

    # if verbose:
    #    print("Saving image stack to file as: " + acquisition_properties.out_file)
    # image_stack.save_as_mrc(acquisition_properties.out_file)


class TiltingThread(threading.Thread):

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
        """
        Creating a new COM interface doesn't work.
        """
        # pythoncom.CoInitialize()
        # tem = cc.CreateObject("TEMScripting.Instrument")
        # print(tem.Projection.Mode)
        # pythoncom.CoUninitialize()

        """ 
        Accessing the illumination and projection functionality of the passed interface doesn't work 
        """
        # print(self.microscope._tem.Stage.Status)
        # print(self.microscope._tem.Vacuum.ColumnValvesOpen)
        # print(self.microscope._tem.Illumination.BeamBlanked)

        """
        We are able to access the stage controls (including tilting) just fine.
        """
        start_time = time.time()
        self.microscope.set_stage_position_alpha(alpha=self.destination, speed=self.speed, movement_type="go")
        stop_time = time.time()

        print("\nStarting tilting at: " + str(start_time))
        print("Stopping tilting at: " + str(stop_time))
        print("Total time spent tilting: " + str(stop_time - start_time))


class TiltingProcess(multiprocessing.Process):

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

        multiprocessing.Process.__init__(self)
        # self.microscope = microscope
        self.microscope = microscope
        self.destination = destination
        self.speed = speed
        self.verbose = verbose

    def run(self):
        # pythoncom.CoInitialize()
        # tem = cc.CreateObject("TEMScripting.Instrument")
        # pythoncom.CoUninitialize()
        # print(self.microscope._tem.Stage.Status)
        # print(self.microscope._tem.Vacuum.ColumnValvesOpen)
        # print(tem.Projection.Mode)
        # print(self.microscope._tem.Illumination.BeamBlanked)

        start_time = time.time()
        self.microscope.set_stage_position_alpha(alpha=self.destination, speed=self.speed, movement_type="go")
        stop_time = time.time()

        if self.verbose:
            print("\nStarting tilting at: " + str(start_time))
            print("Stopping tilting at: " + str(stop_time))
            print("Total time spent tilting: " + str(stop_time - start_time))


def blanker(exposure_time):
    """

    :param exposure_time: float:
            The requested exposure time, in seconds.
    :return:
    """
    beam_blanker_interface = BeamBlankerInterface()

    # tem = cc.CreateObject("TEMScripting.Instrument")
    # tem.Illumination.BeamBlanked = True

    # Wait for one exposure_time period while the camera prepares itself.
    time.sleep(exposure_time)

    # Unblank for one exposure_time while the acquisition is active.
    beam_unblank_time = time.time()
    beam_blanker_interface.unblank_beam()
    time.sleep(exposure_time)
    beam_reblank_time = time.time()
    beam_blanker_interface.blank_beam()

    print("\nUnblanked the beam at: " + str(beam_unblank_time))
    print("Re-blanked the beam at: " + str(beam_reblank_time))
    print("Total time spent with the beam unblanked: " + str(beam_reblank_time - beam_unblank_time))


if __name__ == "__main__":

    try:
        scope = Interface()
    except BaseException as e:
        print(e)
        print("Unable to connect to microscope, proceeding with None object.")
        scope = None

    # BeamBlanker()

    start_alpha_ = -2
    stop_alpha_ = 2
    step_alpha_ = 1

    num_alpha = int((stop_alpha_ - start_alpha_) / step_alpha_ + 1)
    alpha_arr = np.linspace(start=start_alpha_, stop=stop_alpha_, num=num_alpha, endpoint=True)

    aqc_props = AcquisitionSeriesProperties(camera_name='BM-Ceta', alpha_arr=alpha_arr, integration_time=3,
                                            sampling='1k')

    shifts_ = np.full(shape=len(aqc_props.alphas), dtype=(float, 2), fill_value=0.0)

    print("Shifts:")
    print(shifts_)

    multitasking_testing(microscope=scope, acquisition_properties=aqc_props, shifts=shifts_)
