import sys
import tkinter as tk
import warnings
from tkinter import ttk
from tkinter import filedialog

# from Interface.TEMInterface import TEMInterface


def get_welcome_message():
    """
    :return: str: Welcome message.
    """
    title = "Willkommen!"
    message = "Welcome to BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging " \
              "script. MicroED allows fast, high resolution 3D structure determination of small chemical " \
              "compounds biological macromolecules! You can exit the script any time using the exit buttons on the " \
              "pop-up message boxes, or by hitting Ctrl-C on your keyboard. " \
              "\n\nPlease click the continue button to get started!"
    return title, message


def get_initialization_message():
    """
    :return: str: Initialization message.
    """
    title = "Initialization"
    message = "In order to initialize the microscope for MicroED, we are now going to: " \
              "\n - Connect to the microscope." \
              "\n - Make sure the microscope is in 'TEM' mode." \
              "\n - Make sure the microscope is in 'Imaging' mode. " \
              "\n - Zero the image shift." \
              "\n - Zero the \u03B1 tilt." \
              "\n - Normalize all lenses." \
              "\n\n To start this initialization procedure, please click the continue button."
    return title, message


def get_alignment_message():
    """
    :return: str: Initialization message
    """
    title = "Alignment"
    message = "Using the microscope control panel, please select the desired magnification and center the microscope " \
              "on the particle of interest. " \
              "\n\nPlease do not adjust the stage tilt nor the image shift. " \
              "\n\nOnce the particle is centered, please click the continue button."
    return title, message


def exit_script(microscope, status):
    """
    Exit the script.
    :param microscope: 
    :param status: int:
    Exit status, one of:
        -1: Failure
        0: Success
        1: Early exit (script not yet complete)
    """""
    if microscope is not None:
        warnings.warn("Returning the microscope to a safe state...")
        microscope.make_safe()
    sys.exit(status)


