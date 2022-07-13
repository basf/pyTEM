"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""


def tem_tilt_speed(speed_deg_per_s: float) -> float:
    """
    Convert from tilt speed in degrees per second to the TEM fractional tilt speed required by
     Interface.set_stage_position().

    :param speed_deg_per_s: float:
        Tilt speed, in degrees per second.

    :return: float:
        The equivalent TEM fractional tilt speed required by Interface.set_stage_position().
    """

    if speed_deg_per_s > 15:
        raise Exception("The microscope's maximum tilt speed is 15 deg / s.")

    elif speed_deg_per_s > 1.5:
        # This conversion works well for larger tilting speeds, R^2 = 0.99985445
        return 0.000267533 * (speed_deg_per_s ** 3) \
               - 0.002387867 * (speed_deg_per_s ** 2) \
               + 0.043866877 * speed_deg_per_s \
               - 0.004913243  # Notice that the non-zero y-intercepts are likely due to a constant delay

    elif speed_deg_per_s <= 0.000376177 / 0.034841591:
        raise Exception("The microscope's minimum tilt speed is 0.02 deg / s.")

    else:
        # This conversion works well for low tilt speeds where the relationship is ~linear, R^2 = 0.999982772
        return 0.034841591 * speed_deg_per_s \
               - 0.000376177  # Notice that the non-zero y-intercepts are likely due to a constant delay

