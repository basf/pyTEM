"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import time
import warnings
import math

import numpy as np
import tkinter as tk

from tkinter import ttk
from tkinter import filedialog
from datetime import date
from typing import Union, Tuple
from pathlib import Path

from pyTEM.Interface import Interface

from pyTEM_scripts.lib.micro_ed.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window
from pyTEM_scripts.lib.micro_ed.exit_script import exit_script
from pyTEM_scripts.lib.micro_ed.messages import get_automated_alignment_message
from pyTEM_scripts.lib.micro_ed.opposite_signs import opposite_signs
from pyTEM_scripts.lib.micro_ed.powspace import powspace


class GetTiltRange:

    def __init__(self, microscope: Union[Interface, None], camera_name: str, verbose: bool = False):
        """
        :param microscope: pyTEM Interface (or None):
           The microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
        :param camera_name: str:
            The name of the camera to use. To reduce beam exposure, we will only be showing the user images taken
             with this camera (rather than unblanking and having the user view through the FluCam screen).
        :param verbose: bool:
            Print out extra information. Useful for debugging.
        """
        self.microscope = microscope
        user_had_the_beam_blank = self._beam_is_blank()
        if not user_had_the_beam_blank:
            # Blank to reduce unnecessary dose
            self._blank_beam()

        # Obtain the tilt range limits
        try:
            self.alpha_min, self.alpha_max = self.microscope.get_stage_limits(axis='alpha')
        except AttributeError:
            warnings.warn("Unable to obtain tilt range limits, assuming -90 to +90 degrees.")
            self.alpha_min, self.alpha_max = -90, 90

        self.verbose = verbose
        self.camera_name = camera_name
        self.font = None  # Default is fine
        self.font_size = 13

        # Since the tilt step is always to be respected, we will get it first
        if self.verbose:
            print("Prompting user for tilt step...")
        while True:
            self.step = self.get_tilt_step()
            if 0.001 <= abs(self.step) <= 40.1:
                break  # Input is okay  # TODO: Add tkinter validation to Entry widget itself
            else:
                warnings.warn("The provided alpha step is unpractical, please try again!")

        if self.verbose:
            print("Prompting user for tilt start...")
        while True:
            self.start = self.get_tilt_start()
            if self.alpha_min < self.start < self.alpha_max and self.start != 0:
                break  # Input is okay  # TODO: Add tkinter validation to Entry widget itself
            else:
                warnings.warn("Invalid alpha start, please try again!")

        # tilt_step and tilt_start should have opposite signs
        if not opposite_signs(self.start, self.step):
            if self.verbose:
                print("Flipping the provided tilt step so it has the opposite sign as the tilt start...")
            self.step = -1 * self.step

        if self.verbose:
            print("Prompting user for tilt stop...")
        self.stop = self.get_tilt_stop()

        if not user_had_the_beam_blank:
            # Leave the blanker as we found it
            self._unblank_beam()

    def get_tilt_step(self) -> float:
        """
        Prompt the user for the microED alpha step (angle interval between successive images).

        :return: float:
            step: alpha angle interval between successive images.
        """
        root = tk.Tk()
        style = ttk.Style()
        window_width = 500

        root.title("At this time, portable electronic devices must be switched into ‘airplane’ mode.")

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please enter the desired tilt step "
                                       "\n(the alpha tilt angle between adjacent images).",
                            font=(self.font, self.font_size), justify='center', wraplength=window_width)
        message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        # Add labels for the parameters we are trying to collect.
        step_label = ttk.Label(root, text="Step:", font=(self.font, self.font_size))
        step_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)

        # Add entry box for user input.
        step = tk.StringVar()
        step_entry_box = ttk.Entry(root, textvariable=step)
        step_entry_box.grid(column=1, row=1, padx=5, pady=5)
        step_entry_box.insert(0, "0.3")

        # Add labels showing the units.
        step_units_label = ttk.Label(root, text="deg", font=(self.font, self.font_size))
        step_units_label.grid(column=2, row=1, sticky="w", padx=5, pady=5)

        # Create submit and exit buttons
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=1, row=2, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=self.microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=1, row=3, padx=5, pady=5)

        style.configure('big.TButton', font=(self.font, self.font_size), foreground="blue4")
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.mainloop()

        return float(step.get())

    def get_tilt_start(self) -> float:
        """
        Prompt the user for the microED alpha start angle (beginning of the tilt range).

        :return: float:
            start_alpha: The alpha tilt angle at which to start the series acquisition, in degrees.
        """
        root = tk.Tk()
        style = ttk.Style()
        window_width = 500
        window_height = 280

        root.title("Please ensure your seat back is straight up and your tray table is stowed.")

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please enter the \u03B1 tilt angle at which to start tilting."
                                       "\n\nPlease confirm, using the 'Test Input' button, that the stage is "
                                       "actually capable of tilting to the this \u03B1, and that the particle remains "
                                       "in the field-of-view and doesn't overlap any other particles before submitting "
                                       "your input."
                                       "\n\nFor reference, our tilt step is \u0394\u03B1=" + str(self.step) + " deg.",
                            wraplength=window_width, font=(self.font, self.font_size), justify='center')
        message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        max_range_label = ttk.Label(root, text="Maximum allowed tilt range: " + str(round(self.alpha_min, 2)) + " to "
                                               + str(round(self.alpha_max, 2)) + " deg", wraplength=window_width,
                                    font=(self.font, self.font_size), justify='center')
        max_range_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)

        # Add labels for the parameters we are trying to collect.
        start_label = ttk.Label(root, text="Start:", font=(self.font, self.font_size))
        start_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)

        # Add entry box for user input.
        start = tk.StringVar()
        start_entry_box = ttk.Entry(root, textvariable=start)
        start_entry_box.grid(column=1, row=2, padx=5, pady=5)
        start_entry_box.insert(0, "-30.0")

        # Add labels showing the units.
        start_units_label = ttk.Label(root, text="deg", font=(self.font, self.font_size))
        start_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)

        def disable_buttons_and_update_alpha():
            """
            Temporarily disable the buttons, update alpha, and then re-enable the buttons.
            This helps prevent problems that arise when one clicks a button while the microscope is working.
            :return: None.
            """
            # Make the buttons 'look' un-clickable.
            test_input_button.config(state=tk.DISABLED)
            test_input_button.update()
            continue_button.config(state=tk.DISABLED)
            continue_button.update()
            exit_button.config(state=tk.DISABLED)
            exit_button.update()

            # Actually make the buttons un-clickable.
            test_input_button.grid_forget()
            continue_button.grid_forget()
            exit_button.grid_forget()

            # Actually update alpha.
            self._update_alpha(float(start.get()))

            # And finally go ahead and restore the buttons.
            test_input_button.config(state=tk.NORMAL)
            test_input_button.grid(column=0, row=3, padx=5, pady=5)
            continue_button.config(state=tk.NORMAL)
            continue_button.grid(column=1, row=3, padx=5, pady=5)
            exit_button.config(state=tk.NORMAL)
            exit_button.grid(column=2, row=3, padx=5, pady=5)

        # Create test, continue, and exit buttons
        test_input_button = ttk.Button(root, text="Test Input", style="big.TButton",
                                       command=disable_buttons_and_update_alpha)
        test_input_button.grid(column=0, row=3, padx=5, pady=5)
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=1, row=3, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=self.microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=2, row=3, padx=5, pady=5)

        style.configure('big.TButton', font=(self.font, self.font_size), foreground="blue4")

        # Make sure the window appears out of the way
        root.geometry("{width}x{height}+{x}+{y}".format(width=window_width, height=window_height,
                                                        x=int(0.65 * root.winfo_screenwidth()),
                                                        y=int(0.025 * root.winfo_screenheight())))

        root.mainloop()

        return float(start.get())

    def get_tilt_stop(self) -> float:
        """
        Prompt the user for the microED alpha stop angle (end of the tilt range).

        :return: float
            stop: The alpha tilt angle at which to stop the series acquisition, in degrees.
        """
        # Try to build a symmetric array of alpha values using the start and step values. Encase the tilt range can't
        #  be divided evenly by the tilt step, the stop value will not be respected.
        alpha_arr = np.arange(self.start, -1 * self.start + self.step, self.step)

        # Suggest the final value in alpha_arr as a legal final stop value.
        default_stop_value = round(alpha_arr[-1], 2)

        root = tk.Tk()
        style = ttk.Style()
        window_width = 500
        window_height = 350

        root.title("Fasten your seat belt by placing the metal fitting into the buckle, and adjust the strap so it "
                   "fits low and tight around your hips.")

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please enter the \u03B1 tilt angle at which to stop tilting."
                                       "\n\nPlease confirm, using the 'Test Input' button, that the stage is "
                                       "capable of tilting to the desired \u03B1, and that the particle remains in the "
                                       "field-of-view and doesn't overlap any other particles before submitting your "
                                       "input."
                                       "\n\nFor reference, our start angle is \u03B1=" + str(self.start) + " deg \n"
                                       "and our tilt step is \u0394\u03B1=" + str(self.step),
                            wraplength=window_width, font=(self.font, self.font_size), justify='center')
        message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        max_range_label = ttk.Label(root, text="Maximum allowed tilt range: " + str(round(self.alpha_min, 2)) + " to "
                                               + str(round(self.alpha_max, 2)) + " deg",
                                    font=(self.font, self.font_size), justify='center')
        max_range_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)

        # Show the user what last stop we will use encase of an uneven division
        def update_uneven_division_label(*args):
            try:
                current_stop = float(stop.get())
            except ValueError:
                current_stop = 0

            if current_stop < self.alpha_min or current_stop > self.alpha_max:
                # The suggested value falls outside the legal tilt range.
                continue_button.config(state=tk.DISABLED)
                txt_ = "Warning: The current stop falls outside of the allowable tilt range. Suggested stop: " \
                       + str(default_stop_value) + "."
                uneven_division_label.configure(foreground="red")

            elif not opposite_signs(self.start, current_stop):
                # The start and stop values must have opposite signs
                continue_button.config(state=tk.DISABLED)
                txt_ = "Warning: The stop value must differ in sign from the start value. Suggested stop: " \
                       + str(default_stop_value) + "."
                uneven_division_label.configure(foreground="red")

            elif current_stop == 0:
                # Zero is not allowed.
                continue_button.config(state=tk.DISABLED)
                txt_ = "Warning: 0 degrees is an illegal stop value. Suggested stop: " + str(default_stop_value) + "."
                uneven_division_label.configure(foreground="red")

            else:
                # Try to build an array of alpha values using the provided start, stop, and step values.
                alpha_arr_ = np.arange(self.start, current_stop + self.step, self.step)

                if math.isclose(a=alpha_arr_[-1], b=current_stop, abs_tol=1e-4) or \
                        math.isclose(a=alpha_arr_[-2], b=current_stop, abs_tol=1e-4):
                    # The input value is okay from a division standpoint.
                    txt_ = ""
                    continue_button.config(state=tk.NORMAL)
                    uneven_division_label.configure(foreground="black")

                else:
                    # The current stop value would result in a tilt range that is not evenly divisible by the tilt
                    #  step, disable the continue button and warn the user.
                    continue_button.config(state=tk.DISABLED)

                    # Suggest the final value in alpha_arr as a legal final stop value.
                    suggested_stop = round(alpha_arr_[-1], 2)
                    txt_ = "Warning: A stop value of " + str(current_stop) + " would provide a tilt interval that " \
                           "doesn't divide evently by \u0394\u03B1=" + str(self.step) + ". Suggested stop: " + \
                           str(suggested_stop) + "."
                    uneven_division_label.configure(foreground="red")

            uneven_division_label.config(text=txt_)

        # Add labels for the parameters we are trying to collect.
        stop_label = ttk.Label(root, text="Stop:", font=(self.font, self.font_size))
        stop_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)

        # Add entry boxes for user input.
        stop = tk.StringVar()
        stop_entry_box = ttk.Entry(root, textvariable=stop)
        stop_entry_box.grid(column=1, row=2, padx=5, pady=5)
        stop_entry_box.insert(0, str(default_stop_value))
        stop.trace('w', update_uneven_division_label)

        # Add labels showing the units.
        stop_units_label = ttk.Label(root, text="deg", font=(self.font, self.font_size))
        stop_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)

        # Add a warning label encase we are unable to evenly divide the provided interval by the provided step and thus
        #  cannot use this step exactly
        uneven_division_label = ttk.Label(root, text="", wraplength=window_width, font=(self.font, self.font_size),
                                          justify='center')
        uneven_division_label.grid(column=0, columnspan=3, row=3, padx=5, pady=5)

        def disable_buttons_and_update_alpha():
            """
            Temporarily disable the buttons, update alpha, and then re-enable the buttons.
            This helps prevent problems that arise when one clicks a button while the microscope is working.
            :return: None.
            """
            # Make the buttons 'look' un-clickable
            test_input_button.config(state=tk.DISABLED)
            test_input_button.update()
            continue_button.config(state=tk.DISABLED)
            continue_button.update()
            exit_button.config(state=tk.DISABLED)
            exit_button.update()

            # Actually make the buttons un-clickable
            test_input_button.grid_forget()
            continue_button.grid_forget()
            exit_button.grid_forget()

            # Actually update alpha.
            self._update_alpha(float(stop.get()))

            # And finally go ahead and restore the buttons.
            test_input_button.config(state=tk.NORMAL)
            test_input_button.grid(column=0, row=4, padx=5, pady=5)
            continue_button.config(state=tk.NORMAL)
            continue_button.grid(column=1, row=4, padx=5, pady=5)
            exit_button.config(state=tk.NORMAL)
            exit_button.grid(column=2, row=4, padx=5, pady=5)

        # Create test, continue, and exit buttons
        test_input_button = ttk.Button(root, text="Test Input", style="big.TButton",
                                       command=disable_buttons_and_update_alpha)
        test_input_button.grid(column=0, row=4, padx=5, pady=5)
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=1, row=4, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=self.microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=2, row=4, padx=5, pady=5)

        style.configure('big.TButton', font=(self.font, self.font_size), foreground="blue4")

        # Make sure the window appears out of the way
        root.geometry("{width}x{height}+{x}+{y}".format(width=window_width, height=window_height,
                                                        x=int(0.65 * root.winfo_screenwidth()),
                                                        y=int(0.025 * root.winfo_screenheight())))
        root.mainloop()

        return float(stop.get())

    # The following helper functions are all Interface wrappers that allow us to test this class without an actual
    #  microscope connection.

    def _update_alpha(self, alpha: float) -> None:
        """
        Helper function to update the alpha tilt angle.
        :param alpha: float:
            The alpha tilt angle that we will move the stage to.
        :return: None.
        """
        if self.microscope is None:
            print("We are not connected to the microscope, but otherwise we would be moving to \u03B1=" + str(alpha)
                  + " and talking a quick picture to show the user.")
            time.sleep(2)  # Pause to visually confirm the buttons disable.

        else:
            if self.verbose:
                print("Moving to \u03B1=" + str(alpha) + "...")
            self.microscope.set_stage_position_alpha(alpha=alpha, speed=0.5)

            # Sometimes, if the allowable tilt range is not properly configured, the user might be able to enter an
            #  angle that is unreachable
            if not math.isclose(alpha, self.microscope.get_stage_position_alpha(), abs_tol=0.01):
                raise Exception("Error: We don't seem to be able to reach the requested tilt angle.")

            # Take a quick acquisition and show it to the user. They can use this to check whether the tilt angle is
            #  okay without having to unblank.
            if self.verbose:
                print("Taking a quick picture to show to the user.")
            quick_acq = self.microscope.acquisition(camera_name=self.camera_name, exposure_time=0.25, sampling='1k',
                                                    blanker_optimization=True, verbose=self.verbose)
            quick_acq.show_image()

    def _blank_beam(self) -> None:
        """
        Helper function to blank the beam.
        :return: None.
        """
        if self.microscope is None:
            print("We are not connected to the microscope, but otherwise would be blanking the beam.")
        else:
            self.microscope.blank_beam()

    def _unblank_beam(self) -> None:
        """
        Helper function to unblank the beam.
        :return: None.
        """
        if self.microscope is None:
            print("We are not connected to the microscope, but otherwise we would be unblanking the beam.")
        else:
            self.microscope.blank_beam()

    def _beam_is_blank(self) -> bool:
        """
        Helper function to see if the beam is blank.
        :return: bool:
            True: Beam is blank.
            False: Beam is unblanked.
        """
        if self.microscope is None:
            print("We are not connected to the microscope, but otherwise we would be returning whether the beam is "
                  "blank.")
            return True  # For testing, just assume the user has the beam blank
        else:
            return self.microscope.beam_is_blank()


