import tkinter as tk
from tkinter import ttk

from Interface.TEMInterface import TEMInterface


def get_welcome_message():
    """
    :return: str: Welcome message.
    """
    title = "Willkommen!"
    message = "Welcome to BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging " \
              "script. MicroED allows fast, high resolution 3D structure determination of small chemical " \
              "compounds biological macromolecules! You can exit the script any time using the exit button. " \
              "Please click the continue button to get started!"
    return title, message


def get_initialization_message():
    """
    :return: str: Initialization message
    """
    title = "Initialization"
    message = "in order to initialize the microscope for MicroED are now going to: " \
              "\n - Connect to the microscope." \
              "\n - Connect to the microscope, " \
              "\n - Zero the image shift." \
              "\n - Zero the \u03B1 tilt." \
              "\n To start the initialization procedure, please click the continue button."
    return title, message


def exit_script():
    """

    :return:
        -1: Failure
        0: Success
        1: Exiting before image sequence completion.
    """
    # TODO: Return the microscope to a safe state and exit gracefully
    pass


def display_message(title, message, position="centered"):
    """
    Display a simple message box with 'continue' and 'exit' buttons at the bottom.

    :param message: str:
        The message to display.
    :param title: str:
        Message box title.
    :param position: str:
        The position of the message box, one of:
        - "centered" (useful when you need the users full attention, and don't want them fiddling around with the
                      microscope in the background)
        - "out-of-the-way" (useful when you need the user to adjust the microscope in the background before confirming)

    :return: None.
    """
    # TODO: Fix up this function
    root = tk.Tk()
    root.title(title)

    window_width = 600
    window_height = 300

    # get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # find the center point
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    # set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # root.iconbitmap("../.ico")

    message = ttk.Label(root, text=message, wraplength=window_width, font=("Arial", 25))

    # tk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

    continue_button = ttk.Button(root, text="Continue", command=lambda: root.quit())
    exit_button = ttk.Button(root, text="Quit", command=lambda: root.quit())


    continue_button.pack(ipadx=5, ipady=5, expand=True)
    message.pack(ipadx=5, ipady=5, expand=True)
    exit_button.pack(ipadx=5, ipady=5, expand=True)

    root.mainloop()


def ued_tilt_series():
    """

    """
    # Display a welcome message
    title, message = get_welcome_message()
    display_message(title=title, message=message)

    microscope = TEMInterface()

    # Initialize the microscope for MicroED
    title, message = get_initialization_message()
    display_message(title=title, message=message)
    microscope.set_mode("TEM")
    microscope.set_projection_mode("Imaging")
    microscope.set_image_shift(x=0, y=0)  # Zero the image shift
    microscope.set_stage_position(alpha=0)  # Zero the stage tilt

    print("Please center the microscope on the desired")

    # Normalize the lenses. This
    print("Normalizing, please wait...")
    microscope.normalize()


if __name__ == "__main__":
    ued_tilt_series()
