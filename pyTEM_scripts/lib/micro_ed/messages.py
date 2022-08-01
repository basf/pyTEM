"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import warnings
import tkinter as tk

from tkinter import ttk
from typing import Tuple, Union

from pyTEM.Interface import Interface
from pyTEM_scripts.lib.micro_ed.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window
from pyTEM_scripts.lib.micro_ed.exit_script import exit_script


def display_welcome_message(microscope: Union[Interface, None]) -> None:
    """
    Display a welcome message.
    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "Good afternoon ladies and gentlemen. This is the pre-boarding announcement for TEM Air flight M300 with " \
            "service to Ludwigshafen am Rhein."
    message = "Welcome to BASF's in-house micro-crystal electron diffraction (MicroED) automated imaging " \
              "script. MicroED allows fast, high resolution 3D structure determination of small chemical " \
              "compounds and biological macromolecules! " \
              "\n\nYou can exit the script any time using the exit buttons " \
              "on the pop-up message boxes, or by hitting Ctrl-C on your keyboard. " \
              "\n\nPlease click the Continue button to get started!"
    display_message_centered(title=title, message=message, microscope=microscope)


def display_initialization_message(microscope: Union[Interface, None]) -> None:
    """
    Display the initialization message.
    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "We are now inviting those passengers with small children, and any passengers requiring special " \
            "assistance, to begin boarding at gate 7 at this time."
    message = "In order to initialize the microscope for MicroED, we are now going to: " \
              "\n - Insert the Flucam screen." \
              "\n - Make sure the microscope is in 'TEM' mode." \
              "\n - Make sure the microscope is in 'imaging' mode. " \
              "\n - Zero the image shift." \
              "\n - Zero the \u03B1 tilt." \
              "\n - Normalize all lenses." \
              "\n - Unblank the beam." \
              "\n\nIf a particle has already been chosen, you may want to reduce the illumination or " \
              "move the stage such that it will not be illuminated once, upon completion of the initialization " \
              "process, we unblank the beam." \
              "\n\nOnce you are ready to start the initialization procedure, please click the Continue button."
    display_message_centered(title=title, message=message, microscope=microscope)


