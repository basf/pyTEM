"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""


class StagePosition:
    """
    A simplified, forward facing StagePosition class.

    Private Attributes:
        __x:      float:  The current stage position along the x-axis, in micrometres.
        __y:      float:  The current stage position along the y-axis, in micrometres.
        __z:      float:  The current stage position along the z-axis, in micrometres.
        __alpha:  float:  The current stage tilt along the alpha direction, in degrees.
        __beta:   float:  The current stage tilt along the beta direction, in degrees.
    """

    def __init__(self, x, y, z, alpha, beta):
        self.__x = x
        self.__y = y
        self.__z = z
        self.__alpha = alpha
        self.__beta = beta

    def get_x(self):
        """
        :return: float: The current stage position along the x-axis, in micrometres.
        """
        return self.__x

    def get_y(self):
        """
        :return: float: The current stage position along the y-axis, in micrometres.
        """
        return self.__y

    def get_z(self):
        """
        :return: float: The current stage position along the z-axis, in micrometres.
        """
        return self.__z

    def get_alpha(self):
        """
        :return: float: The current stage tilt along the alpha direction, in degrees.
        """
        return self.__alpha

    def get_beta(self):
        """
        :return: float: The current stage tilt along the beta direction, in degrees.
        """
        return self.__beta

    def set_x(self, new_x):
        """
        Update the current stage position along the x-axis, in micrometres.
        Notice that since this does nothing to update the microscope's internal (Thermo-Fisher's) StagePosition object,
         utilization of this method will not affect the microscope.
        """
        self.__x = new_x

    def set_y(self, new_y):
        """
        Update the current stage position along the y-axis, in micrometres.
        Notice that since this does nothing to update the microscope's internal (Thermo-Fisher's) StagePosition object,
         utilization of this method will not affect the microscope.
        """
        self.__y = new_y

    def set_z(self, new_z):
        """
        Update the current stage position along the z-axis, in micrometres.
        Notice that since this does nothing to update the microscope's internal (Thermo-Fisher's) StagePosition object,
         utilization of this method will not affect the microscope.
        """
        self.__z = new_z

    def set_alpha(self, new_alpha):
        """
        Update the current stage tilt along the alpha direction, in degrees.
        Notice that since this does nothing to update the microscope's internal (Thermo-Fisher's) StagePosition object,
         utilization of this method will not affect the microscope.
        """
        self.__alpha = new_alpha

    def set_beta(self, new_beta):
        """
        Update the current stage tilt along the beta direction, in degrees.
        Notice that since this does nothing to update the microscope's internal (Thermo-Fisher's) StagePosition object,
         utilization of this method will not affect the microscope.
        """
        self.__beta = new_beta