def get_tilt_range(microscope: Union[Interface, None], camera_name: str, verbose: bool = False) -> np.array:
    """
    Get the full alpha tilt range from the user.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to test out different tilt angles, and also to return the microscope to a safe
         state if the user exits the script through the 'Quit' button on the message box.
    :param camera_name: str:
        The name of the camera to use. To reduce beam exposure, we will only be showing the user images taken
         with this camera (rather than unblanking and having the user view through the FluCam screen).
    :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return: np.array of floats:
        An array of alpha start-stop values that can be used for a tilt acquisition series.
    """
    tilt_range = GetTiltRange(microscope=microscope, camera_name=camera_name, verbose=verbose)
    alpha_arr = np.arange(tilt_range.start, tilt_range.stop + tilt_range.step, tilt_range.step)

    if math.isclose(a=alpha_arr[-1], b=tilt_range.stop, abs_tol=1e-4):
        # Then all is good, np.arange() worked as we intended.
        pass

    elif math.isclose(a=alpha_arr[-2], b=tilt_range.stop, abs_tol=1e-4):
        # Our array is one element too long (owing to inconsistencies in np.arange() from numerical error, just remove
        #  the last element, and then we are good)
        alpha_arr = np.delete(arr=alpha_arr, obj=-1)

    else:
        # Something is not right, panic!
        exit_script(microscope=microscope, status=1)

    return alpha_arr