def display_second_condenser_message(microscope: Union[Interface, None]) -> None:
    """
    Display a message prompting the user to insert the second condenser aperture, and set the second condenser lens
     intensity.

    To improve the chances of the user actual inserting the condenser aperture and adjusting the C2 lens, check boxes
     are provided, both of which need to be checked before the continue button becomes active.

    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "To expedite the boarding process, please have your boarding pass ready and passport open to the picture " \
            "page."
    upper_message = "Please optimize the intensity by inserting the C2 (second-condenser) aperture and by optimizing" \
                    " the C2 (second-condenser) lens. Please note that the C2 lens should be set to at least 55% " \
                    "intensity." \
                    "\n\nNotice that the C2 aperture is controlled from the Search tab on the microscope UI, and " \
                    "the C2 lens is controlled through the Intensity knob on the microscope control panel."
    lower_message = "Once the intensity has been optimized, please click the continue button."

    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    window_width = 650

    # Display the first part of the message
    upper_message = ttk.Label(root, text=upper_message, wraplength=window_width, font=(None, 15), justify='center')
    upper_message.grid(column=0, columnspan=2, row=0, padx=5, pady=5)

    def check_if_intensity_optimized() -> None:
        """
        Check to see if both the second-condenser aperture and lens have been properly configured. Once both the
         aperture and lens check boxes have been clicked, we can go ahead and enable the continue button.
        """
        if aperture_inserted.get() and lens_intensity_optimized.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    # Create a checkbutton for aperture inserted.
    aperture_inserted = tk.BooleanVar()
    aperture_inserted.set(False)
    aperture_inserted_checkbutton = ttk.Checkbutton(root, text="C2 Aperture Inserted",
                                                    variable=aperture_inserted, command=check_if_intensity_optimized,
                                                    style="big.TCheckbutton")
    aperture_inserted_checkbutton.grid(column=0, columnspan=2, row=1, padx=5, pady=(5, 0))

    # Create a checkbutton for lens intensity optimized.
    lens_intensity_optimized = tk.BooleanVar()
    lens_intensity_optimized.set(False)
    lens_intensity_optimized_checkbutton = ttk.Checkbutton(root, text="C2 Lens Intensity Optimized (>= 55%)",
                                                           variable=lens_intensity_optimized,
                                                           command=check_if_intensity_optimized,
                                                           style="big.TCheckbutton")
    lens_intensity_optimized_checkbutton.grid(column=0, columnspan=2, row=2, padx=5, pady=(0, 5))

    # Display the other part of the message
    lower_message = ttk.Label(root, text=lower_message, wraplength=window_width, font=(None, 15), justify='center')
    lower_message.grid(column=0, columnspan=2, row=3, padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=4, sticky="e", padx=5, pady=5)
    check_if_intensity_optimized()  # Disabled until aperture and lens are adjusted.
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=4, sticky="w", padx=5, pady=5)

    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()


def have_user_center_particle(microscope: Union[Interface, None], dummy_particle: bool = False) -> None:
    """
    Have the user center on a particle.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.
    :param dummy_particle: bool:
        Whether we are aligning the dummy particle.
            True: We are aligning a dummy particle.
            False: We are aligning on the actual particle we want to analyse

    :return: None.
    """
    if microscope is not None:
        microscope.unblank_beam()
    else:
        print("We are not connected to the microscope, otherwise we would be unblanking the beam.")

    while True:
        if dummy_particle:
            title = "We are now inviting our business and first-class customers to gate 7 for priority boarding."
            message = "Using the microscope control panel, please select a magnification in the SA range and center " \
                      "the microscope on some dummy particle. Don't worry about over-exposing the particle, this is " \
                      "the not the particle we are going to analyse." \
                      "\n\nFor best results, please choose a dummy particle at approximately the same y-location as " \
                      "(and preferably near to) the particle you want to analyse." \
                      "\n\nPlease do not adjust the stage tilt nor the image shift. " \
                      "\n\nOnce the dummy particle is centered, please click the Continue button."
            display_message_out_of_the_way(title=title, message=message, microscope=microscope, window_height=325)

            # The particle we are centering on is just some dummy particle, no need to re-blank

        else:
            title = "Our flight is now ready for departure, we wish you all an enjoyable flight."
            message = "Using the microscope control panel, please (with a magnification in the SA range) " \
                      "center the microscope on the particle of interest. " \
                      "\n\nPlease do not adjust the stage tilt nor the image shift. " \
                      "\n\nOnce the particle is centered, please click the Continue button and the blanker will be " \
                      "enabled automatically."
            display_message_out_of_the_way(title=title, message=message, microscope=microscope, window_height=215)

            if microscope is not None:
                microscope.blank_beam()
            else:
                print("We are not connected to the microscope, otherwise we would be blanking the beam.")

        if microscope is not None:
            # Confirm that we are in the correct magnification range (at the time of writing image shift is only
            #  calibrated for magnifications in the SA range)
            if microscope.get_projection_submode() == "SA":
                break  # Magnification is okay
            else:
                warnings.warn("Currently we are in the " + str(microscope.get_projection_submode())
                              + " magnification range, please select a magnification in the SA range.")
        else:
            break  # No microscope connection.

    return None


def display_eucentric_height_message(microscope: Union[Interface, None]) -> None:
    """
    Display the eucentric height calibration message.
    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "We will now begin general boarding for TEM Air flight M300 with service to Ludwigshafen am Rhein."
    message = "Please, using the \u03B1 wobble and z-axis buttons on the microscope control panel, manually set the " \
              "microscope to the eucentric height. That is, please find and select the z-height where tilting the " \
              "specimen leads to a minimal lateral movement of the image." \
              "\n\nOnce at eucentric height, re-center on the dummy particle and click the continue button."
    display_message_out_of_the_way(title=title, message=message, microscope=microscope, window_height=215)


