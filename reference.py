
# These import statements are actually used by things which import reference
import threading
import time
from codeTimer import CodeTimer

codeTimer = CodeTimer()

runThreads = True # Used to stop the execution of all threads

# LED strip configuration:
NUM_STRINGS    = 10      # Number of strings total
PIXELS_PER_STRING = 150  # Number of pixels per led string
LED_COUNT      = NUM_STRINGS/2 * PIXELS_PER_STRING  # Number of LED pixels per side.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN2       = 13      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


screenSize = (1100, 600)
screenBorder = {
    "right": 50,
    "left": 50,
    "top": 50,
    "bottom": 50
}
relevantScreenSize = (screenSize[0]-screenBorder["left"]-screenBorder["right"], screenSize[1]-screenBorder["top"]-screenBorder["bottom"])
ledSize = (15,3)
laserColor = "red"
laserDiameter = 25

# Config is a reference for games which require measurements on the area of the pixels on the ceiling
config = {
    "ceiling_size": [5, 2.5] # Area of the ceiling with pixels, not the room dimensions. This does not include the border.
}

laserConfig = {
    "distance_away": 3, # The distance from the ceiling to the base of the laser stand
    "laser_position": (2.5, 1.25), # The (x, y) position of the laser on the field
    "laser_rotation": 0, # The twist (deg) of the laser base relative to the sides - 0 is that the first servo is aligned with the sides
}

stringToRGB = {
    "white": (255,255,255),
    "black": (0,0,0),
    "blue": (0,0,255),
    "red": (255,0,0),
    "green": (0,255,0),
    "yellow": (255,255,0),
    "orange": (255, 165, 0),
    "purple": (128,0,128),
    "violet": (159, 0, 255),
    "cyan": (0,255,255),
}

def getLaserCoords(*pos):
    if len(pos)==1: # If you just pass in an array it will be the first argument in pos
        x=pos[0][0]
        y=pos[0][1]
    else: #if len(pos)==2: # Else assume pos is the x and y
        x=pos[0]
        y=pos[1]

    return rectalize(x * ((relevantScreenSize[0]) / config["ceiling_size"][0]) + screenBorder["left"], y * ((relevantScreenSize[1]) / config["ceiling_size"][1])
              + screenBorder["top"], laserDiameter, laserDiameter, center=True)

def toHex(color):
    if isinstance(color, tuple) and len(color)==3: # If it's an rgb tuple
        return "#%02x%02x%02x" % color
    elif isinstance(color, str):
        if color[0] == '#': # If it's already hex then just return it
            return color
        else:
            return toHex(stringToRGB[color])
    else:
        assert False, "Color not recognized: " + str(color)

def toRGB(color):
    if isinstance(color, tuple) and len(color)==3: # If it's an rgb tuple
        return color
    elif isinstance(color, str):
        if color[0] == '#': # If it's hex then just return it
            return tuple(int(color[i:i+2], 16) for i in (0, 2 ,4))
        else:
            return stringToRGB[color]
    else:
        assert False, "Color not recognized: " + str(color)

def stopAllThreads():
    global runThreads
    runThreads = False

def threadsShouldBeRunning():
    return runThreads

# Given a rectangle, turn the width and height into x2 and y2 positions for tkinter
# if center is true, the x and y given are used as the center of the box returned
def rectalize(x, y, width, height, center=False):
    if center:
        return x-width/2,y-height/2,x+width/2,y+height/2
    else:
        return x,y,x+width,y+height

"""
Just going to put this here for a bit of reference
class Test:
    def __init__(self, numStrips=numStrings, numLedsPerStrip=numPixelsPerString):
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

        print self.red

        for stringNum in range(len(self.lights)):
            for ledNum in range(len(self.lights[stringNum])):
                self.lights[stringNum][ledNum] = (self.red, 0, 0)
"""