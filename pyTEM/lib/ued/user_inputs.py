"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
import sys
import warnings
import tkinter as tk

from tkinter import ttk
from tkinter import filedialog
from datetime import date
from typing import Union, Tuple

import numpy as np

# Add the pyTEM package directory to path
package_directory = pathlib.Path().resolve().parent.resolve().parent.resolve().parent.resolve()
sys.path.append(str(package_directory))
try:
    from pyTEM.Interface import Interface
    from pyTEM.lib.ued.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window
    from pyTEM.lib.ued.exit_script import exit_script
    from pyTEM.lib.ued.messages import automated_alignment_message, get_welcome_message, display_message, \
    get_alignment_message
    from pyTEM.lib.ued.opposite_signs import opposite_signs
except Exception as ImportException:
    raise ImportException


class GetTiltRange:

    def __init__(self, microscope: Union[Interface, None]):
        """
        :param microscope: pyTEM Interface (or None):
           The microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
        """
        self.microscope = microscope

        # Obtain the tilt range limits
        try:
            self.alpha_min, self.alpha_max = self.microscope.get_stage_limits(axis='alpha')
        except AttributeError:
            warnings.warn("Unable to obtain tilt range limits, assuming -90 to +90 degrees.")
            self.alpha_min, self.alpha_max = -90, 90

        self.font = None  # Default is fine
        self.font_size = 13

        while True:
            self.start = self.get_tilt_start()
            if self.alpha_min < self.start < self.alpha_max and self.start != 0:
                break  # Input is okay  # TODO: Add tkinter validation to Entry widget itself
            else:
                warnings.warn("Invalid alpha start, please try again!")

        while True:
            self.stop = self.get_tilt_stop()
            if self.alpha_min < self.stop < self.alpha_max and self.stop != 0 and opposite_signs(self.start, self.stop):
                break  # Input is okay  # TODO: Add tkinter validation to Entry widget itself
            else:
                warnings.warn("Invalid alpha stop, please try again!")

        while True:
            self.step = self.get_tilt_step()
            if abs(self.step) <= abs(self.start - self.stop) / 2:
                break  # Input is okay  # TODO: Add tkinter validation to Entry widget itself
            else:
                warnings.warn("Invalid alpha step, please try again!")

        # tilt_step and tilt_start should have opposite signs
        if not opposite_signs(self.start, self.step):
            self.step = -1 * self.step

    def get_tilt_start(self) -> float:
        """
        Prompt the user for the microED alpha start angle (beginning of the tilt range).

        :return: float:
            start_alpha: The alpha tilt angle at which to start the series acquisition, in degrees.
        """
        root = tk.Tk()
        style = ttk.Style()
        window_width = 500
        window_height = 235

        root.title("Please ensure your seat back is straight up and your tray table is stowed.")

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please enter the \u03B1 tilt angle at which to start tilting."
                                       "\n\nPlease confirm, using the 'Test Input' button, that the stage is "
                                       "capable of tilting to the this \u03B1, and that the particle remains in the "
                                       "field-of-view and doesn't overlap any other particles before submitting your "
                                       "input.",
                            wraplength=window_width, font=(self.font, self.font_size), justify='center')
        message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        max_range_label = ttk.Label(root, text="Maximum allowed tilt range: " + str(round(self.alpha_min, 2)) + " - "
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

        # Create test, continue, and exit buttons
        test_button = ttk.Button(root, text="Test Input", style="big.TButton",
                                 command=lambda: self._update_alpha(alpha=float(start.get())))
        test_button.grid(column=0, row=3, padx=5, pady=5)
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
        root = tk.Tk()
        style = ttk.Style()
        window_width = 500
        window_height = 275

        root.title("Fasten your seat belt by placing the metal fitting into the buckle, and adjust the strap so it "
                   "fits low and tight around your hips.")

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please enter the \u03B1 tilt angle at which to stop tilting."
                                       "\n\nPlease confirm, using the 'Test Input' button, that the stage is "
                                       "capable of tilting to the desired \u03B1, and that the particle remains in the "
                                       "field-of-view and doesn't overlap any other particles before submitting your "
                                       "input."
                                       "\n\nFor reference, our start angle is \u03B1=" + str(self.start) + " deg.",
                            wraplength=window_width, font=(self.font, self.font_size), justify='center')
        message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        max_range_label = ttk.Label(root, text="Maximum allowed tilt range: " + str(round(self.alpha_min, 2)) + " - "
                                               + str(round(self.alpha_max, 2)) + " deg",
                                    font=(self.font, self.font_size), justify='center')
        max_range_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)

        # Add labels for the parameters we are trying to collect.
        stop_label = ttk.Label(root, text="Stop:", font=(self.font, self.font_size))
        stop_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)

        # Add entry boxes for user input.
        stop = tk.StringVar()
        stop_entry_box = ttk.Entry(root, textvariable=stop)
        stop_entry_box.grid(column=1, row=2, padx=5, pady=5)
        stop_entry_box.insert(0, str(-1 * self.start))

        # Add labels showing the units.
        stop_units_label = ttk.Label(root, text="deg", font=(self.font, self.font_size))
        stop_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)

        # Create test, continue, and exit buttons
        test_button = ttk.Button(root, text="Test Input", style="big.TButton",
                                 command=lambda: self._update_alpha(alpha=float(stop.get())))
        test_button.grid(column=0, row=3, padx=5, pady=5)
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

        return float(stop.get())

    def _update_alpha(self, alpha: float) -> None:
        """
        Helper function to update the alpha tilt angle as the user searches for a valid alpha tilt range.
        :param alpha: float:
            The alpha tilt angle that we will move the stage to.
        :return: None.
        """
        if self.microscope is None:
            print("We are not connected to the microscope, but otherwise would be moving to \u03B1=" + str(alpha))
        else:
            self.microscope.set_stage_position_alpha(alpha=alpha, speed=0.5)

    def get_tilt_step(self) -> float:
        """
        Prompt the user for the microED alpha step (angle interval between successive images).

        :return: float:
            step: alpha angle interval between successive images.
        """
        root = tk.Tk()
        style = ttk.Style()
        window_width = 500

        root.title("At this time, portable electronic devices must be switched into ‘airplane’ mode.")  # TODO.

        add_basf_icon_to_tkinter_window(root)

        message = ttk.Label(root, text="Please enter the tilt step "
                                       "\n(the alpha tilt angle between adjacent images)."
                                       "\n\nFor reference, our tilt range is \u03B1=" + str(self.start) + " to "
                                       + str(self.stop) + " deg.",
                            font=(self.font, self.font_size), justify='center', wraplength=window_width)
        message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

        # Add labels for the parameters we are trying to collect.
        step_label = ttk.Label(root, text="Step:", font=(self.font, self.font_size))
        step_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)

        # Add entry boxes for user input.
        step = tk.StringVar()
        step_entry_box = ttk.Entry(root, textvariable=step)
        step_entry_box.grid(column=1, row=1, padx=5, pady=5)
        step_entry_box.insert(0, "0.1")

        # Add labels showing the units.
        step_units_label = ttk.Label(root, text="deg", font=(self.font, self.font_size))
        step_units_label.grid(column=2, row=1, sticky="w", padx=5, pady=5)

        # Create continue and exit buttons
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=1, row=2, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=self.microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=1, row=3, padx=5, pady=5)

        style.configure('big.TButton', font=(self.font, self.font_size), foreground="blue4")
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.mainloop()

        return float(step.get())