def display_insert_and_align_sad_aperture_message(microscope: Union[Interface, None]) -> None:
    """
    Display the insert and align aperture message.

    To improve the changes of the user actual aligning and remembering to remove the aperture, check boxes are
     provided, both of which need to be checked before the continue button becomes active.

    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "In order to expedite the boarding process, please be seated as quickly as possible after stowing your " \
            "carry-on items."
    upper_message = "Please, using your microscope's UI and the microscope control panel, insert and align the " \
                    "required selected area diffraction (SAD) aperture." \
                    "\n\nOnce the SAD aperture is aligned, please remove it."
    lower_message = "Once the SAD aperture has aligned and removed, please click the continue button."

    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    window_width = 650

    # Display the first part of the message
    upper_message = ttk.Label(root, text=upper_message, wraplength=window_width, font=(None, 15), justify='center')
    upper_message.grid(column=0, columnspan=2, row=0, padx=5, pady=5)

    def check_if_aperture_is_aligned_and_removed() -> None:
        """
        Check to see, if both the aperture aligned and removed check boxes have been checked then we can go ahead and
         enable the continue button.
        """
        if aperture_aligned.get() and aperture_removed.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    # Create a checkbutton for aperture aligned.
    aperture_aligned = tk.BooleanVar()
    aperture_aligned.set(False)
    aperture_aligned_checkbutton = ttk.Checkbutton(root, text="SAD Aperture Aligned", variable=aperture_aligned,
                                                   command=check_if_aperture_is_aligned_and_removed,
                                                   style="big.TCheckbutton")
    aperture_aligned_checkbutton.grid(column=0, columnspan=2, row=1, padx=5, pady=(5, 0))

    # Create a checkbutton for aperture removed.
    aperture_removed = tk.BooleanVar()
    aperture_removed.set(False)
    aperture_removed_checkbutton = ttk.Checkbutton(root, text="SAD Aperture Removed", variable=aperture_removed,
                                                   command=check_if_aperture_is_aligned_and_removed,
                                                   style="big.TCheckbutton")
    aperture_removed_checkbutton.grid(column=0, columnspan=2, row=2, padx=5, pady=(0, 5))

    # Display the other part of the message
    lower_message = ttk.Label(root, text=lower_message, wraplength=window_width, font=(None, 15), justify='center')
    lower_message.grid(column=0, columnspan=2, row=3, padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=4, sticky="e", padx=5, pady=5)
    check_if_aperture_is_aligned_and_removed()  # Disabled until aperture has been aligned and removed.
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=4, sticky="w", padx=5, pady=5)

    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    # Display the message box up in the top right-hand corner
    root.geometry("{width}x{height}+{x}+{y}".format(width=window_width, height=270,
                                                    x=int(0.65 * root.winfo_screenwidth()),
                                                    y=int(0.025 * root.winfo_screenheight())))

    root.mainloop()


def get_automated_alignment_message() -> Tuple[str, str]:
    """
    :return: str: A message explaining the automated image alignment functionality.
    """
    title = "Thank you for choosing TEM-Air, we wish you all an enjoyable flight."
    message = "This MicroED script supports automated image alignment functionality. The required image shifts will " \
              "be computed from a preparatory tilt sequence using the hyperspy Python library (phase correlation) " \
              "and then applied during the main acquisition sequence." \
              "\n\nTo continue without image alignment functionality, please uncheck the checkbox below."
    return title, message


def display_insert_camera_message(microscope: Union[Interface, None], camera_name: str) -> None:
    """
    Display the start message.

    To improve the changes of the user actual inserting the aperture and beam-stop, check boxes are provided, both of
     which need to be checked before the continue button becomes active.

    :param camera_name: str:
        The name of the camera the user requested.
    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "Take a moment to locate the exit nearest you keeping in mind that the closest usable exit may be " \
            "located behind you."
    upper_message = "Please ensure the " + camera_name + " camera is inserted."
    lower_message = "Once the camera is inserted, please click the continue button."

    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    window_width = 650

    # Display the first part of the message
    upper_message = ttk.Label(root, text=upper_message, wraplength=window_width, font=(None, 15), justify='center')
    upper_message.grid(column=0, columnspan=2, row=0, padx=5, pady=5)

    def check_if_camera_is_inserted() -> None:
        """
        Check to see, if the camera inserted check box has been checked then we can go ahead and enable the continue
         button.
        """
        if camera_inserted.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    # Create a checkbutton for aperture inserted.
    camera_inserted = tk.BooleanVar()
    camera_inserted.set(False)
    camera_inserted_checkbutton = ttk.Checkbutton(root, text=camera_name + " Inserted", variable=camera_inserted,
                                                  command=check_if_camera_is_inserted, style="big.TCheckbutton")
    camera_inserted_checkbutton.grid(column=0, columnspan=2, row=1, padx=5, pady=5)

    # Display the other part of the message
    lower_message = ttk.Label(root, text=lower_message, wraplength=window_width, font=(None, 15), justify='center')
    lower_message.grid(column=0, columnspan=2, row=3, padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=4, sticky="e", padx=5, pady=5)
    check_if_camera_is_inserted()  # Disable the continue button until the user has confirmed the camera is inserted.
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=4, sticky="w", padx=5, pady=5)

    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()


