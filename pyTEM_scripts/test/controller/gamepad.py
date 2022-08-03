import sys
import pygame
import keyboard
import mouse
import time
from pygame.locals import *


def gamepad():
    global shift
    global q
    global event
    global xr
    global yr
    global yl
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                print("a")
                keyboard.press_and_release(shift + "a")
            if event.button == 1:
                print("b")
                keyboard.press_and_release(shift + "b")
            if event.button == 2:
                print("x")
            if event.button == 3:
                print("y")
            if event.button == 4:
                print("LB")
                keyboard.press_and_release("Backspace")
            if event.button == 5:
                print("RB")
                keyboard.press_and_release("Space")
            if event.button == 6:
                if shift == "":
                    shift = "Shift+"
                    print("Shift aktiviert")
                else:
                    shift = ""
                    print("Shift deaktiviert")
            if event.button == 7:
                print("ESC was pressed, program closed!")
                pygame.quit()
                sys.exit()
            if event.button == 8:
                print("Joy-left push")
            if event.button == 9:
                print("Joy-right push")

        if event.type == JOYAXISMOTION:
            if event.axis == 0:
                xl = round(event.value, 3)
            if event.axis == 1:
                yl = round(event.value, 3)
                if yl > 0.075:
                    mouse.wheel(-yl/10)
                if yl < -0.075:
                    mouse.wheel(-yl/10)
            if event.axis == 2:
                xr = round(event.value, 3)
                if xr > 0.075 or xr < -0.075:
                    mouse.move(xr*faktor, 0, absolute=False)
            if event.axis == 3:
                yr = round(event.value, 3)
                if yr > 0.075 or yr < -0.075:
                    mouse.move(0, yr*faktor, absolute=False)
            if event.axis == 4:
                lt = round(event.value, 3)
                if lt > 0.95:
                    mouse.click("right")
                    print("LT")
            if event.axis == 5:
                rt = round(event.value, 3)
                if rt > 0.95:
                    mouse.click("left")
                    print("RT")

        if event.type == JOYHATMOTION:
            if event.value == (-1, 0):
                print("left")
            if event.value == (1, 0):
                print("lright")
            if event.value == (0, 1):
                print("up")
            if event.value == (0, -1):
                print("down")

        if event.type == JOYDEVICEADDED:
            gamepad = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            for gamepad in gamepad:
                print(gamepad.get_name() + ", connected!  You're ready for TEM!")
        if event.type == JOYDEVICEREMOVED:
            gamepad = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            print("PLEASE RECONNECT CONTROLLER!!")

    q = 1
    time.sleep(0.0025)


if __name__ == "__main__":
    while True:
        pygame.init()
        pygame.joystick.init()
        gamepad = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

        shift = "Shift+"
        q = 0
        xr = 0
        xl = 0
        yr = 0
        yl = 0
        faktor = 5
        while True:
            if q == 0:
                pygame.init()
                pygame.joystick.init()
                gamepad = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
                gamepad()
            elif q == 1:
                q = 0
                if event is not None:
                    if xr > 0.075 or xr < -0.075:
                        mouse.move(xr*faktor, 0, absolute=False)
                    if yr > 0.075 or yr < -0.075:
                        mouse.move(0, yr*faktor, absolute=False)
                    if yl > 0.075:
                        mouse.wheel(-yl/10)
                    if yl < -0.075:
                        mouse.wheel(-yl/10)
                    if xl != 0:
                        print(xl)