def get_acquisition_parameters(microscope: Union[Interface, None]) -> Tuple[str, float, str, bool]:
    """
    Get the camera parameters required for the acquisition series.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return:
        str: camera_name: The name of the camera being used, one of:
            - 'BM-Ceta'
            - 'BM-Falcon'
        float: integration_time: Total exposure time.
        str: sampling: Photo resolution, one of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
        bool: downsample: Whether to decimate the obtained image by a factor of 2.
    """
    try:
        camera_options = microscope.get_available_cameras()
    except AttributeError:
        warnings.warn("Unable to obtain available cameras, assuming 'BM-Ceta' and 'BM-Falcon'.")
        camera_options = ['BM-Ceta', 'BM-Falcon']
    # TODO: Obtain available sampling options directly from the provided microscope object
    sampling_options = ['4k (4096 x 4096)', '2k (2048 x 2048)', '1k (1024 x 1024)', '0.5k (512 x 512)']

    while True:
        root = tk.Tk()
        style = ttk.Style()

        root.title("Please review the ‘Safety Instructions’ card in the seat pocket in front of you.")

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please provide the following acquisition\nparameters:",
                            font=(None, 15), justify='center')
        message.grid(column=0, row=0, columnspan=3, sticky='w', padx=5, pady=5)

        # Add labels for the parameters we are trying to collect.
        camera_label = ttk.Label(root, text="Camera:")
        camera_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)
        integration_time_label = ttk.Label(root, text="Integration Time:")
        integration_time_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)
        binning_label = ttk.Label(root, text="Binning:")
        binning_label.grid(column=0, row=3, sticky="e", padx=5, pady=5)

        # Create widgets for user entry
        camera_name = tk.StringVar()
        camera_option_menu = ttk.OptionMenu(root, camera_name, camera_options[0], *camera_options)
        camera_option_menu.grid(column=1, row=1, padx=5, pady=5)

        integration_time = tk.StringVar()
        integration_time_entry_box = ttk.Entry(root, textvariable=integration_time, width=10)
        integration_time_entry_box.insert(0, "3")  # Default value
        integration_time_entry_box.grid(column=1, row=2, padx=5, pady=5)

        sampling = tk.StringVar()
        sampling.set(sampling_options[0])  # Default to the first option in the list
        sampling_option_menu = ttk.OptionMenu(root, sampling, sampling_options[0], *sampling_options)
        sampling_option_menu.grid(column=1, row=3, padx=5, pady=5)

        # Add label showing integration time units.
        stop_units_label = ttk.Label(root, text="seconds")
        stop_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)

        # Create a checkbutton for whether to downsample.
        downsample = tk.BooleanVar()
        downsample.set(False)
        downsample_checkbutton = ttk.Checkbutton(root, text="Downsample (Bilinear decimation by 2)",
                                                 variable=downsample)
        downsample_checkbutton.grid(column=0, columnspan=3, row=4, padx=5, pady=5)

        # Create continue and exit buttons
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=0, columnspan=3, row=5, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=0, columnspan=3, row=6, padx=5, pady=5)

        style.configure('big.TButton', font=(None, 10), foreground="blue4")
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.mainloop()

        try:
            min_supported_exposure_time, max_supported_exposure_time = \
                microscope.get_exposure_time_range(str(camera_name.get()))
        except AttributeError:
            warnings.warn("Unable to obtain supported exposure time range, assuming 0.1 s to 100 s.")
            min_supported_exposure_time, max_supported_exposure_time = 0.1, 100

        if min_supported_exposure_time < float(integration_time.get()) < max_supported_exposure_time:
            break  # Input is okay  # TODO: Add tkinter validation to Entry widgets themselves
        else:
            warnings.warn("Invalid integration time. Integration time must be between "
                          + str(min_supported_exposure_time) + " and " + str(max_supported_exposure_time)
                          + " seconds.")

    return str(camera_name.get()), float(integration_time.get()), str(sampling.get())[0:2], bool(downsample.get())


