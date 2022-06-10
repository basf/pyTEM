"""
 Author:  Michael Luciuk
 Date:    Summer 2022

This is BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging script. MicroED allows fast,
 high resolution 3D structure determination of small chemical compounds biological macromolecules!
"""
import warnings
import numpy as np

from uED.lib.exit_script import exit_script
# from Interface.TEMInterface import TEMInterface
from uED.lib.messages import get_welcome_message, get_initialization_message, display_message, get_alignment_message, \
    get_start_message, get_end_message, get_good_bye_message
from uED.lib.obtain_shifts import obtain_shifts
from uED.lib.perform_tilt_series import perform_tilt_series
from uED.lib.user_inputs import get_tilt_range, get_camera_parameters, get_out_file


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
        # microscope = TEMInterface()
        # microscope.insert_screen()
        # microscope.open_column_valve()
        # microscope.set_mode("TEM")
        # microscope.set_projection_mode("Imaging")
        # microscope.set_image_shift(x=0, y=0)  # Zero the image shift
        # microscope.set_stage_position(alpha=0)  # Zero the stage tilt
        # microscope.unblank_beam()
        # microscope.normalize()

        # Have the user center the particle
        title, message = get_alignment_message()
        display_message(title=title, message=message, microscope=microscope, position="out-of-the-way")

        # Get tilt range info
        while True:
            start_alpha, stop_alpha, step_alpha = get_tilt_range(microscope=microscope)
            if (start_alpha > stop_alpha and step_alpha < 0) or (start_alpha < stop_alpha and step_alpha > 0):
                break
            else:
                warnings.warn("Invalid tilt range, please try again!")

        # Get the required camera parameters
        while True:
            camera_name, integration_time, sampling = get_camera_parameters(microscope=microscope)
            if 0.1 < integration_time < 10:
                break
            else:
                warnings.warn("Invalid integration time. Integration time must be between 0.1 and 10 seconds.")

        # Get the out path (where in the file system to save the results)
        out_file = get_out_file(microscope=microscope)

        # Confirm the user is happy, remove the screen, and start the procedure
        title, message = get_start_message()
        display_message(title=title, message=message, microscope=microscope, position="centered")
        # microscope.remove_screen()

        num_alpha = int((stop_alpha - start_alpha) / step_alpha + 1)
        alpha_arr = np.linspace(start=start_alpha, stop=stop_alpha, num=num_alpha, endpoint=True)

        shifts = obtain_shifts(microscope=microscope, alpha_arr=alpha_arr)

        # Switch to diffraction mode
        # microscope.insert_screen()  # For safety when switching modes
        # Switch back to diffraction mode
        # microscope.remove_screen()

        perform_tilt_series(microscope=microscope, camera=camera_name, integration_time=integration_time,
                            sampling=sampling, alpha_arr=alpha_arr, shifts=shifts, out_file=out_file)

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
