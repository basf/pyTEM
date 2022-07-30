"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import sys

import numpy as np
import tkinter as tk

from tkinter import ttk
from typing import Union

from pyTEM_scripts.lib.micro_ed.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window


def get_correctional_factors() -> Union[np.ndarray, None]:
    """
    Sometimes, in the absence of a sample, you don't observe the expected intensity. For example, when both the
     polarizer and analyzer are aligned at 45 deg you expect 100% intensity. However, this is not always the case. Such
     discrepancies may be due to inhomogeneities in, and a slight polarization of, the incident light.

    Here, we collect correctional factors, which are computed from the observed intensity with an amorphous sample.

    :return: 2-dimensional array:
        A matrix of correctional factors. As shown in the matrix below, row indices represent polarization angle and
         column indices represent analyzer angler.

                                       Analyzer angle
                                            0 deg       45 deg      90 deg      135 deg
           Polarizer angle     0 deg         11          12          13          14
                               45 deg        21          22          23          24
                               90 deg        31          32          33          34
                               135 deg       41          42          43          44

         If None, then the user has chosen to proceed without correctional factors.
    """
    window_width = 650
    font = (None, 13)

    root = tk.Tk()
    style = ttk.Style()

    title = "Correctional Factors"
    root.title(title)
    add_basf_icon_to_tkinter_window(root)

    intro_message = "Sometimes, in the absence of a sample, you don't observe the expected intensity. Here, we " \
                    "collect the observed intensities with an amorphous sample, from which correctional factors are " \
                    "computed."
    intro_message_label = ttk.Label(root, text=intro_message, wraplength=window_width, font=font, justify='center')
    intro_message_label.grid(row=0, column=0, columnspan=6, padx=5, pady=5)

    def deactivate_other_entry_widgets():
        """
        Deactivate all the entry widgets whenever the user unchecks the use_correctional_factors button.
        """
        if use_correctional_factors.get() == 1:
            # Enable all entry boxes.
            for (_, _), entry in np.ndenumerate(observed_intensity_entry_boxes):
                entry.config(state=tk.NORMAL)
        else:
            # Disable all entry boxes
            for (_, _), entry in np.ndenumerate(observed_intensity_entry_boxes):
                entry.config(state=tk.DISABLED)

    # Create a checkbutton for asking the user whether they want to use correctional factors.
    use_correctional_factors = tk.BooleanVar()
    use_correctional_factors.set(True)
    use_correctional_factors_button = ttk.Checkbutton(root, text="Use Correctional Factors",
                                                      variable=use_correctional_factors, style="big.TCheckbutton",
                                                      command=deactivate_other_entry_widgets)
    use_correctional_factors_button.grid(row=1, column=0, columnspan=6, padx=5, pady=5)

    # Provide the user with some instructions
    instructions1 = "Enter the observed intensities into the entry boxes below."
    instructions1_label = ttk.Label(root, text=instructions1, wraplength=window_width, font=font, justify='center')
    instructions1_label.grid(row=2, column=0, columnspan=6, padx=5, pady=(5, 0))
    instructions2 = "Correctional factors are shown in blue."
    instructions2_label = ttk.Label(root, text=instructions2, wraplength=window_width, font=font, justify='center')
    instructions2_label.grid(row=3, column=0, columnspan=6, padx=5, pady=(0, 5))
    instructions2_label.config(foreground="blue")

    # Create analyzer and polarizer table labels.
    analyzer_angle_label = ttk.Label(root, text="Analyzer Angle, \u03C6 [deg]", wraplength=125, font=font,
                                     justify='center')
    analyzer_angle_label.grid(row=4, column=2, padx=5, pady=5)
    polarizer_angle_label = ttk.Label(root, text="Polarizer Angle, \u03B8 [deg]", wraplength=125, font=font,
                                      justify='center')
    polarizer_angle_label.grid(row=6, rowspan=2, column=0, padx=5, pady=5)

    # Add horizontal and vertical degree labels.
    horizontal_deg_labels = np.asarray([ttk.Label(root, text=str(45 * i), font=font) for i in range(4)])
    for i, label in enumerate(horizontal_deg_labels):
        label.grid(row=5, column=2 + i, padx=5, pady=5)
    vertical_deg_labels = np.asarray([ttk.Label(root, text=str(45 * i), font=font) for i in range(4)])
    for i, label in enumerate(vertical_deg_labels):
        label.grid(row=6 + 2 * i, rowspan=2, column=1, padx=5, pady=5)

    # Preallocate a matrix for the correctional factors, initially, they are all just 1.0.
    correctional_factor_str_vars = observed_intensity_entry_boxes = np.asarray(
        [[tk.StringVar() for j in range(4)] for i in range(4)]
    )

    # Offsets for the 4x4 entry box grid.
    row_offset = 6  # There are this many rows above us.
    col_offset = 2  # There are this many columns to the right of us.

    # Add entry boxes in which the user can insert the observed intensity.
    observed_intensity_entry_boxes = np.asarray(
        [[ttk.Entry(root, textvariable=correctional_factor_str_vars[i][j]) for j in range(4)] for i in range(4)]
    )
    for (row, col), observed_intensity_entry_box in np.ndenumerate(observed_intensity_entry_boxes):
        observed_intensity_entry_box.config(justify='center')
        observed_intensity_entry_box.insert(0, str(100))
        observed_intensity_entry_box.grid(row=row_offset + 2 * row, column=col_offset + col, padx=5, pady=(5, 0))

    # Add labels where we show the current correctional factors in blue.
    correctional_factor_labels = np.asarray(
        [[ttk.Label(root, text=str(i) + str(j), font=font) for j in range(4)] for i in range(4)]
    )
    for (row, col), correctional_factor_label in np.ndenumerate(correctional_factor_labels):
        correctional_factor_label.config(foreground="blue")
        correctional_factor_label.grid(row=row_offset + 2 * row + 1, column=col_offset + col, padx=5, pady=(0, 5))




    # Create a 'Continue' button that the user can click to proceed.
    continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
    continue_button.grid(row=14, column=0, columnspan=6, padx=5, pady=5)

    # Create an 'exit' button that the user can use to exit the script.
    exit_button = ttk.Button(root, text="Exit", command=lambda: sys.exit(), style="big.TButton")
    exit_button.grid(row=15, column=0, columnspan=6, padx=5, pady=5)

    style.configure('big.TButton', font=(None, 10), foreground="blue4")
    style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
    style.configure('big.TRadiobutton', font=(None, 11))

    root.eval('tk::PlaceWindow . center')  # Center the window on the screen

    root.mainloop()

    if use_correctional_factors.get():
        # The user has requested we proceed with correctional factors.
        correctional_factors = np.asarray(
            [[correctional_factor_str_vars[i][j].get() for j in range(4)] for i in range(4)]
        )
        return correctional_factors

    else:
        # We are proceeding without correctional factors.
        return None


if __name__ == "__main__":
    correctional_factors_ = get_correctional_factors()

    print("Here are the obtained correctional factors:")
    print(correctional_factors_)