def get_out_file(microscope: Union[Interface, None]) -> Tuple[str, bool]:
    """
    Using some Tkinter windows, to get the out file information from the user.

    :param microscope: pyTEM Interface (or None):
            The microscope interface, needed to return the microscope to a safe state if the user exits the script
             through the quit button on the message box.

    :return:
        out_file_path: str:
            The complete out file path, including the file extension.
        save_as_stack: bool:
            True: Save results in a single image stack file.
            False: Save each image in its own individual file.
    """
    return GetOutFile(microscope=microscope).run()


class GetOutFile:
    """
    Helper class to get out file information from the user.
    """

    def __init__(self, microscope: Union[Interface, None]):
        """
        :param microscope: pyTEM Interface (or None):
            The microscope interface, needed to return the microscope to a safe state if the user exits the script
             through the quit button on the message box.
        """
        self.microscope = microscope
        self.out_directory = str(Path.home())

        # Preallocate, put we can't build these string vars until we have a tkinter window.
        self.file_extension_str_var = None
        self.stack_str_var = None

    def run(self) -> Tuple[str, bool]:
        """
        Get the out file path.

        :return:
            out_file_path: str:
                The complete out file path, including the file extension.
            save_as_stack: bool:
                True: Save results in a single image stack file.
                False: Save each image in its own individual file.
        """
        # Create a new window in which the user can fill in the remaining in file path information.
        root = tk.Tk()
        style = ttk.Style()
        max_window_width = 500

        root.title("If you have any questions, please don’t hesitate to ask one of our crew members.")
        add_basf_icon_to_tkinter_window(root)

        def change_out_directory():
            """
            Change/update the out directory.
            :return: None, but the self.out_directory is updated with the new out directory of the users choosing.
            """
            leaf = tk.Tk()
            leaf.title("Please select an out directory.")
            add_basf_icon_to_tkinter_window(leaf)
            leaf.geometry("{width}x{height}".format(width=500, height=leaf.winfo_height()))

            self.out_directory = filedialog.askdirectory()
            path_label.configure(text=self.out_directory + "/")
            leaf.destroy()

        def update_file_extension_options_based_on_stack():
            """
            The list of legal file extensions varies based on whether we are saving as a stack or as a list of
             individual files.
            :return: None, but self.file_extension_str_var is updated.
            """
            if self.stack_str_var.get() == "True":
                # Then we are saving as a stack.
                file_extension_options = ['.mrc', '.tif']
            else:
                # We are saving as multiple single image files, and therefore have more freedom.
                file_extension_options = ['.mrc', '.tif', '.jpeg', '.png']

            # Update the drop-down menu with the new list of options.
            menu = file_extension_menu["menu"]
            file_extension_menu["menu"].delete(0, "end")
            for string in file_extension_options:
                menu.add_command(label=string, command=lambda value=string: self.file_extension_str_var.set(value))

            # Make sure the current file extension is a valid one from the current set of options.
            if self.file_extension_str_var.get() not in file_extension_options:
                self.file_extension_str_var.set(file_extension_options[0])

        complete_out_file_label = ttk.Label(root, text="Where would you like to save the results?", font=(None, 15),
                                            wraplength=max_window_width, justify='center')
        complete_out_file_label.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        # Label the filename box with the out directory
        path_label = ttk.Label(root, text=self.out_directory + "\\", wraplength=max_window_width, justify='center')
        path_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)

        # Create an entry box for the user to enter the file name.
        file_name_str_var = tk.StringVar()
        file_name_entry_box = ttk.Entry(root, textvariable=file_name_str_var)
        file_name_entry_box.insert(0, "micro_ed_" + str(date.today()))  # Default value
        file_name_entry_box.grid(column=1, row=1, padx=5, pady=5)

        # Add a dropdown menu to get the file extension
        self.file_extension_str_var = tk.StringVar()
        file_extension_menu = ttk.OptionMenu(root, self.file_extension_str_var)
        file_extension_menu.grid(column=2, row=1, sticky="w", padx=5, pady=5)

        # Create a button that, when clicked, will update the out_file directory.
        out_file_button = ttk.Button(root, text="Update Out Directory", command=lambda: change_out_directory(),
                                     style="big.TButton")
        out_file_button.grid(column=0, columnspan=3, row=2, padx=5, pady=5)

        # Create a label asking the user if they would like to save the image as a stack or as several individual files.
        complete_out_file_label = ttk.Label(root, text="Would you like to save the results as a multi-image stack "
                                                       "or as multiple single-image files?",
                                            font=(None, 15), wraplength=max_window_width, justify='center')
        complete_out_file_label.grid(column=0, row=3, columnspan=3, padx=5, pady=5)

        # Add radio buttons for single image stack or multiple single-image files.
        self.stack_str_var = tk.StringVar(value="True")
        stack_str_var_radio_button1 = ttk.Radiobutton(root, text="Single Image Stack", variable=self.stack_str_var,
                                                      value="True", style="big.TRadiobutton",
                                                      command=lambda: update_file_extension_options_based_on_stack())
        stack_str_var_radio_button2 = ttk.Radiobutton(root, text="Multiple Single Image Files", value="False",
                                                      style="big.TRadiobutton", variable=self.stack_str_var,
                                                      command=lambda: update_file_extension_options_based_on_stack())
        stack_str_var_radio_button1.grid(column=0, columnspan=3, row=4, pady=(5, 0))
        stack_str_var_radio_button2.grid(column=0, columnspan=3, row=5, pady=(0, 15))

        # Add continue and quit buttons.
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=0, columnspan=3, row=6, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=self.microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=0, columnspan=3, row=7, padx=5, pady=5)

        style.configure('big.TButton', font=(None, 10), foreground="blue4")
        style.configure('big.TRadiobutton', font=(None, 11))

        # Just to make sure dropdown file extension is consistent with whether we are saving as a stack.
        update_file_extension_options_based_on_stack()

        root.eval('tk::PlaceWindow . center')  # Center the window on the screen.

        root.mainloop()

        # Build and return the complete path
        out_path = self.out_directory + "/" + str(file_name_str_var.get()) + str(self.file_extension_str_var.get())
        if self.stack_str_var.get() == "True":
            return out_path, True
        else:
            return out_path, False


