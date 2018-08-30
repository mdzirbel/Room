import tkinter as tk
from reference import *


class Lights:
    def __init__(self, lights, gui=False, ceiling=False):
        self.lights = lights # The lights you want it to put on the ceiling / screen
        self.laserConfig = laserConfig # The setup of the laser in the physical world. See top for example
        self.gui = gui # If you want a gui
        self.ceiling = ceiling

        if self.gui:
            root = tk.Tk()
            root.title = "Game"
            root.resizable(0,0)
            root.wm_attributes("-topmost", 1)
            self.screenSize = gui # If gui is wanted it should be given as the desired dimensions of the gui
            self.canvas = tk.Canvas(root, width=screenSize[0], height=screenSize[1], bd=0, highlightthickness=0)
            self.canvas.focus_set()
            self.canvas.pack()
            self.laser = None
            self.lightsObjects = []
            if lights:
                self.initializeGUI()
                self.updateGUI()

    def updateLights(self, lights=None): # Called by the user to pass a new lights pointer in
        self.lights = lights
        self.updateGUI()

    # Initialize the lights for the gui
    def initializeGUI(self): # system is type of input is expected for lights. eg: "one color" or something, with lights=(20,30,50)
        assert self.gui, "You need a gui to initialize the lights"

        leds, laser = getLedsAndLights(self.lights)

        color = toHex("black") # Start all lights with the default starting color of black

        # Render lights
        for stringNum in range(12):

            # Calculate this ahead of time to cut down on time
            x = int(stringNum/11 * (relevantScreenSize[0] - ledSize[0])) + screenBorder["left"]
            relevantY = relevantScreenSize[1] - ledSize[1]

            self.lightsObjects.append([])

            for ledNum in range(numPixelsPerString):
                # (led number / total leds) * (relevant screen size to scale)
                y = int((ledNum+1) / numPixelsPerString * relevantY) + screenBorder["top"]

                newPixel = self.canvas.create_rectangle(rectalize(x, y, ledSize[0], ledSize[1]), fill=color)
                self.lightsObjects[stringNum].append(newPixel)

        # Order is somewhat important here. The laser should be rendered on top of the leds
        # If there is a laser, render it
        if laser:
            self.laser = self.canvas.create_oval(getLaserCoords(laser), fill=laserColor)

    # The general update function for the lights controller, to be called when we want to update the current gui / physical leds
    def update(self):
        if self.gui:
            self.updateGUI()
        elif self.ceiling:
            self.updateCeiling()

    # Changes the GUI to reflect the current position of self.lights. Assumes that there is a gui
    def updateGUI(self):

        leds, laser = getLedsAndLights(self.lights) # Does not take time

        # Render lights
        # print(self.lights)
        codeTimer.start("")
        for stringNum in range(12):
            codeTimer.start("string")

            if isinstance(leds[stringNum], list): # If it's a list
                if not leds[stringNum]: # If it's an empty list fill black
                    for pixelNum in range(150):
                        codeTimer.start("set")
                        self.canvas.itemconfig(self.lightsObjects[stringNum][pixelNum], fill="#000000")
                        codeTimer.print("set")
                else: # Treat it as a regular pixel list
                    for pixelNum in range(150):
                        color = toHex(leds[stringNum][pixelNum])
                        codeTimer.start("regular")
                        self.canvas.itemconfig(self.lightsObjects[stringNum][pixelNum], fill=color)
                        codeTimer.print("regular")

            elif isinstance(leds[stringNum], str): # If it's a string with a color set the LED string to that color
                color = toHex(leds[stringNum])
                for pixelNum in range(150):
                    self.canvas.itemconfig(self.lightsObjects[stringNum][pixelNum], fill=color)

            else:
                print("Can't figure out how to render something in updateGUI (in ceiling.py)")
                raise TypeError("Lights is not the right type to be figured out by ceiling.py (updateGUI())")

            codeTimer.print("string")
        # Order is somewhat important here. The laser should be rendered on top of the leds
        # If there is a laser, render it
        if laser:
            self.canvas.coords(self.laser, getLaserCoords(laser))

        self.canvas.update_idletasks()
        self.canvas.update()

    def moveLaserToPos(self, pos):
        pass
        # xDisOff = (config["laser_position"][0] - pos[0])  # horizontal distance the laser is from the pointer target
        # xAngle = math.atan(xDisOff / config["distance_away"]) * (180 / math.pi)  # Get angle from vertical to move to
        # xAngle += 90
        # assert 0 < xAngle < 180
        #
        # # Still needs to set the second servo
        #
        # print("xAngle:", xAngle)
        # moveServo1(xAngle)

# Unpack lights to leds and laser
def getLedsAndLights(lights):
    if isinstance(lights, dict):  # If it's a dictionary it should have a lights and a laser, otherwise it should be the lights if it's a string
        leds = lights["lights"]
        laser = lights["laser"]
    elif isinstance(lights, str):  # If it's a string it should be a list with 12 of the strings
        leds = [str for _ in range(12)]
        laser = None
    else:  # Default is to assume that self.lights is just the leds and there is no laser
        leds = lights
        laser = None

    return leds, laser

