
import threading
import time
from codeTimer import CodeTimer

codeTimer = CodeTimer()

numStrings = 12
numPixelsPerString = 150

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

def stopAllThreads():
    pass # I'm not sure how to do this atm, sorry

# Given a rectangle, turn the width and height into x2 and y2 positions for tkinter
def rectalize(x, y, width, height, center=False):
    if center:
        return x-width/2,y-height/2,x+width/2,y+height/2
    else:
        return x,y,x+width,y+height