def display_insert_sad_aperture_message(microscope: Union[Interface, None]) -> None:
    """
    Display the message prompting the user to insert the SAD aperture.

    To improve the changes of the user actual inserting the aperture, a checkbox is provided which need to be checked
     before the continue button becomes active.

    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "Flight attendants, prepare doors for departure and cross-check."
    upper_message = "Please insert the desired (and previously aligned) SAD aperture."
    lower_message = "Upon pressing continue, we will switch into diffraction mode."

    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    window_width = 650

    # Display the first part of the message
    upper_message = ttk.Label(root, text=upper_message, wraplength=window_width, font=(None, 15), justify='center')
    upper_message.grid(column=0, columnspan=2, row=0, padx=5, pady=5)

    def check_if_aperture_is_inserted() -> None:
        """
        Check to see, if the aperture has been inserted then we can go ahead and enable the continue button.
        """
        if aperture_inserted.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    # Create a checkbutton for aperture inserted.
    aperture_inserted = tk.BooleanVar()
    aperture_inserted.set(False)
    aperture_inserted_checkbutton = ttk.Checkbutton(root, text="SAD Aperture Inserted", variable=aperture_inserted,
                                                    command=check_if_aperture_is_inserted,
                                                    style="big.TCheckbutton")
    aperture_inserted_checkbutton.grid(column=0, columnspan=2, row=1, padx=5, pady=5)

    # Display the other part of the message
    lower_message = ttk.Label(root, text=lower_message, wraplength=window_width, font=(None, 15), justify='center')
    lower_message.grid(column=0, columnspan=2, row=3, padx=5, pady=5)

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=4, sticky="e", padx=5, pady=5)
    check_if_aperture_is_inserted()  # Disabled until aperture has been inserted.
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=4, sticky="w", padx=5, pady=5)

    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()


def display_beam_stop_center_spot_message(microscope: Union[Interface, None]) -> None:
    """
    Display a message prompting the user to:
     - Set an appropriate camera length
     - Insert the beam stop (if required)
     - Center the diffraction spot

    To improve the changes of the user actual selecting an appropriate camera length, inserting beam-stop, and
     aligning the diffraction spot, check boxes are provided, all of which need to be checked before the continue
     button becomes active.

    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    root = tk.Tk()
    style = ttk.Style()

    root.title("We are third in priority for take-off, we should depart in about five minutes.")
    add_basf_icon_to_tkinter_window(root)

    window_width = 650
    window_height = 325

    def check_if_camera_length_set__beam_stop_inserted__diffraction_spot_aligned() -> None:
        """
        Check to see, if the camera length, beam-stop, and diffraction spot check boxes have all been checked then
         we can go ahead and enable the continue button.
        """
        if camera_length_selected.get() and beam_stop_inserted.get() and diffraction_spot_centered.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    # Display the first message.
    message1 = "Please select an appropriate camera length."
    message1_label = ttk.Label(root, text=message1, wraplength=window_width, font=(None, 15), justify='center')
    message1_label.grid(column=0, columnspan=2, row=0, padx=5, pady=(5, 0))

    # Create a checkbutton for camera length selected.
    camera_length_selected = tk.BooleanVar()
    camera_length_selected.set(False)
    camera_length_selected_checkbutton = \
        ttk.Checkbutton(root, text="Camera Length Selected", variable=camera_length_selected,
                        command=check_if_camera_length_set__beam_stop_inserted__diffraction_spot_aligned,
                        style="big.TCheckbutton")
    camera_length_selected_checkbutton.grid(column=0, columnspan=2, row=1, padx=5, pady=(0, 5))

    # Display the second message.
    message2 = "If required, please insert the beam-stop."
    message2_label = ttk.Label(root, text=message2, wraplength=window_width, font=(None, 15), justify='center')
    message2_label.grid(column=0, columnspan=2, row=2, padx=5, pady=(5, 0))

    # Create a checkbutton for beam-stop inserted.
    beam_stop_inserted = tk.BooleanVar()
    beam_stop_inserted.set(False)
    beam_stop_inserted_checkbutton = \
        ttk.Checkbutton(root, text="Beam-Stop Inserted (or not required)", variable=beam_stop_inserted,
                        command=check_if_camera_length_set__beam_stop_inserted__diffraction_spot_aligned,
                        style="big.TCheckbutton")
    beam_stop_inserted_checkbutton.grid(column=0, columnspan=2, row=3, padx=5, pady=(0, 5))

    # Display the third message
    message3 = "Please, using the multifunction knobs on the microscope control panel, center/align the " \
               "diffraction spot."
    message3_label = ttk.Label(root, text=message3, wraplength=window_width, font=(None, 15),
                               justify='center')
    message3_label.grid(column=0, columnspan=2, row=4, padx=5, pady=(5, 0))

    # Create a checkbutton for diffraction spot centered.
    diffraction_spot_centered = tk.BooleanVar()
    diffraction_spot_centered.set(False)
    diffraction_spot_centered_checkbutton = \
        ttk.Checkbutton(root, text="Diffraction Spot Aligned", variable=diffraction_spot_centered,
                        command=check_if_camera_length_set__beam_stop_inserted__diffraction_spot_aligned,
                        style="big.TCheckbutton")
    diffraction_spot_centered_checkbutton.grid(column=0, columnspan=2, row=5, padx=5, pady=(0, 5))

    # Display the fourth message
    message4 = "Once an appropriate camera length has been selected, the beam-stop has been inserted (if required), " \
               "and the diffraction spot has been aligned, please continue."
    message4_label = ttk.Label(root, text=message4, wraplength=window_width, font=(None, 15), justify='center')
    message4_label.grid(column=0, columnspan=2, row=6, padx=5, pady=(5, 0))

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=7, sticky="e", padx=5, pady=5)
    # Disable until the camera length has been set, beam stop inserted, and diffraction spot centered.
    check_if_camera_length_set__beam_stop_inserted__diffraction_spot_aligned()
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=7, sticky="w", padx=5, pady=5)

    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    # Display the message box up in the top right-hand corner.
    root.geometry("{width}x{height}+{x}+{y}".format(width=window_width, height=window_height,
                                                    x=int(0.65 * root.winfo_screenwidth()),
                                                    y=int(0.025 * root.winfo_screenheight())))

    root.mainloop()


