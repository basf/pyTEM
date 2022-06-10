"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""
import pathlib
from tkinter import TclError


def add_basf_icon_to_tkinter_window(root):
    """
    Add the BASF ico to root.
    :param root: tkinter window:
        The tkinter window of which you want to add the BASF icon.
    :return: None.
    """
    try:
        root.iconbitmap(pathlib.Path().resolve() / "ico" / "BASF.ico")
    except TclError:
        root.iconbitmap(pathlib.Path().resolve().parent.resolve() / "ico" / "BASF.ico")