"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import tkinter as tk

from tkinter import ttk
from typing import Union

import numpy as np
from PIL import ImageTk
from PIL import Image
from numpy.typing import ArrayLike

from pyTEM.Interface import Interface
from pyTEM_scripts.lib.micro_ed.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window
from pyTEM_scripts.lib.micro_ed.exit_script import exit_script


class AcquisitionSeriesGUI:
    """
    A GUI for the AcquisitionSeries() function. This GUI:
        - Displays the most recent image.
        - Displays the current count. I.e. Performing acquisition x out of y.
        - Displays an estimate of the current time remaining.
        - Allows the user to cancel the acquisition series without resorting to keyboard interrupts.


    """

    def __init__(self, microscope: Union[Interface, None], num: int, exposure_time: float):
        """
        :param microscope: pyTEM Interface (or None):
           The microscope interface, needed to return the microscope to a safe state if the user exits the script
            through the cancel button.
        :param num: int:
            The number of acquisitions in the series.
        :param exposure_time: float:
            Single image exposure time, in seconds.
            Needed to estimate the total time remaining.
        """
        self.microscope = microscope
        self.num = num
        self.exposure_time = exposure_time

        self.user_wants_to_exit = False

        self.font = (None, 13)  # Default font is fine
        self.window_width = 420
        self.window_height = 580

        self.root = tk.Tk()
        style = ttk.Style()

        self.root.title("Acquisition Series in Progress.")
        add_basf_icon_to_tkinter_window(self.root)
        self.root.geometry("{width}x{height}".format(width=self.window_width, height=self.window_height))

        # Create a label with the current acquisition count.
        acquisition_count_text = ("Performing acquisition 1 out of " + str(self.num) + ".")
        acquisition_count_label = ttk.Label(self.root, text=acquisition_count_text, wraplength=self.window_width,
                                            font=self.font, justify='center')
        acquisition_count_label.grid(column=0, row=0, padx=5, pady=5)

        # Create a label with an estimate of the current time remaining.
        time_remaining_text = "Estimated time till series completion: " \
                              + str(self.estimate_time_remaining(current_count=1))
        time_remaining_label = ttk.Label(self.root, text=time_remaining_text, wraplength=self.window_width,
                                         font=self.font, justify='center')
        time_remaining_label.grid(column=0, row=1, padx=5, pady=5)

        # Display the most recent image.
        image_label = ttk.Label(self.root, text="Here is acquisition #0: ", wraplength=self.window_width,
                                font=self.font, justify='center')
        image_label.grid(column=0, row=2, padx=5, pady=(5, 0))

        # Create an object of tkinter ImageTk.
        dummy_image = np.random.random((1024, 1024))  # A random 1k image.
        dummy_image = (65535 * dummy_image).astype(np.int16)  # Covert to 16-bit.

        img = Image.fromarray(dummy_image)
        img = img.resize(size=(400, 400))
        img = ImageTk.PhotoImage(img)

        label = ttk.Label(self.root, image=img)
        label.grid(column=0, row=3, padx=10, pady=(0, 5))

        # Create a button to cancel without saving. If pressed, the results of the current acquisition will be lost.
        cancel_without_saving_button = ttk.Button(self.root, text="Cancel Without Saving",
                                                  command=lambda: self.series_complete(), style="big.TButton")
        cancel_without_saving_button.grid(column=0, row=4, padx=5, pady=5)

        # Create a button to cancel with saving. If pressed, the current (probably incomplete) series should be
        #  returned once the current acquisition is complete.
        cancel_without_saving_button = ttk.Button(self.root, text="Cancel With Saving", style="big.TButton")
        cancel_without_saving_button.grid(column=0, row=5, padx=5, pady=5)
        cancel_without_saving_button.config(state=tk.DISABLED)  # TODO: Implement cancel with saving.

        style.configure('big.TButton', font=self.font, foreground="blue4")

        self.root.eval('tk::PlaceWindow . center')  # Center the window on the screen.

        self.root.protocol("WM_DELETE_WINDOW", lambda: exit_script(microscope=self.microscope, status=1))
        self.root.mainloop()

    def update_image(self, new_image: ArrayLike):
        """
        Update the image on the GUI display window.

        :param new_image: 2D array:
            The new image you would like to display on the GUI window.

        :return: None.
        """
        raise NotImplementedError

    def update_count(self, new_count):
        """
        Update the current acquisition count.

        :param new_count: int:
            The new count. Since acquisition count will run from 1 -> num, update_count must be between 1 and num.

        :return: None.
        """
        if new_count <= 1 or new_count > self.num:
            raise Exception("Error: The current acquisition count can not exceed the total number of acquisition.")

        raise NotImplementedError

    def update_time_remaining(self, current_count: int):
        """
        Update the total time remaining.

        :param current_count: int:
            The current count. Since acquisition count will run from 1 -> num, update_count must be between 1 and num.

        :return: None.
        """
        estimated_time_remaining = (self.num - current_count) * self.exposure_time

        raise NotImplementedError

    def series_complete(self):
        """
        We are done, enable the user_wants_to_exit flag.
        :return: None
        """
        self.user_wants_to_exit = True
        self.root.destroy()

    def estimate_time_remaining(self, current_count: int):
        """
        Based on the current count, estimate the time remaining.

        :param current_count: int:
            The number of the current acquisition.

        :return: float:
            An estimate of the current time remaining, in seconds.
        """
        return (self.num - current_count) * self.exposure_time


if __name__ == "__main__":
    """
    Testing
    """

    gui = AcquisitionSeriesGUI(microscope=None, num=5, exposure_time=3)