def shift_correction_info(microscope: Union[Interface, None], tilt_start: float, tilt_stop: float,
                          exposure_time: float) -> Tuple[bool, np.array]:
    """
    The MicroED script supports automated image alignment using the hyperspy library (phase correlation image shift
     detection functionality). However, it is possible the user may want to proceed without enabling this functionality.

     Find out if the user would like to use automated shift correction, and if so, how many calibration images they
      would like to take. The more correctional images taken, the more accurate the image shift correction will be,
      however, taking these calibration images will increase the sample exposure time.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.
    :param tilt_start: float:
        The alpha tilt angle at which to start the tilt series (where we start obtaining correctional shifts).
    :param tilt_stop: float:
        The alpha tilt angle at which to stop the tilt series (where we stop obtaining automatic shifts).
    :param exposure_time: float:
        The exposure time, in seconds, to use for a single shift-determination image.

    :return: bool:
        use_shift_corrections: bool: Whether to use automatic shift corrections or not.
            True: Use automatic alignment.
            False: Proceed without automated image alignment.
        samples: np.array: The angles at which we take calibration images.
            If we are using automatic alignment, then this is a numpy array of alpha angles at which we need to take
             calibration images.
            If we are proceeding without automated image alignment, then samples is None.
    """
    window_width = 650
    label_font = (None, 13)
    spacing = "exponential"

    root = tk.Tk()
    style = ttk.Style()

    # Display a message informing the user about the automated image alignment functionality.
    title, message = get_automated_alignment_message()
    root.title(title)
    add_basf_icon_to_tkinter_window(root)
    message_label = ttk.Label(root, text=message, wraplength=window_width, font=label_font, justify='center')
    message_label.grid(column=0, columnspan=2, row=0, sticky='w', padx=5, pady=5)

    # Deactivate all the other entry widgets whenever the user unchecks the use_automated_alignment button.
    def deactivate_other_entry_widgets():
        if use_automated_alignment.get() == 1:
            num_correctional_images_entry_box.config(state=tk.NORMAL)
        else:
            num_correctional_images_entry_box.config(state=tk.DISABLED)

    # Create a checkbutton for whether to proceed with automated image alignment.
    use_automated_alignment = tk.BooleanVar()
    use_automated_alignment.set(True)
    use_automated_alignment_button = ttk.Checkbutton(root, text="Proceed with Automated Image Alignment",
                                                     variable=use_automated_alignment, style="big.TCheckbutton",
                                                     command=deactivate_other_entry_widgets)
    use_automated_alignment_button.grid(column=0, columnspan=2, row=1, padx=5, pady=5)

    num_correctional_images_label = ttk.Label(root, text="Number of Calibration Images to Take: ", font=label_font)
    num_correctional_images_label.grid(column=0, row=2, sticky="e", pady=5)

    # Show the user how much exposure will result from the current number of correctional images.
    def update_total_exposure_label(*args):
        try:
            num_correctional_images_ = int(num_correctional_images_string_var.get())
        except ValueError:
            num_correctional_images_ = 0

        exposure_time_label1.config(text="Total exposure time required for automated image alignment with "
                                    + str(num_correctional_images_) + " correctional images: ")

        if num_correctional_images_ < 3:
            # This conditional also fires when we clear the entry box.
            exposure_time_label2.config(text="We cannot perform automatic image alignment with any fewer than 3 "
                                             "correctional images.")
            exposure_time_label2.configure(foreground="red")

            calibration_samples_label.config(text="")

        else:
            samples_ = compute_sample_arr(tilt_start=tilt_start, tilt_stop=tilt_stop, spacing=spacing,
                                          num_correctional_images=num_correctional_images_)
            total_exposure_time_required_ = num_correctional_images_ * exposure_time

            exposure_time_label2.config(text="~" + str(round(total_exposure_time_required_, 2)) + " seconds")
            exposure_time_label2.configure(foreground="black")

            calibration_samples_label.config(text="Calibration Images will be taken at the following tilt "
                                                  "angles:\n" + str(np.round(samples_, 2)))

    # Provide a text box, in which the user can entry the number of correctional images to take.
    num_correctional_images_string_var = tk.StringVar()
    num_correctional_images_entry_box = ttk.Entry(root, textvariable=num_correctional_images_string_var, width=5)
    default_num_correctional_images = 11
    num_correctional_images_entry_box.insert(0, str(default_num_correctional_images))  # Insert default value.
    num_correctional_images_entry_box.grid(column=1, sticky='w', row=2, pady=5)
    num_correctional_images_string_var.trace('w', update_total_exposure_label)

    info_label = ttk.Label(root, font=label_font, wraplength=window_width, justify='center',
                           text="The more correctional images taken, the better the results but also "
                                "the greater the sample dose. For reference, the selected tilt range is \u03B1="
                                + str(round(tilt_start, 2)) + " to " + str(round(tilt_stop, 2)) + " degrees.")
    info_label.grid(column=0, columnspan=2, row=3, padx=5, pady=5)

    num_correctional_images = int(num_correctional_images_string_var.get())
    samples = compute_sample_arr(tilt_start=tilt_start, tilt_stop=tilt_stop, spacing=spacing,
                                 num_correctional_images=num_correctional_images)
    total_exposure_time_required = num_correctional_images * exposure_time

    exposure_time_label1 = ttk.Label(root, text="Total exposure time required for automated image alignment with "
                                                + str(num_correctional_images) + " correctional images: ",
                                     font=label_font, justify='center', wraplength=window_width)
    exposure_time_label1.grid(column=0, columnspan=2, row=4, padx=5, pady=(5, 0))

    exposure_time_label2 = ttk.Label(root, text="~" + str(round(total_exposure_time_required, 2)) + " seconds",
                                     font=label_font + ('bold',), justify='center', wraplength=window_width)
    exposure_time_label2.grid(column=0, columnspan=2, row=5, padx=5, pady=(0, 5))

    calibration_samples_label = ttk.Label(root, text="Calibration Images will be taken at the following tilt "
                                                     "angles:\n" + str(np.round(samples, 2)),
                                          font=label_font, wraplength=window_width, justify='center')
    calibration_samples_label.grid(column=0, columnspan=2, row=6, padx=5, pady=5)

    # Provide a label explaining that we will linear interpolate the required compensatory image shifts between
    #  calibration images.
    interpolation_explanation_label = ttk.Label(root, text="Any additional compensatory image shifts will be linearly "
                                                           "interpolated locally from the bracketing samples.",
                                                font=label_font, wraplength=window_width, justify='center')
    interpolation_explanation_label.grid(column=0, columnspan=2, row=7, padx=5, pady=5)

    # Create a 'Continue' button that the user can click to proceed with automated image alignment
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, columnspan=2, row=8, padx=5, pady=5)

    # Create an 'exit' button that the user can use to exit the script.
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=0, columnspan=2, row=9, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TRadiobutton', font=(None, 11))

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    if use_automated_alignment.get():
        # The user has requested we proceed with automated image alignment functionality
        if int(num_correctional_images_string_var.get()) < 3:
            # Then the user requested too few correctional images, so we will just proceed without automated image
            #  alignment functionality
            warnings.warn("Cannot perform automated image alignment with less than 3 samples, proceeding without "
                          "automated image shift functionality.")
            return False, None

        else:
            # Proceed with automated image alignment functionality with the number of calibration images request by
            #  the user.
            samples = compute_sample_arr(tilt_start=tilt_start, tilt_stop=tilt_stop, spacing="exponential",
                                         num_correctional_images=int(num_correctional_images_string_var.get()))
            return True, samples

    else:
        # We are proceeding without automated image alignment functionality
        return False, None


