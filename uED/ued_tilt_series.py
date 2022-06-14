"""
 Author:  Michael Luciuk
 Date:    Summer 2022

This is BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows fast,
 high resolution 3D structure determination of small chemical compounds biological macromolecules!
"""

import warnings
import pathlib
import sys

import numpy as np

package_directory = pathlib.Path().resolve().parent.resolve()
sys.path.append(str(package_directory))

try:
    from uED.lib.exit_script import exit_script
    from Interface.TEMInterface import TEMInterface
    from uED.lib.messages import get_welcome_message, get_initialization_message, display_message, \
        get_alignment_message, get_start_message, get_eucentric_height_message, get_end_message, get_good_bye_message
    from uED.lib.obtain_shifts import obtain_shifts
    from uED.lib.perform_tilt_series import perform_tilt_series
    from uED.lib.user_inputs import get_tilt_range, get_camera_parameters, get_out_file

except Exception as ImportException:
    raise ImportException


def ued_tilt_series():
    """
    Perform a MicroED automated imaging sequence.

    This involves prompting the user for the required information, automatically computing the required image shifts
     (to compensate for lateral movement of the image during titling), and running a tilt series.

    Results are automatically saved to file at a location of the users choosing.
    """
    microscope = None
    try:
        # Display a welcome message
        title, message = get_welcome_message()
        display_message(title=title, message=message, microscope=microscope, position="centered")

        # Connect to the microscope and Initialize for MicroED
        title, message = get_initialization_message()
        display_message(title=title, message=message, microscope=microscope, position="centered")
        microscope = TEMInterface()
        microscope.insert_screen()
        microscope.open_column_valve()  # Might not work if the column isn't under vacuum
        if microscope.get_column_valve_position() == "Closed":
            raise Exception("Error: We were unable to open the column value, probably because the column isn't "
                            "under sufficient vacuum. Please check the instrument.")

        microscope.set_mode("TEM")
        microscope.set_projection_mode("Imaging")
        microscope.set_image_shift(x=0, y=0)  # Zero the image shift
        microscope.set_stage_position(alpha=0)  # Zero the stage tilt
        microscope.unblank_beam()
        microscope.normalize()

        while True:
            # Have the user center the particle
            title, message = get_alignment_message()
            display_message(title=title, message=message, microscope=microscope, position="out-of-the-way")

            # Confirm that we are in the correct magnification range (at the time of writing image shift is only
            #  calibrated for magnifications in the SA range)
            if microscope.get_projection_submode() == "SA":
                break  # Input is okay  # TODO: Add tkinter validation to Entry widgets
            else:
                warnings.warn("Currently we are in the " + str(microscope.get_projection_submode())
                              + " magnification range, please select a magnification in the SA range.")

        # Have the user manually set eucentric height  # TODO: Automate eucentric height calibration
        title, message = get_eucentric_height_message()
        display_message(title=title, message=message, microscope=microscope, position="out-of-the-way")

        # Get tilt range info
        start_alpha, stop_alpha, step_alpha = get_tilt_range(microscope=microscope)
        while True:
            # Check to make sure that step_alpha has the right sign
            if (start_alpha > stop_alpha and step_alpha < 0) or (start_alpha < stop_alpha and step_alpha > 0):
                # Check to make sure the tilt range includes 0
                if (start_alpha > 0 and stop_alpha < 0) or (start_alpha < 0 and stop_alpha > 0):
                    break  # Input is okay  # TODO: Add tkinter validation to Entry widgets
            else:
                warnings.warn("Invalid tilt range, please try again!")

        # Get the required camera parameters
        while True:
            camera_name, integration_time, binning = get_camera_parameters(microscope=microscope)
            min_supported_exposure_time, max_supported_exposure_time = microscope.get_exposure_time_range(camera_name)
            if min_supported_exposure_time < integration_time < max_supported_exposure_time:
                break  # Input is okay  # TODO: Add tkinter validation to Entry widgets
            else:
                warnings.warn("Invalid integration time. Integration time must be between "
                              + str(min_supported_exposure_time) + " and " + str(max_supported_exposure_time)
                              + " seconds.")

        # Get the out path (where in the file system should we save the results?)
        out_file = get_out_file(microscope=microscope)

        # Confirm the user is happy, remove the screen, and start the procedure
        title, message = get_start_message()
        display_message(title=title, message=message, microscope=microscope, position="centered")
        microscope.remove_screen()

        num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
        alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)

        # Compute the image shifts required to keep the currently centered section of the specimen centered at all
        #  alpha tilt angles.
        shifts = obtain_shifts(microscope=microscope, camera=camera_name, alphas=alpha_arr[0:-1] + step_alpha / 2)

        print("alphas: " + str(alpha_arr[0:-1] + step_alpha / 2))
        print("Shifts: " + str(shifts))

        microscope.set_projection_mode("Diffraction")  # Switch to diffraction mode

        # Go ahead and actually perform the tilt series, saving the results to file.
        perform_tilt_series(microscope=microscope, camera=camera_name, integration_time=integration_time,
                            binning=binning, alpha_arr=alpha_arr, shifts=shifts, out_file=out_file)

        # The acquisition is now complete, inform the user.
        title, message = get_end_message(out_file=out_file)
        display_message(title=title, message=message, microscope=microscope, position="centered")

        # Thanks to the user, and direct them to report issues on GitHub.
        title, message = get_good_bye_message()
        display_message(title=title, message=message, microscope=microscope, position="centered")

    except KeyboardInterrupt:
        warnings.warn("Keyboard interrupt detected, returning the microscope to a safe state and exiting.")
        exit_script(microscope=microscope, status=1)

    except Exception as e:
        raise e


if __name__ == "__main__":
    ued_tilt_series()
