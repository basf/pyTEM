"""
 Author:  Michael Luciuk
 Date:    Summer 2022

This is BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows fast,
 high resolution 3D structure determination of small chemical compounds and biological macromolecules!
"""

import os
import warnings
import pathlib
import sys

import numpy as np

# Add the pyTEM package directory to path
package_directory = pathlib.Path().resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.Interface import Interface

    from pyTEM.lib.micro_ed.exit_script import exit_script
    from pyTEM.lib.micro_ed.AcquisitionSeriesProperties import AcquisitionSeriesProperties
    from pyTEM.lib.micro_ed.messages import get_welcome_message, get_initialization_message, display_message, \
        get_alignment_message, get_start_message, get_eucentric_height_message, get_end_message, get_good_bye_message, \
        get_insert_and_align_sad_aperture_message
    from pyTEM.lib.micro_ed.obtain_shifts import obtain_shifts
    from pyTEM.lib.micro_ed.perform_tilt_series import perform_tilt_series
    from pyTEM.lib.micro_ed.user_inputs import get_tilt_range, get_acquisition_parameters, get_out_file, \
        shift_correction_info, have_user_center_particle
    from pyTEM.lib.micro_ed.build_full_shifts_array import build_full_shift_array

except Exception as ImportException:
    raise ImportException


