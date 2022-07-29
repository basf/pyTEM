"""
 Author:  Michael Luciuk
 Date:    Summer 2022

This is BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows fast,
 high resolution 3D structure determination of small chemical compounds and biological macromolecules!
"""

import argparse
import warnings

import numpy as np

from pyTEM.Interface import Interface

from pyTEM_scripts.lib.micro_ed.exit_script import exit_script
from pyTEM_scripts.lib.micro_ed.messages import display_welcome_message, display_eucentric_height_message, \
    display_insert_and_align_sad_aperture_message, display_end_message, display_good_bye_message, \
    display_initialization_message, have_user_center_particle, display_beam_stop_center_spot_message, \
    display_second_condenser_message, display_insert_camera_message, display_insert_sad_aperture_message, \
    display_start_message
from pyTEM_scripts.lib.micro_ed.obtain_shifts import obtain_shifts
from pyTEM_scripts.lib.micro_ed.user_inputs import get_tilt_range, get_acquisition_parameters, get_out_file, \
    shift_correction_info
from pyTEM_scripts.lib.micro_ed.build_full_shifts_array import build_full_shift_array


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
         3. running the tilt series,
         4. performing any of the requested post-processing (e.g. downsampling),
         5. saving the results to file at the location of the users choosing.

         # TODO: Break this into separate smaller methods to enable batch processing where we perform steps 1 & 2 for a
            series of particles, and then perform steps 3, 4, and 5 for all the particles. Upon exception, jump to the
            next particle (if safe to do so).

        :param verbose: bool:
            Print out extra information. Useful for debugging.
        """
        if self.microscope is None:
            raise Exception("Error: Unable to run MicroED for there is no microscope connection.")

        # In order to minimize sample destruction, we want to expose as little as possible. However, during image shift
        #  calibration, we need to expose for long enough that we get usable images.
        # TODO: Find the lowest exposure time that still allows for reliable calibration
        shift_calibration_exposure_time = 0.25  # seconds
        shift_calibration_sampling = '1k'  # Lower resolution is faster but less precise

        try:
            # Display welcome and initialization messages
            display_welcome_message(microscope=self.microscope)
            display_initialization_message(microscope=self.microscope)

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
            self.microscope.set_image_shift(x=0, y=0)  # Zero the image shift.
            self.microscope.set_stage_position(alpha=0, speed=0.25)  # Zero the stage tilt.
            self.microscope.normalize()
            self.microscope.unblank_beam()

            # Have the user optimize the intensity using the second-condenser aperture and lens.
            display_second_condenser_message(microscope=self.microscope)

            # Have the user center on a dummy particle with which we can calibrate the eucentric height and aperture.
            have_user_center_particle(microscope=self.microscope, dummy_particle=True)

            # Have the user manually set eucentric height.  # TODO: Automate eucentric height calibration
            display_eucentric_height_message(microscope=self.microscope)

            # Have the user manually insert, align, and remove the SAD aperture.  # TODO: Automate SAD aperture controls
            display_insert_and_align_sad_aperture_message(microscope=self.microscope)

            # Have the user center the particle.
            have_user_center_particle(microscope=self.microscope)

            # We are now centered on the particle and need to keep the beam blank whenever possible.
            self.microscope.blank_beam()

            # The user is done making their adjustments, we can now retract the screen.
            self.microscope.retract_screen()

            # Get the required acquisition parameters.
            camera_name, integration_time, sampling, downsample = get_acquisition_parameters(microscope=self.microscope)

            # Confirm that the requested camera is actually inserted.
            display_insert_camera_message(microscope=self.microscope, camera_name=camera_name)

            # Get tilt range info
            alpha_arr = get_tilt_range(microscope=self.microscope, camera_name=camera_name)

            # Get the out path. (Where in the file system should we save the results?)
            out_file = get_out_file(microscope=self.microscope)

            # Fnd out if the user wants to use the automated image alignment functionality, and if so which angles they
            #  would like to sample.
            use_shift_corrections, samples = shift_correction_info(microscope=self.microscope,
                                                                   tilt_start=alpha_arr[0], tilt_stop=alpha_arr[-1],
                                                                   exposure_time=shift_calibration_exposure_time)
            if use_shift_corrections:
                # Compute the image shifts required to keep the currently centered section of the specimen centered at
                #  all alpha tilt angles. While alpha_arr is a complete array of alpha start-stop values, we need to
                # compute alphas - the interval midpoints which the correctional shifts will be based.
                alpha_step = alpha_arr[1] - alpha_arr[0]
                alphas = alpha_arr[0:-1] + alpha_step / 2

                # Sample at the requested tilt angles.
                shifts_at_samples = obtain_shifts(microscope=self.microscope, alphas=samples, camera_name=camera_name,
                                                  sampling=shift_calibration_sampling, batch_wise=False,
                                                  exposure_time=shift_calibration_exposure_time, verbose=verbose)
                if shifts_at_samples is None:
                    # We will proceed without compensatory image shifts, just make shifts all zero
                    warnings.warn("Automatic shift alignment failed :( proceeding without compensatory image shifts.")
                    shifts = np.full(shape=len(alpha_arr) - 1, dtype=(float, 2), fill_value=0.0)
                else:
                    # Go on and interpolate the rest.
                    shifts = build_full_shift_array(alphas=alphas, samples=samples, shifts_at_samples=shifts_at_samples,
                                                    kind="linear", interpolation_scope="local", verbose=verbose)

            else:
                # We will proceed without compensatory image shifts, just make shifts all zero.
                shifts = np.full(shape=len(alpha_arr) - 1, dtype=(float, 2), fill_value=0.0)

            # Have the user insert the previously aligned SAD aperture.
            display_insert_sad_aperture_message(microscope=self.microscope)

            # Switch to diffraction mode.
            self.microscope.set_projection_mode("diffraction")

            # If required, have the user insert the beam stop.
            # Additionally, this message will have the user center the diffraction spot.
            self.microscope.insert_screen()
            self.microscope.unblank_beam()
            display_beam_stop_center_spot_message(microscope=self.microscope)
            self.microscope.retract_screen()
            self.microscope.blank_beam()

            # Let the user know we are ready to begin!
            display_start_message(microscope=self.microscope)

            # We have everything we need, go ahead and actually perform the tilt series.
            acq_stack = self.microscope.acquisition_series(num=len(alpha_arr) - 1, camera_name=camera_name,
                                                           exposure_time=integration_time, sampling=sampling,
                                                           blanker_optimization=True, tilt_bounds=alpha_arr,
                                                           shifts=shifts, verbose=verbose)

            # Encase running unsupervised, it is a good idea to close the column valve once we are done.
            self.microscope.close_column_valve()

            # If requested, go ahead and downsample the series.
            if downsample:
                if verbose:
                    print("Downsampling images...")
                acq_stack.downsample()

            # Save the image stack to file.
            if verbose:
                print("Saving image stack to file as: " + out_file)
            acq_stack.save_to_file(out_file=out_file)

            # The acquisition is now complete, inform the user.
            display_end_message(microscope=self.microscope, out_file=out_file)

            # Give thanks to the user, and direct them to report issues on GitHub.
            display_good_bye_message(microscope=self.microscope)

            exit_script(microscope=self.microscope, status=0)

        except KeyboardInterrupt:
            warnings.warn("Keyboard interrupt detected...")
            exit_script(microscope=self.microscope, status=1)

        except Exception as e:
            print(e)
            exit_script(microscope=self.microscope, status=1)


def script_entry():
    """
    Entry point for the MicroED script. Once pyTEM is installed, view script usage by running the following command in
     a terminal window:

        micro_ed --help

    """
    parser = argparse.ArgumentParser(description="BASF's in-house micro-crystal electron diffraction (MicroED) "
                                                 "automated imaging script.")
    parser.add_argument("-v", "--verbose", help="Increase verbosity, especially useful when debugging.",
                        action="store_true")
    args = parser.parse_args()

    MicroED().run(verbose=args.verbose)


if __name__ == "__main__":
    MicroED().run(verbose=True)