def compute_sample_arr(tilt_start: float, tilt_stop: float, num_correctional_images: int,
                       spacing: str = 'linear', verbose: bool = False) -> np.array:
    """
    Compute and return the array of tilt angles at which we will perform calibration images (samples), along with the
     largest step between any two values in samples.

    :param tilt_start: float:
        The alpha tilt angle at which to start the tilt series (where we start obtaining correctional shifts).
    :param tilt_stop: float:
        The alpha tilt angle at which to stop the tilt series (where we stop obtaining automatic shifts).
    :param num_correctional_images: int:
        The number of calibration images you would like to take (number of calibration angles you would like to use).
    :param spacing: string (optional; default is 'linear'):
        The spacing method you would like to use. One of:
            - 'linear': Evenly spaced values.
            - 'exponential': Exponentially spaced values. To provide for tilting experiments where you experience more
                drift at higher tilt angles, this returns exponentially spaced values that are spaced increasingly
                closer together the farther you get from 0.
    :param verbose: bool:
        Print out extra information. Useful for debugging.

    :return:
        samples: np.array:
            The angles at which we need to take calibration images.
    """
    if num_correctional_images < 3:
        raise Exception("Error: compute_sample_arr() requires at least 3 calibration angles.")

    # Just to be sure...
    spacing = str(spacing).lower()
    num_correctional_images = int(num_correctional_images)

    if spacing == "linear":
        samples = np.linspace(start=tilt_start, stop=tilt_stop, num=num_correctional_images, endpoint=True)

    elif spacing == "exponential":
        # This implementation uses powspace() with an exponent <1 to build an array where the values are spaced
        #  increasingly closer together the farther you get from 0.
        power = 0.7
        # Because powspace() only allows positive start/stop values, we have to break our interval across 0 and compute
        #  the positive and negative samples separately.

        # Because each sign will have a 0. Notice this means that num >=4 (allowing at least 2 values for the negative
        #  samples and two values for the positive samples)
        num = num_correctional_images + 1

        if tilt_start < 0:
            # Then negative samples go from 0 -> abs(start), and positive from 0 -> stop.
            num_negative_samples = int(abs(tilt_start) / (tilt_stop - tilt_start) * num)
            num_positive_samples = num - num_negative_samples

            # Each sign range requires at least 2 samples (0 and the end value).
            if num_negative_samples < 2:
                num_negative_samples = 2
                num_positive_samples = num - num_negative_samples
            if num_positive_samples < 2:
                num_positive_samples = 2
                num_negative_samples = num - num_positive_samples

            negative_samples = -1 * powspace(start=0, stop=abs(tilt_start), power=power, num=num_negative_samples)
            positive_samples = powspace(start=0, stop=tilt_stop, power=power, num=num_positive_samples)

        else:
            # Then negative samples go from 0 -> abs(stop), and positive from 0 -> start
            num_positive_samples = int(tilt_start / (tilt_start - tilt_stop) * num)
            num_negative_samples = num - num_positive_samples

            # Again, each sign range requires at least 2 samples (0 and the end value).
            if num_negative_samples < 2:
                num_negative_samples = 2
                num_positive_samples = num - num_negative_samples
            if num_positive_samples < 2:
                num_positive_samples = 2
                num_negative_samples = num - num_positive_samples

            negative_samples = -1 * powspace(start=0, stop=abs(tilt_stop), power=power, num=num_negative_samples)
            positive_samples = powspace(start=0, stop=tilt_start, power=power, num=num_positive_samples)

        samples = np.round(np.concatenate((negative_samples, positive_samples)), 5)
        samples = np.unique(np.sort(samples))  # Removes the extra zero(s).

        if verbose:
            print("\nNumber of negative samples: " + str(num_negative_samples))
            print("Number of positive samples: " + str(num_positive_samples))

            print("\nNegative samples: " + str(negative_samples))
            print("Positive samples: " + str(positive_samples))

    else:
        raise Exception("Error: spacing strategy (" + spacing + ") not recognized.")

    return samples


