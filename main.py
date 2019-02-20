
from ceiling import Lights
from reference import *
from pong import Pong
import Tkinter as tk

mode = "gui" # can be "gui" or "ceil"

ledUpdateRate = 20

beingPressed = [] # this tracks whether the keys for pong are being pressed

currentLightProgram = Pong(beingPressed, "pong") # Create an active pong game with a pointer to the keys being pressed and set its name as "pong"

lightController = Lights(currentLightProgram.outputs, ledUpdateRate, mode)

# Create a system for logging which keys are being pressed. If we aren't using the GUI this won't work, so don't run it when not using the GUI
if mode=="gui":

    def keyDown(event):
        key = event.char
        if key in relevantKeys and not key in beingPressed:
            beingPressed.append(key)

    def keyUp(event):
        key = event.char
        if key in beingPressed:
            beingPressed.remove(key)

    relevantKeys = ['a', 'z', '/', '\'']
    lightController.canvas.bind("<KeyPress>", keyDown)
    lightController.canvas.bind("<KeyRelease>", keyUp)
    lightController.canvas.update_idletasks()
    lightController.canvas.focus_set()
    lightController.canvas.pack()

# The window running loop. Not really supposed to do anything currently but keep the main thread from exiting
def mainLoop():
    try: # Try so that if we close the window it just exits instead of throwing an error

        while threadsShouldBeRunning():

            time.sleep(1)

    finally:
        stopAllThreads()
        currentLightProgram.stopThread()
        lightController.stop()


threading.Thread(target=mainLoop).start()
lightController.autoUpdate()