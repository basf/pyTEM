"""
Some manual testing of the TEMInterface stage stuff - getting and setting the stage position, etc.
"""
import sys
sys.path.append('T:/Michael L/tem-scripting-package')
from TEMInterface.TEMInterface import TEMInterface
talos = TEMInterface()

print("Getting initial stage position...")
stage_position = talos.get_stage_position()
print("The stages current x coordinate=" + str(stage_position.get_x()))
print("The stages current y coordinate=" + str(stage_position.get_y()))
print("The stages current z coordinate=" + str(stage_position.get_z()))
print("The stages current alpha coordinate=" + str(stage_position.get_alpha()))
print("The stages current beta coordinate=" + str(stage_position.get_beta()))

input("Press Enter to continue...")

print("\nWe are going to modify the initial stage position object, this should not affect the microscope...")
stage_position.set_x(4)
stage_position.set_alpha(6)

input("Press Enter to continue...")

