import math


def pascal_to_log(pressure_in_pascals):
    """
    Convert pressures from pascals into log units. Log units are defined in such a way that a realistic range of
     pressures (for that vacuum element) goes from 0 to 100. The advantage of the log units is simplicity and high
     sensitivity for the good vacuum values (where it matters) and low sensitivity for poor vacuum values (where it
     doesn't).

    :param pressure_in_pascals: float:
        A pressure value, in pascals.

    :return: pressure_in_log_units: float:
        The provided pressure value, converted into log units.
    """
    # Note: math.log() is a natural logarithm.
    # TODO: Ask where this conversion can from, because it doesn't seem to be quite right
    return 3.5683 * math.log(pressure_in_pascals) + 53.497
