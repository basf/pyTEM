"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import tkinter as tk
from tkinter import ttk

from uED.lib.exit_script import exit_script


def get_welcome_message():
    """
    :return: str: A welcome message.
    """
    title = "Good morning ladies and gentlemen. On behalf of TEM Air, it is my pleasure to welcome you aboard flight " \
            "uED-4567."
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
    title = "In order to expedite the boarding process, please be seated as quickly as possible after stowing your " \
            "carry-on items."
    message = "In order to initialize the microscope for MicroED, we are now going to: " \
              "\n - Connect to the microscope." \
              "\n - Insert the Flucam screen." \
              "\n - Make sure the microscope is in 'TEM' mode." \
              "\n - Make sure the microscope is in 'Imaging' mode. " \
              "\n - Zero the image shift." \
              "\n - Zero the \u03B1 tilt." \
              "\n - Normalize all lenses." \
              "\n - Unblank the beam." \
              "\n\n To start this initialization procedure, please click the continue button."
    return title, message


def get_alignment_message():
    """
    :return: str: An initialization message.
    """
    title = "Fasten your seat belt by placing the metal fitting into the buckle, and adjust the strap so it fits " \
            "low and tight around your hips."
    message = "Using the microscope control panel, please select the desired magnification and center the microscope " \
              "on the particle of interest. " \
              "\n\nPlease do not adjust the stage tilt nor the image shift. " \
              "\n\nOnce the particle is centered, please click the continue button."
    return title, message


def get_start_message():
    """
    :return: str: A start message.
    """
    title = "Flight attendants, prepare doors for departure and cross check."
    message = "We are now ready to perform a MicroED tilt acquisition series! Please refrain from touching the " \
              "microscope controls for the duration of the experiment. If at any point you need to stop the " \
              "experiment, please hit Ctrl-C on your keyboard. " \
              "\n\nUpon pressing continue, the stage will be removed and the automated acquisition series will begin!"
    return title, message


def get_end_message(out_file):
    """
    :param: out_file: str:
        The out file path.
    :return: str: An end message.
    """
    title = "Ladies and gentlemen, we have begun our descent."
    message = "We have now completed the MicroED tilt acquisition series!" \
              "\n\nYour images can be found in " + str(out_file)
    return title, message


def get_good_bye_message():
    """
    :return: str: A good bye message.
    """
    title = "Thank you for flying with Air TEM, we hope to see you again soon!"
    message = "Thank you for using BASF's in house MicroED automated imaging script. Please report any issues on " \
              "GitHub: https://github.com/mrl280/tem-scripting-package"
    return title, message


def display_message(title, message, microscope, position="centered"):
    """
    Display a simple message box with 'continue' and 'exit' buttons at the bottom.

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
    message = ttk.Label(root, text=message, wraplength=window_width, font=(None, 15), justify='center')
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