def display_start_message(microscope: Union[Interface, None]) -> None:
    """
    Display a message notifying the user that we are about to start the experiment.

    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    """
    title = "Cabin crew, please take your seats for take-off."
    message = "We are now ready to begin the MicroED tilt series!" \
              "\n\nPlease refrain from touching the microscope controls for the duration of the experiment. If, at " \
              "any point, you need to stop the experiment, please hit Ctrl-C on the keyboard. " \
              "\n\nOnce the experiment concludes, the column valve will close automatically. Upon pressing " \
              "continue, the automated acquisition series will begin!"
    display_message_centered(title=title, message=message, microscope=microscope)


def display_end_message(microscope: Union[Interface, None], out_file: str, saved_as_stack: bool) -> None:
    """
    Display an end message letting the user know that we have completed the MicroED sequence.

    We inform the user of the things that will be taken care of automatically (like zeroing the image shift)

    To improve the changes of the user actual inserting beam-stop and aligning the spot, check boxes are provided,
     both of which need to be checked before the continue button becomes active.

    :param microscope: pyTEM Interface (or None):
           A microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the quit button on the message box.
    :param out_file: str:
        The out file path.
    :param saved_as_stack: bool:
        Whether the images were saved as a single multi-image stack file.
    """
    title = "Ladies and gentlemen, we have begun our descent into Ludwigshafen, where the weather is a balmy " \
            "30 degrees centigrade."
    upper_message = "We have now completed the MicroED tilt series acquisition!" \
                    "\n\nThe results can be found here:"
    lower_message = "Image shift and \u03B1 stage tilt will be zeroed automatically upon script termination. " \
                    "However, the beam will remain blank, and both the apertures and the camera will remain inserted " \
                    "until manually retracted."

    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    window_width = 650

    # Display the upper part of the message.
    upper_message_label = ttk.Label(root, text=upper_message, wraplength=window_width, font=(None, 15),
                                    justify='center')
    upper_message_label.grid(column=0, columnspan=2, row=0, padx=5, pady=(5, 0))

    def check_if_user_understands() -> None:
        """
        Check to see, if the user checks the box indicating that they understand that they must remove the apertures and
         the camera manually, then can go ahead and enable the continue button.
        """
        if user_understands.get():
            continue_button.config(state=tk.NORMAL)
        else:
            continue_button.config(state=tk.DISABLED)

    # Display the out file location.
    if saved_as_stack:
        out_file_label_text = out_file
    else:
        file_name_base, file_extension = os.path.splitext(out_file)
        out_file_label_text = file_name_base + "_<tilt angle>" + file_extension
    out_file_label = ttk.Label(root, text=out_file_label_text, wraplength=window_width, font=(None, 12, 'bold'),
                               justify='center')
    out_file_label.grid(column=0, columnspan=2, row=1, padx=5, pady=(0, 5))

    # Display the lower part of the message.
    lower_message_label = ttk.Label(root, text=lower_message, wraplength=window_width, font=(None, 15),
                                    justify='center')
    lower_message_label.grid(column=0, columnspan=2, row=2, padx=5, pady=(5, 0))

    # Create a checkbutton for the user to click if they understand they are responsible for removing the apertures
    #  and camera manually.
    user_understands = tk.BooleanVar()
    user_understands.set(False)
    user_understands_checkbutton = ttk.Checkbutton(root, text="I understand the apertures and camera need to be "
                                                              "retracted manually.", variable=user_understands,
                                                   command=check_if_user_understands, style="big.TCheckbutton")
    user_understands_checkbutton.grid(column=0, columnspan=2, row=3, padx=5, pady=(0, 5))

    # Create continue and exit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=4, sticky="e", padx=5, pady=5)
    # Disable until user understands that the apertures and camera need to be retracted manually.
    check_if_user_understands()
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=4, sticky="w", padx=5, pady=5)

    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen.

    root.mainloop()


