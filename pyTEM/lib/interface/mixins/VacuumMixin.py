"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import comtypes.client as cc

from pyTEM.lib.interface.pascal_to_log import pascal_to_log  # Requires the pyTEM package directory on path


class VacuumMixin:
    """
    Microscope vacuum system valve controls and pressure reports.

    This mixin was developed in support of pyTEM.pyTEM, but can be included in other projects where helpful.
    """
    _tem: type(cc.CreateObject("TEMScripting.Instrument"))

    def _pull_vacuum_info(self):
        """
        Pull vacuum info from the microscope and, from this info, build and return a dictionary (keyed by integers)
         containing 3-element lists with gauge names, pressures in Pascals, and pressures in log units.

        :return: Vacuum info: dictionary:
           Keys are integers, 3-element lists containing gauge name, pressure in Pascals, and pressure in log units.
        """
        # The gauge objects are used to retrieve information about the vacuum system measurement devices and
        #  the actual pressures measured with them.
        gauges = self._tem.Vacuum.Gauges
        gauge_names = ['IGPa (accelerator)', 'IGPco (column)', 'PIRco (detector)',
                       'PPm (sample airlock)', 'IGPf (electron gun)']

        # Build a dictionary with the gauge name, pressure in Pascals, and pressure in log units.
        pressure_dictionary = dict()
        for i in range(len(gauges)):
            pressure_dictionary.update({i: [gauge_names[i], gauges[i].Pressure, pascal_to_log(gauges[i].Pressure)]})

        return pressure_dictionary

    def print_vacuum_info(self):
        """
        Print out the vacuum info in a table-like format:
            Gauge     Pressure [Pa]     Pressure [Log]

        :return: None.
        """
        pressure_info = self._pull_vacuum_info()

        print("{:<25} {:<20} {:<20}".format('Gauge', 'Pressure [Pa]', 'Pressure [Log]'))  # Table header
        for key, value in pressure_info.items():
            name, pressure_in_pascals, pressure_in_log = value
            print("{:<25} {:<20} {:<20}".format(name, '{:0.3e}'.format(pressure_in_pascals), round(pressure_in_log, 3)))

    def get_accelerator_vacuum(self, units="log"):
        """
        Obtain the vacuum level up on the outside of the gun.
        :param units: string:
            The units of the returned accelerator gauge pressure. Either "Pascal" or "log".
        :return: float:
            The current accelerator gauge pressure, in the requested units.
        """
        gauge_name, pressure_in_pascals, pressure_in_log = self._pull_vacuum_info()[0]
        units = str(units).lower()

        if units in {"log", "logs"}:
            return pressure_in_log
        elif units in {"pascal", "pascals"}:
            return pressure_in_pascals
        else:
            print("Error getting accelerator vacuum: units '" + units + "' not recognized.")
            return math.nan

    def get_column_vacuum(self, units="log"):
        """
        Obtain the vacuum the main section of the microscope with the sample, lenses, etc.
        :param units: string:
            The units of the returned column gauge pressure. Either "Pascal" or "log".
        :return: float:
            The current column gauge pressure, in the requested units.
        """
        gauge_name, pressure_in_pascals, pressure_in_log = self._pull_vacuum_info()[1]
        units = str(units).lower()

        if units in {"log", "logs"}:
            return pressure_in_log
        elif units in {"pascal", "pascals"}:
            return pressure_in_pascals
        else:
            print("Error getting column vacuum: units '" + units + "' not recognized.")
            return math.nan

    def column_under_vacuum(self):
        """
        This function checks to make sure the column is under vacuum.

        This is a safety check. Since a loss of vacuum can damage the electron gun, there is a valve (column value)
         separating the 'accelerator' and 'column' sections of the instrument. If there is a leak, it usually starts at
         the column, causing the vacuum pressure to increase first in this section.

        :return: bool:
            True: The column is under vacuum (it is therefore safe to open the column valve and take images).
            False: The column is not under vacuum (the column valve must remain closed to protect the electron gun).
        """
        if 0 < self.get_column_vacuum(units="log") < 20:
            # The TEM usually operates with a column vacuum around 15 Log, but anything under 20 Log should be okay.
            return True
        else:
            return False  # Unsafe

    def get_column_valve_position(self):
        """
        :return: str:
            The current column value position, either "Open" or "Closed".
            The column value should always be closed when the microscope is not in use.
        """
        if self._tem.Vacuum.ColumnValvesOpen:
            return "Open"
        else:
            return "Closed"

    def close_column_valve(self):
        """
        Close the column value.
        :return: None.
        """
        if self.get_column_valve_position().lower() == "closed":
            print("The column value is already closed.. no changes made.")
            return

        self._tem.Vacuum.ColumnValvesOpen = False

    def open_column_valve(self):
        """
        Open the column valve (if it is safe to do so).
        :return: None
        """
        if self.column_under_vacuum():
            # The column is under vacuum, it is safe to open the value up to the accelerator.
            self._tem.Vacuum.ColumnValvesOpen = True

        else:
            print("The column value cannot be safely opened because the column isn't under sufficient vacuum. "
                  "Please check the TEM.")

    def print_vacuum_status(self):
        """
        Print out the current vacuum status, along with a 'helpful' description.
        :return: None
        """
        vacuum_status = self._tem.Vacuum.Status
        if vacuum_status == 1:
            print("vsUnknown (1): Status of vacuum system is unknown.")
        elif vacuum_status == 2:
            print("vsOff (2): Vacuum system is off.")
        elif vacuum_status == 3:
            print("vsCameraAir (3): Camera (only) is aired.")
        elif vacuum_status == 4:
            print("vsBusy (4): Vacuum system is busy, that is: on its way to ‘Ready’, ‘CameraAir’, etc.")
        elif vacuum_status == 5:
            print("vsReady (5): Vacuum system is ready.")
        elif vacuum_status == 6:
            print("vsElse (6): Vacuum is in any other state (gun air, all air etc.), and will not come back to ready "
                  "without any further action of the user.")
        else:
            raise Exception("Vacuum Status '" + str(vacuum_status) + "' not recognized.")
