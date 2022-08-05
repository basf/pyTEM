"""
 Author:  Jason Kobel
 Date:    Summer 2022
"""

import warnings
from pyTEM.Interface import Interface


class Adapter():
    """
    Connection to the TEM
    """


    def __init__(self):
        # Try to connect to a microscope
        try:
            self.tem = Interface()
            print("Microscope connection established successfully.")
        except BaseException as e:
            warnings.warn("MicroED was unable to connect to a microscope, try (re)connecting with MicroED.connect(). "
                          "\nError details:" + str(e))
            self.tem = None


    def xy(self, offset_x, offset_y):
        cx = self.tem.get_stage_position()['Cx']
        cy = self.tem.get_stage_position()['y']
        self.tem.set_stage_position(x = offset_x + cx, y = offset_y + cy)


    def down(self, offset_z_down):
        cz = self.tem.get_stage_position()['z']
        self.tem.set_stage_position(z = offset_z_down - cz)

    def up(self, offset_z_up):
        cz = self.tem.get_stage_position()['z']
        self.tem.set_stage_position(z = offset_z_up + cz)


    def reset(self):
        self.tem.set_stage_position(x = 0, y = 0)
        print('STAGE RESET!')