def display_good_bye_message(microscope: Union[Interface, None]):
    """
    Display goodbye message.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: None.
    """
    title = "Thank you for flying with Air TEM, we hope to see you again soon!"
    message = "Thank you for using BASF's in house MicroED automated imaging script. Please report any issues on " \
              "GitHub: https://github.com/mrl280/pyTEM/issues."
    display_message_centered(title=title, message=message, microscope=microscope)


def display_message_centered(title: str, message: str, microscope: Union[Interface, None]) -> None:
    """
    Display a simple message box with 'Continue' and 'Quit' buttons at the bottom.

    Message is displayed on the centered on the screen, which is useful when you need the users full attention,
     and don't want them fiddling around with the microscope in the background.

    :param message: str:
        The message to display.
    :param title: str:
        Message box title.

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: None.
    """
    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    window_width = 650
    message = ttk.Label(root, text=message, wraplength=window_width, font=(None, 15), justify='center')
    message.grid(column=0, columnspan=2, row=0, padx=5, pady=5)

    # Create continue and quit buttons
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(column=0, row=1, sticky="e", padx=5, pady=5)
    exit_button = ttk.Button(root, text="Quit", command=lambda: exit_script(microscope=microscope, status=1),
                             style="big.TButton")
    exit_button.grid(column=1, row=1, sticky="w", padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    # Center the window on the screen
    root.eval('tk::PlaceWindow . center')

    root.mainloop()


def display_message_out_of_the_way(title: str, message: str, window_height: Union[float, int],
                                   microscope: Union[Interface, None]) -> None:
    """
    Display a simple message box with 'continue' and 'exit' buttons at the bottom.

    Message is displayed "out of the way", which is useful when you need the user to adjust the microscope in the
     background before continuing.

    :param message: str:
        The message to display.
    :param title: str:
        Message box title.
    :param window_height: int or float:
        The desired window height (usually determined experimentally based on message length).

    :param microscope: pyTEM Interface (or None):
        The microscope interface, needed to return the microscope to a safe state if the user exits the script
         through the quit button on the message box.

    :return: None.
    """
    root = tk.Tk()
    style = ttk.Style()

    root.title(title)
    add_basf_icon_to_tkinter_window(root)

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

    # Display the message box up in the top right-hand corner
    root.geometry("{width}x{height}+{x}+{y}".format(width=window_width, height=window_height,
                                                    x=int(0.65 * root.winfo_screenwidth()),
                                                    y=int(0.025 * root.winfo_screenheight())))

    root.mainloop()


if __name__ == "__main__":
    """ 
    Testing 
    """

    # display_welcome_message(microscope=None)

    # display_initialization_message(microscope=None)

    # display_second_condenser_message(microscope=None)

    # have_user_center_particle(microscope=None, dummy_particle=True)

    # have_user_center_particle(microscope=None, dummy_particle=False)

    # display_eucentric_height_message(microscope=None)

    # display_insert_and_align_sad_aperture_message(microscope=None)

    # display_insert_camera_message(microscope=None, camera_name="BM-Ceta")

    # display_insert_sad_aperture_message(microscope=None)

    # display_beam_stop_center_spot_message(microscope=None)

    # display_start_message(microscope=None)

    display_end_message(microscope=None, out_file="C:/PycharmProjects/dummy_path.tif", saved_as_stack=False)

    # display_good_bye_message(microscope=None)
