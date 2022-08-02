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


class GetCorrectionalFactors:
    """
    Sometimes, in the absence of a sample, you don't observe the expected intensity. For example, when both the
     polarizer and analyzer are aligned at 45 deg you expect 100% intensity. However, this is not always the case. Such
     discrepancies may be due to inhomogeneities in, and a slight polarization of, the incident light.

    This class displays a Tkinter window to help the user get the correctional factors.
    """

    def __init__(self):
        # Preallocate correctional factors' matrix.
        self.correctional_factors = np.full(shape=(4, 4), fill_value=np.nan, dtype='float64')

        # So we don't have to type them in every time, hard code some default values for the observed intensities.
        self.observed_intensity_default_values = [[100.0, 100.0, 100.0, 100.0],
                                                  [91.2,  89.8,  83.4,  93.8],
                                                  [49.2,  70.8,  79.5,  80.9],
                                                  [89.0,  87.4,  84.5,  89.3]]

    def run(self) -> Union[np.ndarray, None]:
        """
        :return: correctional_factors: 2-dimensional array:
            A matrix of correctional factors. As shown in the matrix below, row indices represent polarization angle and
             column indices represent analyzer angle.

                                           Analyzer angle
                                                0 deg       45 deg      90 deg      135 deg
               Polarizer angle     0 deg         11          12          13          14
                                   45 deg        21          22          23          24
                                   90 deg        31          32          33          34
                                   135 deg       41          42          43          44

             If the user chooses to proceed without correctional factors, then all returned factors are just 1.0.
        """
        window_width = 650
        font = (None, 13)

        root = tk.Tk()
        style = ttk.Style()

        title = "Correctional Factors"
        root.title(title)
        add_basf_icon_to_tkinter_window(root)

        intro_message = "Sometimes, in the absence of a sample, you don't observe the expected intensity. Here, we " \
                        "collect the observed intensities with an amorphous sample, from which correctional factors " \
                        "are computed."
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
        instructions2_label.grid(row=3, column=0, columnspan=6, padx=5, pady=(0, 15))
        instructions2_label.config(foreground="blue")

        # Create analyzer and polarizer table labels.
        analyzer_angle_label = ttk.Label(root, text="Analyzer Angle, \u03C6 [deg]", wraplength=300, font=font,
                                         justify='center')
        analyzer_angle_label.grid(row=4, column=2, columnspan=2, padx=5, pady=5)
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

        def compute_correctional_factors_and_fill_in_labels(*args) -> np.array:
            """
            Compute the correctional factors from the observed intensities in the entry boxes.

            :return: None. But the correctional_factors attribute is updated.
            """
            for (i, j), factor in np.ndenumerate(self.correctional_factors):
                try:
                    self.correctional_factors[i][j] = 100 / float(observed_intensity_entry_boxes[i][j].get())
                except (ValueError, ZeroDivisionError):
                    # User entered 0 or cleared the box.
                    self.correctional_factors[i][j] = np.inf

                # Update the corresponding label.
                correctional_factor_labels[i][j].config(text=round(self.correctional_factors[i][j], 2))

            # If we have any invalid entries, then disable the continue button.
            if np.inf in self.correctional_factors:
                continue_button.config(state=tk.DISABLED)
            else:
                # All values should be fine
                continue_button.config(state=tk.NORMAL)

        def clear_observed_intensities(*args) -> None:
            """
            Clear all the observed intensity entry boxes.
            :return: None.
            """
            for (_, _), observed_intensity_entry_box_ in np.ndenumerate(observed_intensity_entry_boxes):
                observed_intensity_entry_box_.delete(0, 'end')
            compute_correctional_factors_and_fill_in_labels()

        def reset_observed_intensities(*args) -> None:
            """
            Set/reset all the observed intensity entry boxes to their default values.
            :return: None.
            """
            clear_observed_intensities()
            for (i, j), observed_intensity_entry_box_ in np.ndenumerate(observed_intensity_entry_boxes):
                observed_intensity_entry_box_.insert(0, str(self.observed_intensity_default_values[i][j]))
            compute_correctional_factors_and_fill_in_labels()

        # Offsets for the 4x4 entry box grid.
        row_offset = 6  # There are this many rows above us.
        col_offset = 2  # There are this many columns to the right of us.

        # Create variables to hold the observed intensities.
        observed_intensity_entry_str_vars = np.asarray(
            [[tk.StringVar() for _ in range(4)] for _ in range(4)]
        )

        # Add entry boxes in which the user can update the observed intensities.
        observed_intensity_entry_boxes = np.asarray(
            [[ttk.Entry(root, textvariable=observed_intensity_entry_str_vars[i][j]) for j in range(4)] for i in range(4)]
        )
        for (row, col), observed_intensity_entry_box in np.ndenumerate(observed_intensity_entry_boxes):
            observed_intensity_entry_box.config(justify='center')
            observed_intensity_entry_box.grid(row=row_offset + 2 * row, column=col_offset + col, padx=5, pady=(5, 0))

        # Add labels where we show the current correctional factors in blue.
        correctional_factor_labels = np.asarray(
            [[ttk.Label(root, font=font) for _ in range(4)] for _ in range(4)]
        )
        for (row, col), correctional_factor_label in np.ndenumerate(correctional_factor_labels):
            correctional_factor_label.config(foreground="blue")
            correctional_factor_label.grid(row=row_offset + 2 * row + 1, column=col_offset + col, padx=5, pady=(0, 5))

        # Add a reset button that will reset all observed intensities to their default values.
        reset_button = ttk.Button(root, text="Reset", command=lambda: reset_observed_intensities(), style="big.TButton")
        reset_button.grid(row=14, column=2, padx=5, pady=5)

        # Add a clear button that will clear all observed intensities.
        reset_button = ttk.Button(root, text="Clear", command=lambda: clear_observed_intensities(), style="big.TButton")
        reset_button.grid(row=14, column=3, padx=5, pady=5)

        # Create a 'Continue' button that the user can click to proceed.
        continue_button = ttk.Button(root, text="Continue", command=lambda: root.destroy(), style="big.TButton")
        continue_button.grid(row=14, column=4, padx=5, pady=5)

        # Create an 'exit' button that the user can use to exit the script.
        exit_button = ttk.Button(root, text="Exit", command=lambda: sys.exit(0), style="big.TButton")
        exit_button.grid(row=14, column=5, padx=5, pady=5)

        # Add variable traces and initialize correctional factors from the initial entry box values.
        for (_, _), observed_intensity_entry_str_var in np.ndenumerate(observed_intensity_entry_str_vars):
            observed_intensity_entry_str_var.trace('w', compute_correctional_factors_and_fill_in_labels)
        reset_observed_intensities()  # Also fills in the labels

        style.configure('big.TButton', font=(None, 10), foreground="blue4")
        style.configure('big.TCheckbutton', font=(None, 12, 'bold'))
        style.configure('big.TRadiobutton', font=(None, 11))

        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        root.mainloop()

        if use_correctional_factors.get():
            # The user has requested we proceed with correctional factors.
            return self.correctional_factors

        else:
            # We are proceeding without correctional factors.
            return np.full(shape=(4, 4), fill_value=1.0, dtype='float64')


if __name__ == "__main__":
    correctional_factors__ = GetCorrectionalFactors().run()

    print("Here are the obtained correctional factors:")
    print(correctional_factors__)
