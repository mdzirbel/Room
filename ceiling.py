import Tkinter as tk
from reference import *
#from neopixel import *

class Lights:
    def __init__(self, lights, fps, mode):
        assert type(fps) is int and 1 <= fps <= 200, "fps should be an integer between 1 and 200, was " + fps
        assert mode in ["gui", "ceil"], "mode should only be 'gui' or 'ceil', was " + mode

        self.lights = lights # The lights you want it to put on the ceiling / screen
        self.mode = mode # Whether to use a gui or go to the ceiling. Options are "gui" and "ceil"
        self.fps = fps





        if self.mode=="gui":

            # Initialize useful variables
            self.laser = None # Initialize the variable which will hold the Tkinter circle for the laser if there is one, or None if there isn't
            self.canvas = None # Initialize the variable which will hold the canvas object
            self.lightsObjects = [] # Holds the Tkinter rectangles for the lights

            self.initializeGUI()
            self.updateGUI()
        else:
            self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0)
            self.strip2 = Adafruit_NeoPixel(LED_COUNT, LED_PIN2, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
            self.initializeLEDs()
            self.updateLEDs()

    def stop(self):
        pass # TODO Set all lights to off

    def initializeLEDs(self):
        self.strip.begin()
        self.strip2.begin()

        self.ID = [[],[]]
        stripNum = 4
        lightNum = 0
        for i in range(LED_COUNT):
            self.ID[0].append((stripNum, lightNum))

            if i%PIXELS_PER_STRING==0:
                stripNum -= 1
                lightNum = 0

            lightNum += 1


        stripNum = 5
        lightNum = 0
        for i in range(LED_COUNT):
            self.ID[1].append((stripNum, lightNum))

            if i%PIXELS_PER_STRING==0:
                stripNum += 1
                lightNum = 0

            lightNum += 1

    def updateLEDs(self):
        leds, laser = getLedsAndLights(self.lights)
        currentStripColor0 = 0
        currentStripColor1 = 0
        for i in range(LED_COUNT):
            if i%PIXELS_PER_STRING==0:
                if isinstance(leds[4-i/PIXELS_PER_STRING], str):
                    color = toRGB(leds[4-i/PIXELS_PER_STRING])
                    currentStripColor0 = Color(int(color[1]*255), int(color[0]*255), int(color[2]*255))
                else:
                    currentStripColor0 = 0
            if currentStripColor0:
                self.strip.setPixelColor(i, currentStripColor0)
            else:
                stripIndex, lightIndex = self.ID[0][i]
                color = toRGB(leds[stripIndex][lightIndex])
                self.strip.setPixelColor(i, Color(int(color[1]*255), int(color[0]*255), int(color[2]*255)))


            if i%PIXELS_PER_STRING==0:
                if isinstance(leds[5+i/PIXELS_PER_STRING], str):
                    color = toRGB(leds[5+i/PIXELS_PER_STRING])
                    currentStripColor1 = Color(int(color[1]*255), int(color[0]*255), int(color[2]*255))
                else:
                    currentStripColor1 = 0
            print currentStripColor1,i
            if currentStripColor1:
                self.strip.setPixelColor(i, currentStripColor1)
            else:
                stripIndex, lightIndex = self.ID[1][i]
                color = toRGB(leds[stripIndex][lightIndex])
                self.strip2.setPixelColor(i, Color(int(color[1]*255), int(color[0]*255), int(color[2]*255)))
    # Keep in mind that:
    # self.lights should be unpacked to lights and laser using the helper function getLedsAndLights(lights) at the bottom of this file
    # If the spot where a string of leds could be has a string, that should be a color to set the whole string to, eg lights = ["black", "blue", "green"]
    # An empty list should be treated like "black", so that lights = [[], [], []] == ["black", "black", "black"]
    # lights will always be a list after the unpacking function. If it's passed in as a string, the unpacking function will fix it. eg: "white" -> ["white", "white", "white"]
    # Make sure you read the updateGUI function

    def autoUpdate(self):
        try:
            while threadsShouldBeRunning():

                startTime = time.time() # Record the start time of the function

                self.update()  # Update the gui / physical leds

                elapsedTime = time.time() - startTime # Find the time it took to run move code
                toWait = 1.0 / self.fps - elapsedTime # Calculate time to wait for next frame
                if toWait < -0.02: # If the thread is severely behind, print out a warning
                    print "Lights thread is behind by",round(toWait,2),"seconds (1 / "+str(-round(1/toWait, 2))+" seconds)"
                elif toWait < 0: # Continue to the next frame if it's just a little behind
                    pass
                else: # If it's ahead wait for the next frame
                    time.sleep(toWait)  # Sleep the time minus the time execution took

        except tk.TclError as _:
            pass

        finally: # In case of an error or for proper ending of the function, tell all other threads to exit when this thread exits
            stopAllThreads()

    def updateLights(self, lights): # Called by the user to pass a new lights pointer in
        self.lights = lights
        self.update()

    # Initialize the lights for the gui
    def initializeGUI(self):
        assert self.mode=="gui", "You need a gui to initialize the lights"

        # Create the GUI
        root = tk.Tk()
        root.title = "Game"
        root.resizable(0, 0)
        root.wm_attributes("-topmost", 1)
        self.canvas = tk.Canvas(root, width=screenSize[0], height=screenSize[1], bd=0, highlightthickness=0)
        self.canvas.focus_set()
        self.canvas.pack()

        leds, laser = getLedsAndLights(self.lights)

        color = toHex("black") # Start all lights with the default starting color of black

        # Render lights
        for stringNum in range(NUM_STRINGS):

            # Calculate this ahead of time to cut down on time
            x = int(stringNum / (NUM_STRINGS - 1) * (relevantScreenSize[0] - ledSize[0])) + screenBorder["left"]
            relevantY = relevantScreenSize[1] - ledSize[1]

            self.lightsObjects.append([])

            for ledNum in range(PIXELS_PER_STRING):
                # (led number / total leds) * (relevant screen size to scale)
                y = int((ledNum+1) / PIXELS_PER_STRING * relevantY) + screenBorder["top"]

                newPixel = self.canvas.create_rectangle(rectalize(x, y, ledSize[0], ledSize[1]), fill=color)
                self.lightsObjects[stringNum].append(newPixel)

        # Order is somewhat important here. The laser should be rendered on top of the leds
        # If there is a laser, render it
        if laser:
            self.laser = self.canvas.create_oval(getLaserCoords(laser), fill=laserColor)

    # The general update function for the lights controller, to be called when we want to update either the current gui / physical leds
    def update(self):
        if self.mode=="gui":
            self.updateGUI()
        elif self.mode=="ceil":
            self.updateLEDs()

    # Changes the GUI to reflect the current position of self.lights. Assumes that there is a gui
    def updateGUI(self):

        leds, laser = getLedsAndLights(self.lights)

        # Render lights
        # print self.lights
        codeTimer.start("allLights")
        for stringNum in range(NUM_STRINGS):
            codeTimer.start("oneLightString")

            if isinstance(leds[stringNum], list): # If it's a list
                if not leds[stringNum]: # If it's an empty list fill black
                    for pixelNum in range(PIXELS_PER_STRING):
                        self.canvas.itemconfig(self.lightsObjects[stringNum][pixelNum], fill="#000000")
                else: # Treat it as a regular pixel list
                    for pixelNum in range(PIXELS_PER_STRING):
                        color = toHex(leds[stringNum][pixelNum])
                        self.canvas.itemconfig(self.lightsObjects[stringNum][pixelNum], fill=color)

            elif isinstance(leds[stringNum], str): # If it's a string with a color set the LED string to that color
                color = toHex(leds[stringNum])
                for pixelNum in range(PIXELS_PER_STRING):
                    self.canvas.itemconfig(self.lightsObjects[stringNum][pixelNum], fill=color)

            else:
                print"Can't figure out how to render something in updateGUI (in ceiling.py)"
                raise TypeError("Lights is not the right type to be figured out by ceiling.py (updateGUI())")

            codeTimer.print_time("oneLightString")

        codeTimer.print_time("allLights")

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
        # print "xAngle:", xAngle
        # moveServo1(xAngle)

# Unpack lights to leds and laser
def getLedsAndLights(lights):
    if isinstance(lights, dict):  # If it's a dictionary it should have a lights and a laser, otherwise it should be the lights if it's a string
        leds = lights["lights"]
        laser = lights["laser"]
    elif isinstance(lights, str):  # If it's a string it indicates that all LEDS should be that color, so make a list of it to be handled later
        leds = [str for _ in range(NUM_STRINGS)]
        laser = None
    else:  # Default is to assume that self.lights is just the leds and there is no laser
        leds = lights
        laser = None

    return leds, laser