if __name__ == "__main__":
    """
    Testing.
    """

    # Try to connect to a microscope
    try:
        scope = Interface()
        print("Microscope connection established successfully.")
    except BaseException as e:
        warnings.warn("MicroED was unable to connect to a microscope, try (re)connecting with MicroED.connect(). "
                      "\nError details:" + str(e))
        scope = None

    """ Test getting tilt range info """
    # # Restore default numpy print options
    # # np.set_printoptions(edgeitems=3, infstr='inf', linewidth=75, nanstr='nan', precision=8, suppress=False,
    # #                     threshold=1000, formatter=None)
    # arr = get_tilt_range(microscope=scope, camera_name="BM-Ceta", verbose=True)
    # print("Here is the final alpha array received from get_tilt_range():")
    # print(arr)

    """ Test getting camera parameters """
    # camera_name_, integration_time_, sampling_, downsample_ = get_acquisition_parameters(microscope=scope)
    # print("Camera name: " + camera_name_)
    # print("Integration time: " + str(integration_time_))
    # print("Sampling: " + sampling_)
    # print("Downsampling: " + str(downsample_))

    """ Test getting out file """
    import os
    out_file__, save_as_stack__ = get_out_file(None)
    print("Full out file: " + str(out_file__))
    file_name_base, file_extension = os.path.splitext(out_file__)
    print("File name: " + str(file_name_base))
    print("File extension: " + str(file_extension))
    print("Save as stack: " + str(save_as_stack__))

    """ Test getting shift correction samples """
    # use_shift_corrections, samples__ = shift_correction_info(microscope=scope, tilt_start=35, tilt_stop=-5,
    #                                                          exposure_time=0.25)
    # print("Use shift: " + str(use_shift_corrections))
    # print("Samples: " + str(samples__))

    # samples__ = compute_sample_arr(tilt_start=45, tilt_stop=-30, num_correctional_images=12,
    #                                spacing='exponential', verbose=True)
    # print("\n" + str(samples__))
