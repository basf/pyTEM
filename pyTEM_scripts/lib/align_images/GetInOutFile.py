"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import os
import sys

import tkinter as tk

from tkinter import ttk, filedialog
from typing import Tuple, Union
from pathlib import Path

from pyTEM_scripts.lib.micro_ed import add_basf_icon_to_tkinter_window


class GetInOutFile:
    """
    Display a Tkinter window, and get the in and out file info from the user.

    Does nothing to verify file type.
    """

    def __init__(self):
        self.in_file = ""
        self.out_directory = str(Path.home())

    def run(self) -> Tuple[Union[str, Tuple[str]], str]:
        """
        Get the in and out file paths.

        :return:
            in_file: str or tuple of strings: Path(s) to the file(s) containing the image(s) or image stack that the
                        user wants to read in and align.
            out_file: str: Path to the destination where the user wants to store the file containing the aligned
                        image stack.
        """
        root = tk.Tk()
        style = ttk.Style()

        window_width = 500
        label_font = None  # Just use the default font
        label_font_size = 12

        root.title("Align Images")
        add_basf_icon_to_tkinter_window(root)

        def get_single_in_file():
            """
            Have the user select a single file.
            :return: None, but the in_file attribute is updated with the path to the selected file (as a string).
            """
            # Open file explorer, prompting the user to select a file.
            leaf = tk.Tk()
            leaf.title("Please select a single file containing an image stack you would like to align.")
            add_basf_icon_to_tkinter_window(leaf)
            leaf.geometry("{width}x{height}".format(width=500, height=leaf.winfo_height()))
            self.in_file = filedialog.askopenfilename()

            # Make sure we actually got an in file and the user didn't cancel
            if self.in_file not in {"", " "}:
                # Update the in_file label with the currently selected file.
                in_file_label.config(text="1 file selected:")
                list_of_in_files_label.config(text=self.in_file)
                in_file_label.configure(foreground="black")

                # Suggest an outfile directory based on the input directory.
                self.out_directory = os.path.dirname(self.in_file)
                out_directory_label.config(text=self.out_directory + "/")

                # Suggest an out file to have the same name as the in file.
                suggested_out_file_name, _ = os.path.splitext(os.path.basename(self.in_file))
                out_file_name_entry_box.delete(0, tk.END)
                out_file_name_entry_box.insert(0, str(suggested_out_file_name) + "_aligned")

                # As long as we have an in-file, we are now okay to go ahead with the alignment.
                go_button.config(state=tk.NORMAL)

            leaf.destroy()

        def get_multiple_in_files():
            """
            Have the user select multiple files.
            :return: None, but the in_file attribute is updated with the path to the selected files (as a tuple of
                        strings)
            """
            # Open file explorer, prompting the user to select some files.
            leaf = tk.Tk()
            leaf.title("Please select the images you would like to align.")
            add_basf_icon_to_tkinter_window(leaf)
            leaf.geometry("{width}x{height}".format(width=500, height=leaf.winfo_height()))
            self.in_file = filedialog.askopenfilenames()

            # Make sure we actually got an in file and the user didn't cancel
            if self.in_file not in {"", " "}:
                # Update the in_file label with the currently selected list of files.
                if len(self.in_file) == 1:
                    in_file_label.config(text="1 file selected:")
                    list_of_in_files_label.config(text=self.in_file[0])
                elif len(self.in_file) == 2:
                    in_file_label.config(text="2 files selected:")
                    list_of_in_files_label.config(text=self.in_file[0] + "\n" + self.in_file[1])
                else:
                    # Just print out the first and last file.
                    in_file_label.config(text=str(len(self.in_file)) + " files selected:")
                    list_of_in_files_label.config(text=self.in_file[0] + "\n" + "*" + "\n" + "*" + "\n" + "*"
                                                  + "\n" + self.in_file[-1])
                in_file_label.configure(foreground="black")

                # Suggest an outfile directory based on first input file.
                self.out_directory = os.path.dirname(self.in_file[0])
                out_directory_label.config(text=self.out_directory + "/")

                # Suggest an out file name based on the first file in the series.
                suggested_out_file_name, _ = os.path.splitext(os.path.basename(self.in_file[0]))
                out_file_name_entry_box.delete(0, tk.END)
                out_file_name_entry_box.insert(0, str(suggested_out_file_name) + "_aligned")

                # As long as we have an in-file, we are now okay to go ahead with the alignment.
                go_button.config(state=tk.NORMAL)

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
            out_directory_label.configure(text=self.out_directory + "/")
            leaf.destroy()

        in_file_message = ttk.Label(root, text="Which images would you like to align?", wraplength=window_width,
                                    justify='center', font=(label_font, label_font_size, 'bold'))
        in_file_message.grid(column=0, columnspan=3, row=0, padx=5, pady=5)

        # Create a button that, when clicked, will prompt the user to select a single file containing the image
        #  stack that would like to align.
        single_in_file_button = ttk.Button(root, text="Select a Single Image Stack",
                                           command=lambda: get_single_in_file(), style="big.TButton")
        single_in_file_button.grid(column=0, columnspan=3, row=1, padx=5, pady=5)

        # Create a button that, when clicked, will prompt the user to select the images they would like to align.
        multiple_in_file_button = ttk.Button(root, text="Select Multiple Single Image Files",
                                             command=lambda: get_multiple_in_files(), style="big.TButton")
        multiple_in_file_button.grid(column=0, columnspan=3, row=2, padx=5, pady=5)

        # Display the in file
        in_file_label = ttk.Label(root, text="No files selected.", justify='center', wraplength=window_width,
                                  font=(label_font, label_font_size, 'bold'))
        in_file_label.configure(foreground="red")
        in_file_label.grid(column=0, columnspan=3, row=3, padx=5, pady=5)

        list_of_in_files_label = ttk.Label(root, text="", justify='center', wraplength=window_width,
                                           font=(label_font, label_font_size))
        list_of_in_files_label.grid(column=0, columnspan=3, row=4, padx=5, pady=5)

        out_file_message = ttk.Label(root, text="Where would you like to save the results?", justify='center',
                                     font=(label_font, label_font_size, 'bold'), wraplength=window_width)
        out_file_message.grid(column=0, columnspan=3, row=5, padx=5, pady=5)

        # Create a button that, when clicked, will update the out_file directory
        out_file_button = ttk.Button(root, text="Update Out Directory", command=lambda: change_out_directory(),
                                     style="big.TButton")
        out_file_button.grid(column=0, columnspan=3, row=6, padx=5, pady=5)

        # Label the filename box with the out directory
        out_directory_label = ttk.Label(root, text=self.out_directory + "\\")
        out_directory_label.grid(column=0, row=7, sticky="e", padx=5, pady=5)

        # Create an entry box for the user to enter the out file name.
        out_file_name = tk.StringVar()
        out_file_name_entry_box = ttk.Entry(root, textvariable=out_file_name)
        out_file_name_entry_box.grid(column=1, row=7, padx=5, pady=5)

        # Add a dropdown menu to get the file extension
        file_extension_options = ['.tif', '.mrc']
        file_extension = tk.StringVar()
        file_extension_menu = ttk.OptionMenu(root, file_extension, file_extension_options[0], *file_extension_options)
        file_extension_menu.grid(column=2, row=7, sticky="w", padx=5, pady=5)

        # Create go and exit buttons
        go_button = ttk.Button(root, text="Go", command=lambda: root.destroy(), style="big.TButton")
        go_button.grid(column=0, columnspan=3, row=8, padx=5, pady=5)
        go_button.config(state=tk.DISABLED)
        exit_button = ttk.Button(root, text="Quit", command=lambda: sys.exit(), style="big.TButton")
        exit_button.grid(column=0, columnspan=3, row=9, padx=5, pady=5)

        style.configure('big.TButton', font=(None, 10), foreground="blue4")
        root.eval('tk::PlaceWindow . center')  # Center the window on the screen

        root.mainloop()

        # Build and return the complete path
        out_path = self.out_directory + "/" + str(out_file_name.get()) + str(file_extension.get())
        return self.in_file, out_path


if __name__ == "__main__":
    in_file, out_file = GetInOutFile().run()

    if isinstance(in_file, str):
        print("Received a single in file: " + in_file)

    elif isinstance(in_file, Tuple):
        print("Received multiple in files:")
        for file in in_file:
            print(file)

    else:
        raise Exception("Error: in_file type not recognized.")

    print("\nOut file: " + out_file)
