"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import math
import tkinter as tk

from tkinter import ttk
from tkinter import filedialog

from uED.lib.exit_script import exit_script


def get_tilt_range(microscope):
    """
    Prompt the user for the microED alpha tilt range.

    :param microscope: TEMInterface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return:
        float start: The alpha tilt angle at which to start the series acquisition, in degrees.
        float stop: The alpha tilt angle at which to stop the series acquisition, in degrees.
        float step: Angle interval between successive images.
    """

    # Obtain the tilt range limits
    try:
        alpha_min, alpha_max = microscope.get_stage_limits()
    except AttributeError:
        alpha_min, alpha_max = math.nan, math.nan
    except BaseException as e:
        raise e

    root = tk.Tk()
    style = ttk.Style()

    root.title("Please ensure your seat back is straight up and your tray table is stowed.")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    message = ttk.Label(root, text="Please enter the tilt range.", font=(None, 15), justify='center')
    message.grid(column=0, row=0, columnspan=3, padx=5, pady=5)

    max_range_label = ttk.Label(root, text="Maximum allowed tilt range: " + str(alpha_min) + " through "
                                           + str(alpha_max) + " deg", font=(None, 15), justify='center')
    max_range_label.grid(column=0, row=1, columnspan=3, sticky='w', padx=5, pady=5)

    # Add labels for the parameters we are trying to collect.
    start_label = ttk.Label(root, text="Start:")  # Default value
    start_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)
    stop_label = ttk.Label(root, text="Stop:")
    stop_label.grid(column=0, row=3, sticky="e", padx=5, pady=5)
    step_label = ttk.Label(root, text="Step:")
    step_label.grid(column=0, row=4, sticky="e", padx=5, pady=5)

    # Add entry boxes for user input.
    # TODO: Add tkinter validation to Entry widgets
    start = tk.StringVar()
    start_entry_box = ttk.Entry(root, textvariable=start)
    start_entry_box.insert(0, "-10")
    start_entry_box.grid(column=1, row=2, padx=5, pady=5)
    stop = tk.StringVar()
    stop_entry_box = ttk.Entry(root, textvariable=stop)
    stop_entry_box.grid(column=1, row=3, padx=5, pady=5)
    stop_entry_box.insert(0, "10")
    step = tk.StringVar()
    step_entry_box = ttk.Entry(root, textvariable=step)
    step_entry_box.grid(column=1, row=4, padx=5, pady=5)
    step_entry_box.insert(0, "1")

    # Add labels showing the units.
    start_units_label = ttk.Label(root, text="deg")
    start_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)
    stop_units_label = ttk.Label(root, text="deg")
    stop_units_label.grid(column=2, row=3, sticky="w", padx=5, pady=5)
    step_units_label = ttk.Label(root, text="deg")
    step_units_label.grid(column=2, row=4, sticky="w", padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=1, row=5, padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=6, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    return float(start.get()), float(stop.get()), float(step.get())


def get_camera_parameters(microscope):
    """
    Get the camera parameters required for the acquisition series.

    :param microscope: TEMInterface (or None):
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
    # TODO: Obtain option lists directly from the provided microscope object
    camera_options = ['BM-Ceta', 'BM-Falcon']
    sampling_options = ['4k (4096 x 4096)', '2k (2048 x 2048)', '1k (1024 x 1024)', '0.5k (512 x 512)']

    root = tk.Tk()
    style = ttk.Style()

    root.title("Please review the ‘Safety Instructions’ card in the seat pocket in front of you.")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    message = ttk.Label(root, text="Please provide the following acquisition\nparameters:",
                        font=(None, 15), justify='center')
    message.grid(column=0, row=0, columnspan=3, sticky='w', padx=5, pady=5)

    # Add labels for the parameters we are trying to collect.
    camera_label = ttk.Label(root, text="Camera:")
    camera_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)
    integration_time_label = ttk.Label(root, text="Integration Time:")
    integration_time_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)
    sampling_label = ttk.Label(root, text="Sampling:")
    sampling_label.grid(column=0, row=3, sticky="e", padx=5, pady=5)

    # Create widgets for user entry
    # TODO: Add tkinter validation to Entry widgets
    camera = tk.StringVar()
    camera.set(camera_options[0])  # Default to the first option in the list
    camera_option_menu = ttk.OptionMenu(root, camera, camera_options[0], *camera_options)
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

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, columnspan=3, row=4, padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=0, columnspan=3, row=5, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    return str(camera.get()), float(integration_time.get()), str(sampling.get())[0:2]


def get_out_path(microscope):
    """
    Get the out path, this is where we will store the results of the microED sequence.

    :param microscope: TEMInterface (or None):
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
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    # Build a message, letting the user know that we need directory and file name information
    message = ttk.Label(root, text="Where would you like to save the results?", font=(None, 15), justify='center')
    message.grid(column=0, row=0, sticky='w', padx=5, pady=5)

    # Create 'select directory' and 'exit' buttons
    continue_button = ttk.Button(root, text="Select Directory", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=1, padx=5, pady=5)
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
