"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import pathlib
import tkinter as tk
from tkinter import TclError


def add_basf_icon_to_tkinter_window(root: tk.Tk) -> None:
    """
    Add the BASF ico to root.
    :param root: tkinter window:
        The tkinter window of which you want to add the BASF icon.
    :return: None.
    """
    try:
        # Calling from within pyTEM
        root.iconbitmap(pathlib.Path().resolve() / "lib" / "ued" / "ico" / "BASF.ico")
    except TclError:
        try:
            # Calling from within pyTEM.lib
            root.iconbitmap(pathlib.Path().resolve().parent.resolve() / "ued" / "ico" / "BASF.ico")
        except TclError:
            # Calling from somewhere in test
            root.iconbitmap(pathlib.Path().resolve().parent.resolve().parent.resolve() / "pyTEM" / "lib" / "ued" / "ico" / "BASF.ico")