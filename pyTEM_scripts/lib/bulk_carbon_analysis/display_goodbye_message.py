"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
import sys
import tkinter as tk

from tkinter import ttk
from typing import Union

from pyTEM_scripts.lib.micro_ed.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window


def display_goodbye_message(anisotropy_out_path: Union[pathlib.Path, str],
                            orientation_out_path: Union[pathlib.Path, str]):
    """
    Display a goodbye message,
        - thanking the user,
        - letting them know where to find the anisotropy and orientation map results,
        - and prompting them to report any issues on the GitHub.

    :param anisotropy_out_path: str or path:
        Path to the resultant anisotropy map.
    :param orientation_out_path: str or path:
        Path to the resultant orientation map.

    :return: None.
    """
    root = tk.Tk()
    style = ttk.Style()
    max_window_width = 650

    root.title("Mission success!")
    add_basf_icon_to_tkinter_window(root)

    success_message_label = ttk.Label(root, text="Bulk carbon analysis successful!", wraplength=max_window_width,
                                      font=(None, 15), justify='center')
    success_message_label.grid(column=0, row=0, padx=5, pady=5)

    # Display the anisotropy out file path.
    anisotropy_out_label = ttk.Label(root, text="The anisotropy map can be found here:", wraplength=max_window_width,
                                     font=(None, 15), justify='center')
    anisotropy_out_label.grid(column=0, row=1, padx=5, pady=(5, 0))
    anisotropy_out_path_label = ttk.Label(root, text=str(anisotropy_out_path), wraplength=max_window_width,
                                          font=(None, 15, 'bold'), justify='center')
    anisotropy_out_path_label.grid(column=0, row=2, padx=5, pady=(0, 5))

    #  Display the orientation out file path.
    orientation_out_label = ttk.Label(root, text="The orientation map can be found here:", wraplength=max_window_width,
                                      font=(None, 15), justify='center')
    orientation_out_label.grid(column=0, row=3, padx=5, pady=(5, 0))
    orientation_out_path_label = ttk.Label(root, text=str(orientation_out_path), wraplength=max_window_width,
                                           font=(None, 15, 'bold'), justify='center')
    orientation_out_path_label.grid(column=0, row=4, padx=5, pady=(0, 5))

    # Display messages thanking the user and prompting them to report any issues on GitHub.
    thanks_message_label = ttk.Label(root, text="Thank you for using pyTEM, please report any issues on GitHub:",
                                     wraplength=max_window_width, font=(None, 15), justify='center')
    thanks_message_label.grid(column=0, row=5, padx=5, pady=(5, 0))
    github_issues_label = ttk.Label(root, text="https://github.com/mrl280/pyTEM/issues", wraplength=max_window_width,
                                    font=(None, 15, 'bold'), justify='center')
    github_issues_label.grid(column=0, row=6, padx=5, pady=(0, 5))

    # Create exit button.
    exit_button = ttk.Button(root, text="Exit", command=lambda: sys.exit(0), style="big.TButton")
    exit_button.grid(column=0, row=7, padx=5, pady=5)
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    # Center the window on the screen
    root.eval('tk::PlaceWindow . center')

    root.mainloop()


if __name__ == "__main__":
    display_goodbye_message(anisotropy_out_path="Some fake anisotropy path...",
                            orientation_out_path="Some fake orientation path...")
