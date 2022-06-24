"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
import tkinter as tk
from tkinter import TclError


def add_basf_icon_to_tkinter_window(root: tk.Tk()) -> None:
    """
    Add the BASF ico to root.
    :param root: tkinter window:
        The tkinter window of which you want to add the BASF icon.
    :return: None.
    """
    try:
        root.iconbitmap(pathlib.Path().resolve() / "lib" / "ued" / "ico" / "BASF.ico")
    except TclError:
        root.iconbitmap(pathlib.Path().resolve().parent.resolve() / "lib" / "ued" / "ico" / "BASF.ico")
