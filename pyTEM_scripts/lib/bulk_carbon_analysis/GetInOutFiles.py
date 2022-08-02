"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import sys

import tkinter as tk

from tkinter import ttk, filedialog
from typing import Tuple
from pathlib import Path

from pyTEM_scripts.lib.micro_ed.add_basf_icon_to_tkinter_window import add_basf_icon_to_tkinter_window


class GetInOutFiles:
    """
    Display a Tkinter window to help the user:
        1. Select the 16 required natural light micrographs to use as input.
        2. Select output file names for the resultant anisotropy and orientation maps.

    Does nothing to verify in file type nor image order. For more info on how images should be ordered, read the docs:

        bulk_carbon_analysis --help

    """

    def __init__(self):
        self.in_files = ()
        self.out_directory = str(Path.home())

    def run(self) -> Tuple[Tuple, str, str]:
        """
        Get the in and out file paths.

        :return:
            in_files: Tuple of strings: Paths to the 16 light microscopy input files.
            anisotropy_out_file: str: Path to the destination where the user wants to store the resultant anisotropy
                map.
            orientation_out_file: str: Path to the destination where the user wants to store the resultant orientation
                map.
        """
        root = tk.Tk()
        style = ttk.Style()

        window_width = 500
        label_font = None  # Just use the default font.
        label_font_size = 12

        root.title("Bulk Carbon Analysis")
        add_basf_icon_to_tkinter_window(root)

        def get_in_files():
            """
            Have the user select the 16 natural light microscopy in files.
            :return: None, but the in_files attribute is updated with the paths to the selected files (as a tuple of
                strings).
            """
            # Open file explorer, prompting the user to select some files.
            leaf = tk.Tk()
            leaf.title("Please select all 16 light microscopy images.")
            add_basf_icon_to_tkinter_window(leaf)
            leaf.geometry("{width}x{height}".format(width=500, height=leaf.winfo_height()))
            in_files = filedialog.askopenfilenames()

            # Make sure we actually got an in file and the user didn't just cancel.
            if in_files not in {"", " "}:
                if len(in_files) == 16:
                    # Then we are good, update the in_file label with the currently selected list of files.
                    self.in_files = in_files

                    # Just print out the first and last file.
                    in_files_label.config(text=str(len(self.in_files)) + " files selected:")
                    in_files_label.configure(foreground="black")
                    list_of_in_files_label.config(text=self.in_files[0] + "\n" + "*" + "\n" + "*" + "\n" + "*"
                                                  + "\n" + self.in_files[-1])

                    # Suggest an outfile directory based on first input file.
                    self.out_directory = os.path.dirname(self.in_files[0])
                    anisotropy_out_directory_label.config(text=self.out_directory + "/")
                    orientation_out_directory_label.config(text=self.out_directory + "/")

                    # As long as we have an in-file, we are now okay to go ahead with the alignment.
                    go_button.config(state=tk.NORMAL)

                else:
                    # Remind the user that we are expecting exactly 16 files.
                    in_files_label.config(text="Error: " + str(len(self.in_files)) + " files selected, but we "
                                               "require exactly 16.")
                    in_files_label.config(foreground="red")
                    list_of_in_files_label.config(text="")
                    go_button.config(state=tk.DISABLED)

            else:
                pass  # Don't update self.in_files

            leaf.destroy()

        def change_out_directory():
            """
            Change/update the out directory.
            :return: None, but the out_directory attribute is updated with the new out directory of the users choosing.
            """
            leaf = tk.Tk()
            leaf.title("Please select an out directory.")
            add_basf_icon_to_tkinter_window(leaf)
            leaf.geometry("{width}x{height}".format(width=500, height=leaf.winfo_height()))

            self.out_directory = filedialog.askdirectory()
            anisotropy_out_directory_label.configure(text=self.out_directory + "/")
            orientation_out_directory_label.configure(text=self.out_directory + "/")
            leaf.destroy()

        in_file_message = ttk.Label(root, text="Which images would you like to align?", wraplength=window_width,
                                    justify='center', font=(label_font, label_font_size, 'bold'))
        in_file_message.grid(column=0, columnspan=3, row=0, padx=5, pady=5)

        # Create a button that, when clicked, will prompt the user to select the images they would like to align.
        select_in_files_button = ttk.Button(root, text="Select Light Microscopy Images", command=get_in_files,
                                            style="big.TButton")
        select_in_files_button.grid(column=0, columnspan=3, row=1, padx=5, pady=5)

        # We will display the selected in files here. At the beginning we will have no in files.
        in_files_label = ttk.Label(root, text="No files selected.", justify='center', wraplength=window_width,
                                   font=(label_font, label_font_size, 'bold'))
        in_files_label.configure(foreground="red")
        in_files_label.grid(column=0, columnspan=3, row=2, padx=5, pady=5)

        list_of_in_files_label = ttk.Label(root, text="", justify='center', wraplength=window_width,
                                           font=(label_font, label_font_size))
        list_of_in_files_label.grid(column=0, columnspan=3, row=3, padx=5, pady=5)

        # Create a label asking for the anisotropy out file.
        out_file_label = ttk.Label(root, text="Where would you like to save results?",
                                              justify='center', font=(label_font, label_font_size, 'bold'),
                                              wraplength=window_width)
        out_file_label.grid(column=0, columnspan=3, row=4, padx=5, pady=5)

        # Create a button that, when clicked, will update the out_file directory.
        out_file_button = ttk.Button(root, text="Update Out Directory", command=lambda: change_out_directory(),
                                     style="big.TButton")
        out_file_button.grid(column=0, columnspan=3, row=6, padx=5, pady=5)

        file_extension_options = ['.tif', '.mrc', '.png', '.jpeg']

        # Get the anisotropy out file path.
        anisotropy_out_file_label = ttk.Label(root, text="Anisotropy Map:", justify='center',
                                              font=(label_font, label_font_size - 2), wraplength=window_width)
        anisotropy_out_file_label.grid(column=0, columnspan=3, row=7, padx=5, pady=(5, 0))
        anisotropy_out_file = tk.StringVar()
        anisotropy_out_directory_label = ttk.Label(root, text=self.out_directory + "\\")
        anisotropy_out_directory_label.grid(column=0, row=8, sticky="e", padx=5, pady=(0, 5))
        anisotropy_out_file_entry_box = ttk.Entry(root, textvariable=anisotropy_out_file)
        anisotropy_out_file_entry_box.grid(column=1, row=8, padx=5, pady=(0, 5))
        anisotropy_out_file_entry_box.insert(0, "anisotropy_map")
        anisotropy_file_extension = tk.StringVar()
        anisotropy_file_extension_menu = ttk.OptionMenu(root, anisotropy_file_extension, file_extension_options[0],
                                                        *file_extension_options)
        anisotropy_file_extension_menu.grid(column=2, row=8, sticky="w", padx=5, pady=(0, 5))

        # Get the orientation out file path.
        orientation_out_file_label = ttk.Label(root, text="Orientation Map:", justify='center',
                                               font=(label_font, label_font_size - 2), wraplength=window_width)
        orientation_out_file_label.grid(column=0, columnspan=3, row=9, padx=5, pady=(5, 0))
        orientation_out_file = tk.StringVar()
        orientation_out_directory_label = ttk.Label(root, text=self.out_directory + "\\")
        orientation_out_directory_label.grid(column=0, row=10, sticky="e", padx=5, pady=(0, 5))
        orientation_out_file_entry_box = ttk.Entry(root, textvariable=orientation_out_file)
        orientation_out_file_entry_box.grid(column=1, row=10, padx=5, pady=(0, 5))
        orientation_out_file_entry_box.insert(0, "orientation_map")
        orientation_file_extension = tk.StringVar()
        orientation_file_extension_menu = ttk.OptionMenu(root, orientation_file_extension, file_extension_options[0],
                                                         *file_extension_options)
        orientation_file_extension_menu.grid(column=2, row=10, sticky="w", padx=5, pady=(0, 5))

        # Create go and exit buttons.
        go_button = ttk.Button(root, text="Go", command=lambda: root.destroy(), style="big.TButton")
        go_button.grid(column=0, columnspan=3, row=11, padx=5, pady=5)
        go_button.config(state=tk.DISABLED)
        exit_button = ttk.Button(root, text="Quit", command=lambda: sys.exit(0), style="big.TButton")
        exit_button.grid(column=0, columnspan=3, row=12, padx=5, pady=5)

        style.configure('big.TButton', font=(None, 10), foreground="blue4")
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        root.mainloop()

        # Build and return the complete path
        full_anisotropy_out_path = self.out_directory + "/" + str(anisotropy_out_file.get()) \
            + str(anisotropy_file_extension.get())
        full_orientation_out_path = self.out_directory + "/" + str(anisotropy_out_file.get()) \
            + str(orientation_file_extension.get())
        return self.in_files, full_anisotropy_out_path, full_orientation_out_path


if __name__ == "__main__":
    in_files_, anisotropy_out_path, orientation_out_path = GetInOutFiles().run()

    if isinstance(in_files_, Tuple):
        print("Received " + str(len(in_files_)) + " in files:")
        for file in in_files_:
            print(file)

    else:
        raise Exception("Error: in_files is not a Tuple.")

    print("\nAnisotropy out file path: " + anisotropy_out_path)
    print("\nOrientation out file path: " + orientation_out_path)
