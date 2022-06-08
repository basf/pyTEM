import tkinter as tk
from tkinter import ttk


def hello_world():
    """

    """
    root = tk.Tk()
    root.title("Willkommen!")

    welcome_message = "Welcome to the micro electron diffraction (MicroED) automated imaging software. " \
                      "MicroED allows fast, high resolution 3D structure determination of small chemical compounds " \
                      "biological macromolecules!"

    window_width = 600
    window_height = 300

    # get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # find the center point
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    # set the position of the window to the center of the screen
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # root.iconbitmap("../.ico")

    message = ttk.Label(root, text=welcome_message, wraplength=window_width, font=("Arial", 25))

    # tk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

    exit_button = ttk.Button(root, text="Quit", command=lambda: root.quit())
    message.pack(ipadx=5, ipady=5, expand=True)
    exit_button.pack(ipadx=5, ipady=5, expand=True)

    root.mainloop()


if __name__ == "__main__":
    hello_world()
