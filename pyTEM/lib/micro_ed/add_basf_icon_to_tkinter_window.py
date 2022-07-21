"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import tkinter as tk
BASEDIR = os.path.dirname(os.path.abspath(__file__))


def add_basf_icon_to_tkinter_window(root: tk.Tk) -> None:
    """
    Add the BASF ico to Tkinter window.
    :param root: tkinter window:
        The tkinter window of which you want to add the BASF icon.
    :return: None.
    """
    path_to_ico = os.path.join(BASEDIR, "ico\\BASF.ico")
    print("Path to ico: " + str(path_to_ico))
    print(type(path_to_ico))
    root.iconbitmap(path_to_ico)
