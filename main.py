
from ceiling import Lights
from reference import *
from pong import Pong
import tkinter as tk
import sys

print(sys.version)

doGUI = True # Whether or not to make a screen
fps = 10

# Laser stuff in an easy to edit/input format:
config = {
    "ceiling_size": (5, 2.5), # Size of your ceiling in meters in the format: (distance between goals, goal width)
    "distance_away": 3, # The distance from the ceiling to the base of the laser stand
    "laser_position": (2.5, 1.25), # The (x, y) position of the laser on the field
    "laser_rotation": 0, # The twist (deg) of the laser base relative to the sides - 0 is that the first servo is aligned with the sides
}

class Test:
    def __init__(self, numStrips=12, numLedsPerStrip=150):
        self.lights = []
        self.updatingThread = None
        self.red = 0

        # # Generates a basic set of lights
        for string in range(numStrips):  # range(number of strings)
            self.lights.append([])
            for led in range(numLedsPerStrip):  # range(number of leds)
                self.lights[string].append((255, 0, 0))

    def update(self):

        self.red += 100
        if self.red > 255: self.red = 0

        print(self.red)

        for stringNum in range(len(self.lights)):
            for ledNum in range(len(self.lights[stringNum])):
                self.lights[stringNum][ledNum] = (self.red, 0, 0)


beingPressed = []

currentlyRunning = Pong(beingPressed)
# currentlyRunning = Test()

lightController = Lights(currentlyRunning.lights, gui=doGUI)

if doGUI:

    def keyDown(event):
        key = event.char
        if key in relevantKeys and not key in beingPressed:
            beingPressed.append(key)

    def keyUp(event):
        key = event.char
        beingPressed.remove(key)

    relevantKeys = ['a', 'z', '/', '\'']
    lightController.canvas.bind("<KeyPress>", keyDown)
    lightController.canvas.bind("<KeyRelease>", keyUp)
    lightController.canvas.update_idletasks()
    lightController.canvas.focus_set()
    lightController.canvas.pack()

try: # Try so that if we close the window it just exits instead of throwing an error

    print("time per frame:",1/fps)

    while True:

        startTime = time.time()  # Record the start time of the function

        codeTimer.start("update")
        lightController.update() # Update the gui / physical leds
        codeTimer.print("update")

        elapsedTime = time.time() - startTime  # Find the time it took to run move code
        if elapsedTime > 1/fps:
            print("Behind")
        else:
            time.sleep(int(1 / fps - elapsedTime))  # Recursively call the function

except tk.TclError as ex:
    pass

finally:
    stopAllThreads()
    currentlyRunning.stop()