def get_tilt_range(microscope: Union[Interface, None]) -> np.array:
    """
    Get the full alpha tilt range from the user.

    :param microscope: pyTEM TEMInterface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: np.array of floats:
        An array of alpha start-stop values that can be used for a tilt acquisition series.
    """
    tilt_range = GetTiltRange(microscope=microscope)

    num_alpha = int((tilt_range.stop - tilt_range.start) / tilt_range.step + 1)
    alpha_arr = np.linspace(start=tilt_range.start, stop=tilt_range.stop, num=num_alpha, endpoint=True)

    return alpha_arr


def get_camera_parameters(microscope: Union[Interface, None]) -> Tuple[str, float, str]:
    """
    Get the camera parameters required for the acquisition series.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return:
        str: camera: The name of the camera being used, one of:
            - 'BM-Ceta'
            - 'BM-Falcon'
        float: integration_time: Total exposure time.
        str: sampling: Photo resolution, one of:
            - '4k' for 4k images (4096 x 4096; sampling=1)
            - '2k' for 2k images (2048 x 2048; sampling=2)
            - '1k' for 1k images (1024 x 1024; sampling=3)
            - '0.5k' for 05.k images (512 x 512; sampling=8)
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
        binning_label = ttk.Label(root, text="binning:")
        binning_label.grid(column=0, row=3, sticky="e", padx=5, pady=5)

        # Create widgets for user entry
        camera = tk.StringVar()
        camera.set(camera_options[0])  # Default to the first option in the list
        camera_option_menu = ttk.OptionMenu(root, camera, camera_options[0], *camera_options)
        camera_option_menu.grid(column=1, row=1, padx=5, pady=5)

        integration_time = tk.StringVar()
        integration_time_entry_box = ttk.Entry(root, textvariable=integration_time, width=10)
        integration_time_entry_box.insert(0, "3")  # Default value
        integration_time_entry_box.grid(column=1, row=2, padx=5, pady=5)

        binning = tk.StringVar()
        binning.set(sampling_options[0])  # Default to the first option in the list
        binning_option_menu = ttk.OptionMenu(root, binning, sampling_options[0], *sampling_options)
        binning_option_menu.grid(column=1, row=3, padx=5, pady=5)

        # Add label showing integration time units.
        stop_units_label = ttk.Label(root, text="seconds")
        stop_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)

        # Create continue and exit buttons
        continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(column=0, columnspan=3, row=4, padx=5, pady=5)
        exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                                 style="big.TButton")
        exit_button.grid(column=0, columnspan=3, row=5, padx=5, pady=5)

        style.configure('big.TButton', font=(None, 10), foreground="blue4")
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.mainloop()

        try:
            min_supported_exposure_time, max_supported_exposure_time = microscope.get_exposure_time_range(str(camera.get()))
        except AttributeError:
            warnings.warn("Unable to obtain supported exposure time range, assuming 0.1 s to 100 s.")
            min_supported_exposure_time, max_supported_exposure_time = 0.1, 100

        if min_supported_exposure_time < float(integration_time.get()) < max_supported_exposure_time:
            break  # Input is okay  # TODO: Add tkinter validation to Entry widgets themselves
        else:
            warnings.warn("Invalid integration time. Integration time must be between "
                          + str(min_supported_exposure_time) + " and " + str(max_supported_exposure_time)
                          + " seconds.")

    return str(camera.get()), float(integration_time.get()), str(binning.get())[0:2]


def get_out_file(microscope: Union[Interface, None]) -> str:
    """
    Get the out file, this is where we will store the results of the microED sequence.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: str:
        The out directory where the microED acquisition results will be saved.
    """

    # First we will create a pop-up warning the user they are about to have to select an out directory.
    root = tk.Tk()
    style = ttk.Style()

    root.title("Take a moment to locate the exit nearest you keeping in mind that the closest usable exit may "
               "be located behind you.")
    add_basf_icon_to_tkinter_window(root)

    # Build a message, letting the user know that we need directory and file name information
    message = ttk.Label(root, text="Where would you like to save the results?", font=(None, 15), justify='center')
    message.grid(column=0, row=0, sticky='w', padx=5, pady=5)

    # Create 'select directory' and 'exit' buttons
    select_directory_button = ttk.Button(root, text="Select Directory", command=lambda: root.destroy(),
                                         style="big.TButton")
    select_directory_button.grid(column=0, row=1, padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=0, row=2, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    root.mainloop()

    # Make the user select an out directory
    root = tk.Tk()
    root.title("A life vest is located under or between your seat.")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon
    root.geometry("{width}x{height}".format(width=500, height=root.winfo_height()))
    root.directory = filedialog.askdirectory()
    out_dir = str(root.directory)

    root.destroy()

    # Make the user select a file-name
    root = tk.Tk()
    style = ttk.Style()

    root.title("As a reminder, smoking is not permitted in any area of the aircraft, including the lavatories.")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    message = ttk.Label(root, text="Please complete the out file path:", font=(None, 15))
    message.grid(column=0, row=0, columnspan=3, sticky='w', padx=5, pady=5)

    # Label the filename box with the out directory
    camera_label = ttk.Label(root, text=out_dir + "/")
    camera_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)

    file_name = tk.StringVar()
    file_name_entry_box = ttk.Entry(root, textvariable=file_name)
    file_name_entry_box.insert(0, "MicroED_" + str(date.today()))  # Default value
    file_name_entry_box.grid(column=1, row=1, padx=5, pady=5)

    # Add label showing the file extension
    stop_units_label = ttk.Label(root, text=".tif")  # TODO: Figure out which file extension makes the most sense
    stop_units_label.grid(column=2, row=1, sticky="w", padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, columnspan=2, row=2, padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=0, columnspan=2, row=3, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    # Build and return the complete path
    out_path = out_dir + str(file_name.get()) + ".tif"
    return out_path


def have_user_center_particle(microscope: Union[Interface, None]) -> None:
    """
    Have the user center the particle.

    :param microscope: pyTEM TEMInterface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: None.
    """
    while True:
        title, message = get_alignment_message()
        display_message(title=title, message=message, microscope=microscope, position="out-of-the-way")

        # Confirm that we are in the correct magnification range (at the time of writing image shift is only
        #  calibrated for magnifications in the SA range)
        if microscope.get_projection_submode() == "SA":
            break  # Magnification is okay
        else:
            warnings.warn("Currently we are in the " + str(microscope.get_projection_submode())
                          + " magnification range, please select a magnification in the SA range.")
    return None


def use_shift_correction(microscope: Union[Interface, None]) -> bool:
    """
    The MicroED script supports automated image alignment using the hyperspy library (phase correlation image shift
     detection functionality). However, it is possible the user may want to proceed without enabling this functionality.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: bool:
        True: Use automatic alignment.
        False: Proceed without automated image alignment.
    """

    # First we will create a pop-up warning the user they are about to have to select an out directory.
    root = tk.Tk()
    style = ttk.Style()
    window_width = 650

    title, message = automated_alignment_message()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    # Display the automated alignment message, informing the user of the automated image alignment functionality
    message_label = ttk.Label(root, text=message, wraplength=window_width, font=(None, 15), justify='center')
    message_label.grid(column=0, row=0, sticky='w', padx=5, pady=5)

    # Create a checkbutton that the user can use to
    use_automated_alignment = tk.BooleanVar()
    use_automated_alignment.set(True)
    use_automated_alignment_button = ttk.Checkbutton(root, text="Proceed with Automated Image Alignment",
                                                     variable=use_automated_alignment, style="big.TCheckbutton")
    use_automated_alignment_button.grid(column=0, row=1, padx=5, pady=5)

    # Create a 'Continue' button that the user can click to proceed with automated image alignment
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=2, padx=5, pady=5)

    # Create an 'exit' button that the user can use to exit the script.
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=0, row=3, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    return use_automated_alignment.get()


if __name__ == "__main__":

    """ Display a welcome message """
    # from pyTEM.lib.ued.messages import get_welcome_message, display_message
    # title_, message_ = get_welcome_message()
    # display_message(title=title_, message=message_, microscope=None, position="centered")

    """ Test getting tilt range info """
    # arr = get_tilt_range(microscope=None)
    # print(arr)

    """ Test getting camera parameters"""
    camera_name, integration_time, sampling = get_camera_parameters(microscope=None)
    print("Camera name: " + camera_name)
    print("Integration time: " + str(integration_time))
    print("Sampling: " + sampling)

    # get_out_file(None)
    # # Get tilt range info
    # start_alpha, stop_alpha, step_alpha = get_tilt_range(microscope=None)
    # while True:
    #     # Check to make sure that step_alpha has the right sign
    #     if (start_alpha > stop_alpha and step_alpha < 0) or (start_alpha < stop_alpha and step_alpha > 0):
    #         # Check to make sure the tilt range includes 0
    #         if (start_alpha > 0 and stop_alpha < 0) or (start_alpha < 0 and stop_alpha > 0):
    #             break  # Input is okay
    #     else:
    #         warnings.warn("Invalid tilt range, please try again!")
