#!/usr/bin/env python
"""
Some manual testing of the StagePosition class
"""

import sys
sys.path.append('T:/Michael L/tem-scripting-package')
from Interface.lib.StagePosition import StagePosition


print("\nCreating a stage position object with x=0, y=1, z=2, alpha=-0.35, and beta=0.35...")
stage_position_object = StagePosition(x=0, y=1, z=2, alpha=-0.35, beta=0.35)
print("The stages current x coordinate=" + str(stage_position_object.get_x()))
print("The stages current y coordinate=" + str(stage_position_object.get_y()))
print("The stages current z coordinate=" + str(stage_position_object.get_z()))
print("The stages current alpha coordinate=" + str(stage_position_object.get_alpha()))
print("The stages current beta coordinate=" + str(stage_position_object.get_beta()))

input("Press Enter to continue...")

print("\nUpdating the stage location object to x=-1, y=-2, z=-3, alpha=0.7, and beta=-0.7...")
stage_position_object.set_x(new_x=-1)
stage_position_object.set_y(new_y=-2)
stage_position_object.set_z(new_z=-3)
stage_position_object.set_alpha(new_alpha=0.7)
stage_position_object.set_beta(new_beta=-0.7)
print("The stages current x coordinate=" + str(stage_position_object.get_x()))
print("The stages current y coordinate=" + str(stage_position_object.get_y()))
print("The stages current z coordinate=" + str(stage_position_object.get_z()))
print("The stages current alpha coordinate=" + str(stage_position_object.get_alpha()))
print("The stages current beta coordinate=" + str(stage_position_object.get_beta()))

print("\n###### END OF TESTING ######")
input("Press Enter to exit script...")
