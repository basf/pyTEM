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


def display_goodbye_message(out_path: Union[pathlib.Path, str]):
    """
    Display a goodbye message,
        - thanking the user,
        - letting them know where to find the alignment results,
        - and prompting them to report any issues on the GitHub.

    :param out_path: str or path:
        Path to the alignment results.

    :return: None.
    """
    root = tk.Tk()
    style = ttk.Style()
    window_width = 650

    root.title("Mission success!")
    add_basf_icon_to_tkinter_window(root)

    upper_message = "Image Alignment Successful!" \
                    "\n\nThe results can be found here:"
    lower_message = "Thank you for using pyTEM, please report any issues on GitHub:"

    # Display the upper part of the message.
    upper_message_label = ttk.Label(root, text=upper_message, wraplength=window_width, font=(None, 15),
                                    justify='center')
    upper_message_label.grid(column=0, row=0, padx=5, pady=(5, 0))

    # Display the out file path.
    out_path_label = ttk.Label(root, text=out_path, wraplength=window_width, font=(None, 15, 'bold'),
                               justify='center')
    out_path_label.grid(column=0, row=1, padx=5, pady=(0, 5))

    # Display the lower part of the message.
    upper_message_label = ttk.Label(root, text=lower_message, wraplength=window_width, font=(None, 15),
                                    justify='center')
    upper_message_label.grid(column=0, row=2, padx=5, pady=(5, 0))

    # Display the link to the GitHub issues board.
    github_issues_label = ttk.Label(root, text="https://github.com/mrl280/pyTEM/issues", wraplength=window_width,
                                    font=(None, 15, 'bold'), justify='center')
    github_issues_label.grid(column=0, row=3, padx=5, pady=(0, 5))

    # Create exit button.
    exit_button = ttk.Button(root, text="Exit", command=lambda: sys.exit(0), style="big.TButton")
    exit_button.grid(column=0, row=4, padx=5, pady=5)
    style.configure('big.TButton', font=(None, 10), foreground="blue4")

    # Center the window on the screen
    root.eval('tk::PlaceWindow . center')

    root.mainloop()


if __name__ == "__main__":
    display_goodbye_message(out_path="Some fake path...")
