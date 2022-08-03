import warnings
from pyTEM_scripts.lib.controller.XboxController import XboxController
from pyTEM.Interface import Interface


class Adapter():


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
        cx = self.tem.get_stage_position()['x']
        cy = self.tem.get_stage_position()['y']
        self.tem.set_stage_position(x = offset_x + cx, y = offset_y + cy)


    def z(self, offset_z_down, offset_z_up):
        cz = self.tem.get_stage_position()['z']

        # SetZ = (joy.read()[4]*10**(-6)) + Cz
        # SetZ = (joy.read()[5]*10**(-6)) - Cz
        self.tem.set_stage_position(z = offset_z_down - cz)


    def reset(self):
        self.tem.set_stage_position(x = 0, y = 0)
        print('STAGE RESET!')