class MicroED:
    """
    A MicroED objection that can be used to run MicroED experiments.
    """

    def __init__(self):
        # Try to connect to a microscope
        try:
            self.microscope = Interface()
            print("Microscope connection established successfully.")
        except BaseException as e:
            warnings.warn("MicroED was unable to connect to a microscope, try (re)connecting with MicroED.connect(). "
                          "\nError details:" + str(e))
            self.microscope = None

    def connect(self) -> None:
        """
        Try to connect/reconnect to the microscope.
        """
        try:
            self.microscope = Interface()
            print("Microscope connection established successfully.")
        except BaseException as e:
            warnings.warn("MicroED was unable to connect to a microscope, try (re)connecting with MicroED.connect(). "
                          "\nError details:" + str(e))
            self.microscope = None

    def run(self, verbose: bool = False) -> None:
        """
        Perform a MicroED automated imaging sequence.

        To reduce dose, the beam is kept blank whenever possible.

        This involves:
         1. prompting the user for the required information,
         2. automatically computing compensatory image shifts,
         3. performing any of the requested post-processing (e.g. downsampling),
         4. running the tilt series,
         5. saving the results to file at the location of the users choosing.

        :param verbose: bool:
            Print out extra information. Useful for debugging.
        """
        if self.microscope is None:
            raise Exception("Error: Unable to run MicroED for there is no microscope connection.")
        else:
            # To reduce dose, keep the microscope blanked whenever possible.
            self.microscope.blank_beam()

        # In order to minimize sample destruction, we want to expose as little as possible. However, during image shift
        #  calibration, we need to expose for long enough that we get usable images.
        shift_calibration_exposure_time = 0.25  # s

        try:
            # Display welcome messages
            title, message = get_welcome_message()
            display_message(title=title, message=message, microscope=self.microscope, position="centered")
            title, message = get_initialization_message()
            display_message(title=title, message=message, microscope=self.microscope, position="centered")

            # Initialize for MicroED
            if self.microscope.get_screen_position() != "inserted":
                self.microscope.insert_screen()
            if self.microscope.get_column_valve_position() != "open":
                self.microscope.open_column_valve()  # Might not work if the column isn't under vacuum
            # Confirm that the column valve was actually opened
            if self.microscope.get_column_valve_position() == "closed":
                raise Exception("Error: We were unable to open the column value, probably because the column isn't "
                                "under sufficient vacuum. Please check the instrument.")
            if self.microscope.get_mode() != "TEM":
                self.microscope.set_mode("TEM")
            if self.microscope.get_projection_mode() != "imaging":
                self.microscope.set_projection_mode("imaging")
            self.microscope.set_image_shift(x=0, y=0)  # Zero the image shift
            self.microscope.set_stage_position(alpha=0)  # Zero the stage tilt
            self.microscope.normalize()

            # Have the user center the particle
            have_user_center_particle(microscope=self.microscope)

            # Have the user manually set eucentric height  # TODO: Automate eucentric height calibration
            title, message = get_eucentric_height_message()
            self.microscope.unblank_beam()
            display_message(title=title, message=message, microscope=self.microscope, position="out-of-the-way")
            self.microscope.blank_beam()

            # Get tilt range info
            alpha_arr = get_tilt_range(microscope=self.microscope)

            # Get the required camera parameters
            camera_name, integration_time, sampling, downsample = get_acquisition_parameters(microscope=self.microscope)

            # Get the out path (where in the file system should we save the results?)
            out_file = get_out_file(microscope=self.microscope)

            # Store all the acquisition properties in a AcquisitionSeriesProperties object, this just makes it easier
            #  and safer to pass around all things acquisition
            acquisition_properties = AcquisitionSeriesProperties(camera_name=camera_name, alpha_arr=alpha_arr,
                                                                 integration_time=integration_time, sampling=sampling)

            # Fnd out if the user wants to use the automated image alignment functionality, and if so which angles they
            #  would like to sample and which interpolation strategy they would like to use to obtain the rest.
            use_shift_corrections, samples, interpolation_scope = \
                shift_correction_info(microscope=self.microscope, tilt_start=alpha_arr[0], tilt_stop=alpha_arr[-1],
                                      exposure_time=shift_calibration_exposure_time)
            if use_shift_corrections:
                # Compute the image shifts required to keep the currently centered section of the specimen centered at
                #  all alpha tilt angles.
                shifts_at_samples = obtain_shifts(microscope=self.microscope, alphas=samples, verbose=verbose,
                                                  camera_name=acquisition_properties.camera_name,
                                                  exposure_time=shift_calibration_exposure_time)

                shifts = build_full_shift_array(alphas=acquisition_properties.alphas, samples=samples,
                                                shifts_at_samples=shifts_at_samples, kind="linear",
                                                interpolation_scope=interpolation_scope, verbose=verbose)

            else:
                # We will proceed without compensatory image shifts, just make shifts all zero
                shifts = np.full(shape=len(acquisition_properties.alphas), dtype=(float, 2), fill_value=0.0)

            # Have the user manually insert and center the SAD aperture  # TODO: Automate SAD aperture controls
            title, message = get_insert_and_align_sad_aperture_message()
            self.microscope.unblank_beam()
            display_message(title=title, message=message, microscope=self.microscope, position="out-of-the-way")
            self.microscope.blank_beam()

            # Confirm the user is happy, remove the screen, and start the procedure
            title, message = get_start_message()
            display_message(title=title, message=message, microscope=self.microscope, position="centered")

            # microscope.set_projection_mode("diffraction")  # Switch to diffraction mode

            # Go ahead and actually perform the tilt series, saving the results to file.
            acq_stack = perform_tilt_series(microscope=self.microscope, acquisition_properties=acquisition_properties,
                                            shifts=shifts, verbose=verbose)

            if downsample:
                if verbose:
                    print("Downsampling images...")
                acq_stack.downsample()

            # Save each image individually as a jpeg for easy viewing.
            file_name_base, file_extension = os.path.splitext(out_file)
            for i, acq in enumerate(acq_stack):
                out_file = file_name_base + "_" + str(i) + ".jpeg"
                if verbose:
                    print("Saving image #" + str(i) + "to file as: " + out_file)
                acq.save_to_file(out_file=out_file, extension=".jpeg")

            # Save the image stack to file.
            # if verbose:
            #     print("Saving image stack to file as: " + acquisition_properties.out_file)
            # image_stack.save_as_mrc(acquisition_properties.out_file)

            # The acquisition is now complete, inform the user.
            title, message = get_end_message(out_file=out_file)
            display_message(title=title, message=message, microscope=self.microscope, position="centered")

            # Thanks to the user, and direct them to report issues on GitHub.
            title, message = get_good_bye_message()
            display_message(title=title, message=message, microscope=self.microscope, position="centered")

            exit_script(microscope=self.microscope, status=0)

        except KeyboardInterrupt:
            warnings.warn("Keyboard interrupt detected...")
            exit_script(microscope=self.microscope, status=1)

        except Exception as e:
            print(e)
            exit_script(microscope=self.microscope, status=1)


if __name__ == "__main__":
    MicroED().run(verbose=True)