def display_message(title, message, microscope, position="centered"):
    """
    Display a simple message box with 'continue' and 'exit' buttons at the bottom.

    # TODO: Improve message box aesthetics.

    :param message: str:
        The message to display.
    :param title: str:
        Message box title.

    :param microscope: TEMInterface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :param position: str:
        The position of the message box, one of:
        - "centered" (useful when you need the users full attention, and don't want them fiddling around with the
                      microscope in the background)
        - "out-of-the-way" (useful when you need the user to adjust the microscope in the background before confirming)

    :return: None.
    """
    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    window_width = 650
    message = ttk.Label(root, text=message, wraplength=window_width, font=(None, 15))
    message.configure(anchor="center")
    message.grid(column=0, columnspan=2, row=0, padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=1, sticky="e", padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=1, sticky="w", padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    if position == "centered":
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    elif position == "out-of-the-way":
        pass  # TODO: Position the window somewhere out of the way. Probably in the upper right-hand corner.

    else:
        raise Exception("Display message position '" + str(position) + "' not recognized.")

    root.mainloop()


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
    root = tk.Tk()
    style = ttk.Style()

    root.title("Tilt Range")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    message = ttk.Label(root, text="Please enter the tilt range:", font=(None, 15))
    message.grid(column=0, row=0, columnspan=3, sticky='w', padx=5, pady=5)

    # Add labels for the parameters we are trying to collect.
    start_label = ttk.Label(root, text="Start:")
    start_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)
    stop_label = ttk.Label(root, text="Stop:")
    stop_label.grid(column=0, row=2, sticky="e", padx=5, pady=5)
    step_label = ttk.Label(root, text="Step:")
    step_label.grid(column=0, row=3, sticky="e", padx=5, pady=5)

    # Add entry boxes for user input.
    # TODO: Add tkinter validation to Entry widgets
    start = tk.StringVar()
    start_entrybox = ttk.Entry(root, textvariable=start)
    start_entrybox.grid(column=1, row=1, padx=5, pady=5)
    stop = tk.StringVar()
    stop_entrybox = ttk.Entry(root, textvariable=stop)
    stop_entrybox.grid(column=1, row=2, padx=5, pady=5)
    step = tk.StringVar()
    step_entrybox = ttk.Entry(root, textvariable=step)
    step_entrybox.grid(column=1, row=3, padx=5, pady=5)

    # Add labels showing the units.
    start_units_label = ttk.Label(root, text="deg")
    start_units_label.grid(column=2, row=1, sticky="w", padx=5, pady=5)
    stop_units_label = ttk.Label(root, text="deg")
    stop_units_label.grid(column=2, row=2, sticky="w", padx=5, pady=5)
    step_units_label = ttk.Label(root, text="deg")
    step_units_label.grid(column=2, row=3, sticky="w", padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Submit", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=1, row=4, padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=5, padx=5, pady=5)

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
    # TODO: Obtain option lists directly from the microscope object
    camera_options = ['BM-Ceta', 'BM-Falcon']
    sampling_options = ['4k (4096 x 4096)', '2k (2048 x 2048)', '1k (1024 x 1024)', '0.5k (512 x 512)']

    root = tk.Tk()
    style = ttk.Style()

    root.title("Tilt Range")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    message = ttk.Label(root, text="Please provide the following\nacquisition parameters:", font=(None, 15))
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

    integration_time = tk.StringVar()  # TODO: Add a default value into this entry box
    integration_time_entry_box = ttk.Entry(root, textvariable=integration_time)
    integration_time_entry_box.grid(column=1, row=2, padx=5, pady=5)

    sampling = tk.StringVar()
    sampling.set(sampling_options[0])  # Default to the first option in the list
    sampling_option_menu = ttk.OptionMenu(root, sampling, sampling_options[0], *sampling_options)
    sampling_option_menu.grid(column=1, row=3, padx=5, pady=5)

    # Add label showing integration time units.
    stop_units_label = ttk.Label(root, text="s")
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
    Get the out directory, where we will store the microED sequence.

    :param microscope: TEMInterface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: str:
        The out directory where the microED acquisition results will be saved.
    """
    # Create a pop-up warning the user they are about to have to select an out directory.
    root = tk.Tk()
    style = ttk.Style()

    root.title("Select out directory")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    # Build a message, letting the user know that we need directory and file name information
    message = ttk.Label(root, text="Where would you like to save the results?", font=(None, 15))
    message.grid(column=0, row=0, columnspan=2, sticky='w', padx=5, pady=5)

    # Create 'select directory' and 'exit' buttons
    continue_button = ttk.Button(root, text="Select Directory", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, columnspan=2, row=1, padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=0, columnspan=2, row=2, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    # Make the user select an out directory
    root = tk.Tk()
    root.eval('tk::PlaceWindow . center')  # Center the window on the screen
    root.directory = filedialog.askdirectory()
    out_dir = str(root.directory)

    root.destroy()

    # Make the user select a file-name
    root = tk.Tk()
    style = ttk.Style()

    root.title("Select file name")
    root.iconbitmap("./ico/BASF.ico")  # Add BASF Icon

    message = ttk.Label(root, text="Please select a file name:", font=(None, 15))
    message.grid(column=0, row=0, columnspan=3, sticky='w', padx=5, pady=5)

    # Label the filename box with the out directory
    camera_label = ttk.Label(root, text=out_dir + "/")
    camera_label.grid(column=0, row=1, sticky="e", padx=5, pady=5)

    file_name = tk.StringVar()
    file_name_entry_box = ttk.Entry(root, textvariable=file_name)
    file_name_entry_box.grid(column=1, row=1, padx=5, pady=5)

    # Add label showing the file extension
    stop_units_label = ttk.Label(root, text=".emi")  # TODO: Check this is the file extension
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
    out_path = out_dir + str(file_name.get()) + ".emi"
    return out_path


def ued_tilt_series():
    """

    """
    microscope = None
    try:
        # Display a welcome message
        # title, message = get_welcome_message()
        # display_message(title=title, message=message, microscope=microscope, position="centered")

        # Connect to the microscope and Initialize for MicroED
        # title, message = get_initialization_message()
        # display_message(title=title, message=message, microscope=microscope, position="centered")
        # microscope = TEMInterface()
        # microscope.open_column_valve()
        # microscope.set_mode("TEM")
        # microscope.set_projection_mode("Imaging")
        # microscope.set_image_shift(x=0, y=0)  # Zero the image shift
        # microscope.set_stage_position(alpha=0)  # Zero the stage tilt
        # microscope.normalize()

        # start_alpha, stop_alpha, step_alpha = get_tilt_range(microscope=microscope)

        # Move to the start tilt
        # display_message(title="Moving", message="The stage is being moved to the start angle",
        #                 microscope=microscope, position="centered")
        # microscope.set_stage_position_alpha(start_alpha)

        # Have the user center the particle
        title, message = get_alignment_message()
        display_message(title=title, message=message, microscope=microscope, position="out-of-the-way")

        # Get the required camera parameters
        camera_name, integration_time, sampling = get_camera_parameters(microscope=microscope)

        # Get the out path (where in the file system to save the results)
        out_path = get_out_path(microscope=microscope)
        print(out_path)


    except KeyboardInterrupt:
        warnings.warn("Keyboard interrupt detected, returning the microscope to a safe state and exiting.")
        exit_script(microscope=microscope, status=1)

    except Exception as e:
        raise e


if __name__ == "__main__":
    ued_tilt_series()
