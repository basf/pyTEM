from pyTEM.Interface import Interface

from pathlib import Path

from pyTEM.lib.mixins.BeamBlankerMixin import BeamBlankerMixin

my_microscope = Interface()

""" Acquisition Controls """
# Get a list of available cameras.
available_cameras = my_microscope.get_available_cameras()

if len(available_cameras) > 0:
    # Let's see what each camera can do...
    for camera in available_cameras:
        my_microscope.print_camera_capabilities(camera_name=camera)

    # Perform a single acquisition using the first available camera.
    acq = my_microscope.acquisition(camera_name=available_cameras[0], exposure_time=1, sampling='4k',
                                    blanker_optimization=True)

    # Display a pop-up with the results of our acquisition.
    acq.show_image()

    # Downsample the acquisition (bilinear decimation by a factor of 2).
    acq.downsample()

    # Save the acquisition to file.
    downloads_path = str(Path.home() / "Downloads")
    acq.save_to_file(out_file=downloads_path + "/test_acq.tif")

else:
    print("No available cameras!")

""" Magnification Controls """
from pyTEM.Interface import Interface
my_microscope = Interface()

# Make sure we are in TEM imaging mode.
my_microscope.set_mode(new_mode="TEM")
my_microscope.set_projection_mode(new_projection_mode="imaging")

# Print out the current magnification.
current_magnification = my_microscope.get_magnification()
print("Current magnification: " + str(current_magnification) + "x Zoom")

# Print a list of available magnifications.
my_microscope.print_available_magnifications()

# TEM magnification is set by index, lets increase the magnification by three notches.
current_magnification_index = my_microscope.get_magnification_index()
my_microscope.set_tem_magnification(new_magnification_index=current_magnification_index + 3)

# And decrease it back down by one notch.
my_microscope.shift_tem_magnification(magnification_shift=-1)

""" Image and Beam Shift Controls """
# Print out the current image shift.
u = my_microscope.get_image_shift()
print("Current image shift in the x-direction: " + str(u[0]))
print("Current image shift in the y-axis: " + str(u[1]))

# Print out the current beam shift.
v = my_microscope.get_beam_shift()
print("\nCurrent beam shift in the x-direction: " + str(v[0]))
print("Current beam shift in the y-direction: " + str(v[1]))

# Shift the image 2 microns to the right, and 3 microns up.
my_microscope.set_image_shift(x=u[0] + 2, y=u[1] + 3)

# Move the beam shift to (-10, 5).
my_microscope.set_beam_shift(x=-10, y=5)

# Print out the new image shift.
u = my_microscope.get_image_shift()
print("\nNew image shift in the x-direction: " + str(u[0]))
print("New image shift in the y-direction: " + str(u[1]))

# Print out the new beam shift.
v = my_microscope.get_beam_shift()
print("\nNew beam shift in the x-direction: " + str(v[0]))
print("New beam shift in the y-direction: " + str(v[1]))

# Zero both image and beam shift.
my_microscope.zero_shifts()

""" Mode Controls """
# Make sure we are in TEM imaging mode.
my_microscope.set_mode(new_mode="TEM")
my_microscope.set_projection_mode(new_projection_mode="imaging")

# Print out the current projection submode.
my_microscope.print_projection_submode()

# Print out the current illumination mode.
print("Current illumination mode: " + my_microscope.get_illumination_mode())
if my_microscope.get_illumination_mode() == "microprobe":
    print("This mode provides a nearly parallel illumination at the cost of a larger probe size.")
else:
    print("Use this mode to get a small convergent electron beam.")

# Switch to STEM mode.
my_microscope.set_mode(new_mode="STEM")

""" Screen controls """
if my_microscope.get_screen_position() == "retracted":
    my_microscope.insert_screen()

""" Beam Blanker Controls """

if my_microscope.beam_is_blank():
    print("The beam is blank... un-blanking beam...")
    my_microscope.unblank_beam()
else:
    print("The beam is un-blanked... blanking beam...")
    my_microscope.blank_beam()


""" Stage Controls """

# Print out the stage's current status.
my_microscope.print_stage_status()

# Reset the microscope stage to the home position.
if my_microscope.stage_is_home():
    pass
else:
    my_microscope.reset_stage_position()

# Update the x, y, and alpha stage positions. Move at half speed.
my_microscope.set_stage_position(x=5, y=10, alpha=-45, speed=0.5)

# Print out the current stage position.
my_microscope.print_stage_position()

""" Vacuum Controls """

# Print out the current status of the vacuum system.
my_microscope.print_vacuum_status()

# Print out vacuum info in a table-like format.
my_microscope.print_vacuum_info()

# Check if the column is under vacuum.
if my_microscope.column_under_vacuum():
    print("The column is currently under vacuum; it is safe to open the column valve.")
else:
    print("Column vacuum is insufficient to open the column valve.")

# Make sure the column valve is closed.
if my_microscope.get_column_valve_position() == "open":
    my_microscope.close_column_valve()

# Create a pyTEM interface with only stage controls.
# Through this interface, we have access to all pyTEM stage-related functions,
#  but none of the other functions.
from pyTEM.lib.mixins.StageMixin import StageInterface

stage_interface = StageInterface()

# Using a stage interface, we can perform the same series of commands performed earlier
#  with a complete interface.

# Print out the stage's current status.
stage_interface.print_stage_status()

# Reset the microscope stage to the home position.
if stage_interface.stage_is_home():
    pass
else:
    stage_interface.reset_stage_position()

# Update the x, y, and alpha stage positions. Move at half speed.
stage_interface.set_stage_position(x=5, y=10, alpha=-45, speed=0.5)

# Print out the current stage position.
stage_interface.print_stage_position()

import comtypes.client as cc

from pyTEM.lib.mixins.StageMixin import StageMixin
from pyTEM.lib.mixins.BeamBlankerMixin import BeamBlankerMixin


class StageBeamBlankerInterface(StageMixin, BeamBlankerMixin):
    """
    A microscope interface with only stage and beam blanker controls.
    """

    def __init__(self):
        try:
            self._tem = cc.CreateObject("TEMScripting.Instrument")
        except OSError as e:
            print("Unable to connect to the microscope.")
            raise e


