"""
 Author:  Jason Kobel
 Date:    Summer 2022
"""

import argparse
from pyTEM_scripts.lib.controller.XboxController import XboxController
from pyTEM_scripts.lib.controller.Adapter import Adapter


DESCRIPTION = "Xbox Script"


def controller():
    joy = XboxController()
    adapter = Adapter()
    while True:
        if (joy.read()[10] and joy.read()[11]) == 1:
            adapter.reset()

        if (joy.read()[0] or joy.read()[1]) != 0:
            offset_x = (joy.read()[0]*10**(-6)) 
            offset_y = (joy.read()[1]*10**(-6)) 
            adapter.xy(offset_x, offset_y)

        if (joy.read()[4]) != 0:
            offset_z_down = (joy.read()[4]*10**(-6))
            adapter.down(offset_z_down)
       
        if (joy.read()[5]) != 0:
            offset_z_up = (joy.read()[5]*10**(-6))
            adapter.up(offset_z_up)


def script_entry():
    """
    Entry point for Align Images script. Once pyTEM is installed, view script usage by running the following
     command in a terminal window:

        align_images --help

    """
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.parse_args()
    controller()


if __name__ == "__main__":
    controller()
