"""
 Author:  Michael Luciuk
 Date:    Summer 2022
"""

import math
import copy
import warnings
from typing import Tuple

import comtypes.client as cc

from pyTEM.lib.StagePosition import StagePosition  # Requires the pyTEM package directory on path


# TODO: Compute min and max stage movement speeds along x, y and z

class StageMixin:
    """
    Microscope stage controls, including those for getting and setting the stage position. Also, helpful stage status
     print functions.

    This mixin was developed in support of pyTEM.Interface, but can be included in other projects where helpful.
    """
    try:
        # Unresolved attribute warning suppression
        _tem: type(cc.CreateObject("TEMScripting.Instrument"))
    except OSError:
        pass

    def get_stage_position(self) -> StagePosition:
        """
        :return: StagePosition:
            A deep copy of current stage position. Modifying the returned object will not affect the microscope.
        """
        return copy.deepcopy(self._stage_position)

    def set_stage_position(self, stage_position_obj: StagePosition = None,
                           x: float = None, y: float = None, z: float = None, alpha: float = None, beta: float = None,
                           speed: float = 1.0, movement_type: str = "go"):
        """
        Update the microscope stage position using an pyTEM.lib.StagePosition object.

        Optionally, the stage can be updated with individual x, y, z, alpha, and beta values. However, these values will
         only be used if no pyTEM.lib.StagePosition object is provided.

        To avoid ambiguity and type errors, please call using keyword arguments of the form kwarg=value.

        Note: I tried to refactor this into two separate methods using pythonlangutil.overload. However, I was unable to
         handle optional parameters.

        :param stage_position_obj: StagePosition object:
            The new stage position.
        :param x: float:
            The new stage position along the x-axis, in micrometres.
        :param y: float:
            The new stage position along the y-axis, in micrometres.
        :param z: float:
            The new stage position along the z-axis, in micrometres.
        :param alpha: float:
            The new stage tilt in the alpha direction, in degrees.
        :param beta: float:
            The new stage tilt in the beta direction, in degrees.

        :param speed: float (optional; default is 1.0):
            The fraction of the standard speed setting with which to move the stage.
            Hint: use pyTEM.lib.interface.tem_tilt_speed() to convert from degrees-per-second to fractional microscope
             speed.
            Some examples:
                1.0: Move with 100% of the standard microscope speed (maximum speed; for tilting this is about
                 15 deg / s).
                0.6: Move with 60% of the standard microscope speed.
                0.00032: move with 0.032% of the standard microscope speed (minimum speed; for tilting this is about
                 0.02 deg / s).
        :param movement_type: string (optional; default is "go"):
            The TEM supports two movement types:
                "go": the instrument stage will move directly from the old position to the new position.
                "move": any existing tilts will be zeroed, then the instrument will move to the new position, then the
                 tilts will be restored or updated. This ensures that all possible positions can be reached without
                 touching the objective pole, but is not good for tilting experiments. Also, move does not allow for
                 variable speed. Therefore, the speed parameter will be ignored when movement_type="move".

        :return: None.
        """
        if speed > 1.0:
            print("Microscope speed cannot exceed 1.0 (100% of the standard microscope speed; about 15 deg / s), "
                  "moving the stage with speed 1.0...")
            speed = 1.0

        if speed < 0.00032:
            print("Microscope speed must exceed 0.00032 (0.032% of the standard microscope speed; about 0.02 deg / s), "
                  "moving the stage with speed 0.00032...")
            speed = 0.00032

        movement_type = str(movement_type).lower()
        if movement_type not in {"go", "move"}:
            print("Movement type '" + movement_type + "' not recognized.. no changes made.")
            return

        if movement_type == "move" and speed != 1.0:
            warnings.warn(message="We are moving with movement type 'move', therefore the speed parameter is being "
                                  "ignored and the stage is being moved at 100% standard microscope speed.")

        if self._tem.Stage.Status != 0:
            print("The stage is not ready to move. Rather, the current stage status is:")
            self.print_stage_status()
            print("No changes made..")
            return

        if stage_position_obj is not None:
            # Update x, y, z, and alpha using the provided StagePosition object.
            current_stage_position = self.get_stage_position()

            x = stage_position_obj.get_x()
            if math.isclose(current_stage_position.get_x(), x, abs_tol=1e-5):
                x = None  # No change requested in x direction

            y = stage_position_obj.get_y()
            if math.isclose(current_stage_position.get_y(), y, abs_tol=1e-5):
                y = None  # No change required in y direction

            z = stage_position_obj.get_z()
            if math.isclose(current_stage_position.get_z(), z, abs_tol=1e-5):
                z = None  # No change required in z direction

            alpha = stage_position_obj.get_alpha()
            if math.isclose(current_stage_position.get_alpha(), alpha, abs_tol=1e-5):
                alpha = None  # No change required in alpha direction

            beta = stage_position_obj.get_beta()
            if math.isclose(current_stage_position.get_beta(), beta, abs_tol=1e-5):
                beta = None  # No change required in beta direction

        stage = self._tem.Stage
        new_position = self._tem.Stage.Position  # Just for the object template

        # Note: The following movements are handled individually suppress unnecessary movements of the holder due
        #  to fluctuations in position measurement.

        if x is not None:
            if abs(x) > 1000:
                print("Allowable x values range from -1,000 \u03BCm to 1,000 \u03BCm.")
                print("The provided x value (" + str(x) + " \u03BCm) doesn't fall within this range."
                      "Therefore, the requested x-axis movement was not performed.")
                return

            # Move along the x-axis (1) to the specified x position.
            new_position.X = x / 1e6  # um -> m
            if movement_type == "go":
                stage.GoToWithSpeed(new_position, 1, speed)
            else:  # move
                stage.MoveTo(new_position, 1)

        if y is not None:
            if abs(y) > 1000:
                print("Allowable y values range from -1,000 \u03BCm to 1,000 \u03BCm.")
                print("The provided y value (" + str(y) + " \u03BCm) doesn't fall within this range. "
                      "Therefore, the requested y-axis movement was not performed.")
                return

            # Move along the y-axis (2) to the specified y position.
            new_position.Y = y / 1e6  # um -> m
            if movement_type == "go":
                stage.GoToWithSpeed(new_position, 2, speed)  # change the y position; 2 -> y-axis
            else:  # move
                stage.MoveTo(new_position, 2)

        if z is not None:
            if abs(z) > 375:
                print("Allowable z values range from -375 \u03BCm to 375 \u03BCm.")
                print("The provided z value (" + str(z) + " \u03BCm) doesn't fall within this range. "
                      "Therefore, the requested z-axis movement was not performed.")
                return

            # Move along the z-axis (4) to the specified z position.
            new_position.Z = z / 1e6  # um -> m
            if movement_type == "go":
                stage.GoToWithSpeed(new_position, 4, speed)
            else:  # move
                stage.MoveTo(new_position, 4)

        if alpha is not None:
            if abs(alpha) > 80:
                print("Allowable alpha values range from -80 degrees to 80 degrees.")
                print("The provided alpha value (" + str(alpha) + " degrees) doesn't fall within this range. "
                      "Therefore, the requested \u03B2 tilt was not performed.")
                return

            # Tilt along the alpha-axis (8) to the specified alpha position.
            new_position.A = math.radians(alpha)  # deg -> rad
            if movement_type == "go":
                stage.GoToWithSpeed(new_position, 8, speed)
            else:
                stage.MoveTo(new_position, 8)

        if beta is not None:
            if self._tem.Stage.Holder != 2:
                print("Error: The current stage holder does not support beta tilt:")
                self.print_stage_holder_type()
                print("The requested \u03B2 tilt was not performed.")

            else:
                if abs(beta) > 29.7:
                    print("Allowable beta values range from -29.7 degrees to 29.7 degrees.")
                    print("The provided beta value (" + str(beta) + " degrees) doesn't fall within this range. "
                          "Therefore, the requested \u03B2 tilt was not performed.")
                    return

                # Tilt along the beta-axis (16) to the specified beta position.
                new_position.B = math.radians(beta)  # deg -> rad
                if movement_type == "go":
                    if speed < 1.0:
                        # TODO: Test to see if Beta tilt supports variable speed
                        warnings.warn(message="Beta tilt does not support variable speed, we are tilting at 100% "
                                              "standard microscope speed.")
                    stage.GoTo(new_position, 16)
                else:
                    stage.MoveTo(new_position, 16)

        self._update_stage_position()  # Update the forward facing stage object

    def _update_stage_position(self) -> None:
        """
        Update the internal stage position object. This is required whenever the stage is moved.
        :return: None.
        """
        scope_position = self._tem.Stage.Position  # ThermoFisher StagePosition object
        self._stage_position = StagePosition(x=scope_position.X * 1e6,  # m -> um
                                             y=scope_position.Y * 1e6,  # m -> um
                                             z=scope_position.Z * 1e6,  # m -> um
                                             alpha=math.degrees(scope_position.A),  # rad -> deg
                                             beta=math.degrees(scope_position.B))  # rad -> deg

    def get_stage_position_x(self) -> float:
        """
        :return: float: The current stage position along the x-axis, in micrometres.
        """
        self._update_stage_position()  # Encase something external caused the stage to move.
        return self._stage_position.get_x()

    def set_stage_position_x(self, x: float, speed: float = 1.0, movement_type: str = "go") -> None:
        """
        :param x: float:
            The new stage position along the x-axis, in micrometres.

        :param speed: float (optional; default is 1.0):
            The fraction of the standard speed setting with which to move the stage.
            Hint: use pyTEM.lib.interface.tem_tilt_speed() to convert from degrees-per-second to fractional microscope
             speed.
            Some examples:
                1.0: Move with 100% of the standard microscope speed (maximum speed; for tilting this is about
                 15 deg / s).
                0.6: Move with 60% of the standard microscope speed.
                0.00032: move with 0.032% of the standard microscope speed (minimum speed; for tilting this is about
                 0.02 deg / s).
        :param movement_type: string (optional; default is "go"):
            The TEM has supports two movement types:
                "go": the instrument stage will move directly from the old position to the new position.
                "move": any existing tilts will be zeroed, then the instrument will move to the new position, then the
                 tilts will be restored or updated. This ensures that all possible positions can be reached without
                 touching the objective pole, but is not good for tilting experiments. Also, move does not allow for
                 variable speed. Therefore, the speed parameter will be ignored when movement_type="move".

        :return: None.
        """
        self.set_stage_position(x=x, speed=speed, movement_type=movement_type)

    def get_stage_position_y(self) -> float:
        """
        :return: float: The current stage position along the y-axis, in micrometres.
        """
        self._update_stage_position()  # Encase something external caused the stage to move.
        return self._stage_position.get_y()

    def set_stage_position_y(self, y: float, speed: float = 1.0, movement_type: str = "go"):
        """
        :param y: float:
            The new stage position along the y-axis, in micrometres.

        :param speed: float (optional; default is 1.0):
            The fraction of the standard speed setting with which to move the stage.
            Hint: use pyTEM.lib.interface.tem_tilt_speed() to convert from degrees-per-second to fractional microscope
             speed.
            Some examples:
                1.0: Move with 100% of the standard microscope speed (maximum speed; for tilting this is about
                 15 deg / s).
                0.6: Move with 60% of the standard microscope speed.
                0.00032: move with 0.032% of the standard microscope speed (minimum speed; for tilting this is about
                 0.02 deg / s).
        :param movement_type: string (optional; default is "go"):
            The TEM has supports two movement types:
                "go": the instrument stage will move directly from the old position to the new position.
                "move": any existing tilts will be zeroed, then the instrument will move to the new position, then the
                 tilts will be restored or updated. This ensures that all possible positions can be reached without
                 touching the objective pole, but is not good for tilting experiments. Also, move does not allow for
                 variable speed. Therefore, the speed parameter will be ignored when movement_type="move".

        :return: None.
        """
        self.set_stage_position(y=y, speed=speed, movement_type=movement_type)

    def get_stage_position_z(self) -> float:
        """
        :return: float: The current stage position along the z-axis, in micrometres.
        """
        self._update_stage_position()  # Encase something external caused the stage to move.
        return self._stage_position.get_z()

    def set_stage_position_z(self, z: float, speed: float = 1.0, movement_type: str = "go"):
        """
        :param z: float:
            The new stage position along the z-axis, in micrometres.

        :param speed: float (optional; default is 1.0):
            The fraction of the standard speed setting with which to move the stage.
            Hint: use pyTEM.lib.interface.tem_tilt_speed() to convert from degrees-per-second to fractional microscope
             speed.
            Some examples:
                1.0: Move with 100% of the standard microscope speed (maximum speed; for tilting this is about
                 15 deg / s).
                0.6: Move with 60% of the standard microscope speed.
                0.00032: move with 0.032% of the standard microscope speed (minimum speed; for tilting this is about
                 0.02 deg / s).
        :param movement_type: string (optional; default is "go"):
            The TEM has supports two movement types:
                "go": the instrument stage will move directly from the old position to the new position.
                "move": any existing tilts will be zeroed, then the instrument will move to the new position, then the
                 tilts will be restored or updated. This ensures that all possible positions can be reached without
                 touching the objective pole, but is not good for tilting experiments. Also, move does not allow for
                 variable speed. Therefore, the speed parameter will be ignored when movement_type="move".

        :return: None.
        """
        self.set_stage_position(z=z, speed=speed, movement_type=movement_type)

    def get_stage_position_alpha(self) -> float:
        """
        :return: float: The current stage tilt along the alpha direction, in degrees.
        """
        self._update_stage_position()  # Encase something external caused the stage to move.
        return self._stage_position.get_alpha()

    def set_stage_position_alpha(self, alpha: float, speed: float = 1.0, movement_type: str = "go"):
        """
        :param alpha: float:
            The new stage tilt along the alpha-axis, in degrees.

        :param speed: float (optional; default is 1.0):
            The fraction of the standard speed setting with which to move the stage.
            Hint: use pyTEM.lib.interface.tem_tilt_speed() to convert from degrees-per-second to fractional microscope
             speed.
            Some examples:
                1.0: Move with 100% of the standard microscope speed (maximum speed; for tilting this is about
                 15 deg / s).
                0.6: Move with 60% of the standard microscope speed.
                0.00032: move with 0.032% of the standard microscope speed (minimum speed; for tilting this is about
                 0.02 deg / s).
        :param movement_type: string (optional; default is "go"):
            The TEM has supports two movement types:
                "go": the instrument stage will move directly from the old position to the new position.
                "move": any existing tilts will be zeroed, then the instrument will move to the new position, then the
                 tilts will be restored or updated. This ensures that all possible positions can be reached without
                 touching the objective pole, but is not good for tilting experiments. Also, move does not allow for
                 variable speed. Therefore, the speed parameter will be ignored when movement_type="move".

        :return: None.
        """
        self.set_stage_position(alpha=alpha, speed=speed, movement_type=movement_type)

    def get_stage_position_beta(self) -> float:
        """
        :return: float: The current stage tilt along the alpha direction, in degrees.
        """
        self._update_stage_position()  # Encase something external caused the stage to move.
        return self._stage_position.get_beta()

    def set_stage_position_beta(self, beta: float, speed: float = 1.0):
        """
        :param beta: float:
            The new stage tilt along the beta-axis, in degrees.

        :param speed: float (optional; default is 1.0):
            The fraction of the standard speed setting with which to move the stage.
            Some examples:
                1.0: Move with 100% of the standard microscope speed (maximum speed; for tilting this is about
                 15 deg / s).
                0.6: Move with 60% of the standard microscope speed.
                0.00032: move with 0.032% of the standard microscope speed (minimum speed; for tilting this is about
                 0.02 deg / s).

        :return: None.
        """
        self._update_stage_position()  # Encase something external caused the stage to move.
        self.set_stage_position(beta=beta, speed=speed, movement_type="go")

    def reset_stage_position(self) -> None:
        """
        Reset (zero) the stage position.
        Note: Sometimes this might not return the stage all the way to the home position, check with is_stage_home().
        :return: None.
        """
        self.set_stage_position(x=0, y=0, z=0, alpha=0, beta=0)

    def stage_is_home(self, threshold: float = 0.1) -> bool:
        """
        Check to see if the stage is in the home position (x=0, y=0, z=0, alpha=0, beta=0).
        :param threshold: float (optional; default value is 0.1)
            We will check if the stage is home to within this threshold (this threshold applies to all axes).
        :return: bool:
            True: The stage is in the home position.
            False: The stage is somewhere other than the home position.
        """
        if self.get_stage_position_x() < threshold and self.get_stage_position_y() < threshold and \
                self.get_stage_position_z() < threshold and self.get_stage_position_alpha() < threshold and \
                self.get_stage_position_beta() < threshold:
            return True
        else:
            return False

    def print_stage_position(self) -> None:
        """
        Print out the current stage position (current x, y, z, alpha, and beta values).
        :return: None.
        """
        stage_position = self.get_stage_position()

        print("{:<15} {:<20}".format('Linear Axes', 'Position [\u03BCm]'))
        print("{:<15} {:<20}".format('x', str(stage_position.get_x())))
        print("{:<15} {:<20}".format('y', str(stage_position.get_y())))
        print("{:<15} {:<20}".format('z', stage_position.get_z()))

        print("\n{:<15} {:<20}".format('Tilt Axes', 'Tilt [deg]'))
        print("{:<15} {:<20}".format('\u03B1', stage_position.get_alpha()))
        print("{:<15} {:<20}".format('\u03B2', stage_position.get_beta()) + "\n")

    def print_stage_status(self) -> None:
        """
        Print out the current stage status, along with a 'helpful' description.
        :return: None
        """
        stage_status = self._tem.Stage.Status
        if stage_status == 0:
            print("stReady (0): The stage is ready (capable to perform all position management functions)")
        elif stage_status == 1:
            print("stDisabled (1): The stage has been disabled either by the user or due to an error.")
        elif stage_status == 2:
            print("stNotReady (2): The stage is not (yet) ready to perform position management functions for reasons "
                  "other than already accounted for by the other constants.")
        elif stage_status == 3:
            print("stGoing (3): The stage is performing a movement of type 'go'.")
        elif stage_status == 4:
            print("stMoving (4): The stage is performing a movement of type 'move'.")
        elif stage_status == 5:
            print("stWobbling (5): The stage is wobbling.")
        else:
            raise Exception("Error: Stage status - " + str(stage_status) + " - not recognized.")

    def print_stage_holder_type(self) -> None:
        """
        Print out the current stage holder type, along with a 'helpful' description.
        :return: None.
        """
        stage_type = self._tem.Stage.Holder
        if stage_type == 0:
            print("hoNone (0): Holder is removed.")
        elif stage_type == 1:
            print("hoSingleTilt (1): Single tilt holder.")
        elif stage_type == 2:
            print("hoDoubleTilt (2): Double tilt holder.")
        elif stage_type == 4:
            print("hoInvalid (4): The ‘invalid’ holder. No holder has been selected yet or the current selection has "
                  "become invalid.")
        elif stage_type == 5:
            print("hoPolara (5): Non-removable Polara holder.")
        elif stage_type == 6:
            print("hoDualAxis (6): Dual-axis tomography holder.")
        else:
            raise Exception("Stage type - " + str(stage_type) + " - not recognized.")

    def get_stage_limits(self, axis) -> Tuple[float, float]:
        """
        Get stage limits along a certain axis.

        :param axis: str:
            The axis of which to need the stage limits. One of, 'x', 'y', 'z', 'alpha', and 'beta'.
        :return: float, float: min, max:
            The minimum and maximum allowable stage values along axis, in microns / degrees.
        """
        axis = axis.lower()

        if axis == 'x':
            stage_axis_data = self._tem.Stage.AxisData(1)
            return 1e6 * stage_axis_data.MinPos, 1e6 * stage_axis_data.MaxPos  # m -> um

        elif axis == 'y':
            stage_axis_data = self._tem.Stage.AxisData(2)
            return 1e6 * stage_axis_data.MinPos, 1e6 * stage_axis_data.MaxPos  # m -> um

        elif axis == 'z':
            stage_axis_data = self._tem.Stage.AxisData(4)
            return 1e6 * stage_axis_data.MinPos, 1e6 * stage_axis_data.MaxPos  # m -> um

        elif axis in {'alpha', 'a'}:
            stage_axis_data = self._tem.Stage.AxisData(8)
            return math.degrees(stage_axis_data.MinPos), math.degrees(stage_axis_data.MaxPos)

        elif axis in {'beta', 'b'}:
            stage_axis_data = self._tem.Stage.AxisData(8)
            return math.degrees(stage_axis_data.MinPos), math.degrees(stage_axis_data.MaxPos)

        else:
            raise Exception("Error: axis '" + str(axis) + "' not recognized!")


class StageInterface(StageMixin):
    """
    A microscope interface with only stage controls.
    """

    def __init__(self):
        try:
            self._tem = cc.CreateObject("TEMScripting.Instrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e
