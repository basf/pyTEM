"""
 Author:  Jason Kobel
 Date:    Summer 2022
"""

import math
import threading
from inputs import get_gamepad


class XboxController(object):
    """
    Readout of the Xbox Controller
    """
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def _monitor_controller(self):

        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.X = event.state
                elif event.code == 'BTN_WEST':
                    self.Y = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state

    def read(self):
        xl = round(self.LeftJoystickX, 3)
        yl = round(self.LeftJoystickY, 3)
        xr = round(self.RightJoystickX, 3)
        yr = round(self.RightJoystickY, 3)
        lt = round(self.LeftTrigger, 3)
        rt = round(self.RightTrigger, 3)
        if(((xl < 0.075) and (xl > -0.075)) and ((yl < 0.075) and (yl > -0.075))):
            xl = 0
            yl = 0
        if(((xr < 0.075) and (xr > -0.075)) and ((yr < 0.075) and (yr > -0.075))):
            xr = 0
            yr = 0

        a = self.A
        b = self.B
        xx = self.X
        yy = self.Y
        LB = self.LeftBumper
        RB = self.RightBumper
        esc = self.Back
        start = self.Start
        left = self.LeftDPad
        right = self.RightDPad
        up = self.UpDPad
        down = self.DownDPad
        Jl = self.LeftThumb
        Jr = self.RightThumb
        return[xl, yl, xr, yr, lt, rt, a, b, xx, yy, LB, RB, esc, start, left, right, up, down, Jl, Jr]
