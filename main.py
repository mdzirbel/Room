
from ceiling import Lights
from reference import *
from pong import Pong
from general import General

ledUpdateRate = 30

beingPressed = [] # this tracks whether the keys for pong are being pressed

#currentLightProgram = Pong(beingPressed, "pong") # Create an active pong game with a pointer to the keys being pressed and set its name as "pong"
currentLightProgram = General("general") # Create an active pong game with a pointer to the keys being pressed and set its name as "pong"

lightController = Lights(currentLightProgram.outputs, ledUpdateRate, mode)

# Default: go to general
def updateScene(new_scene):
    global currentLightProgram
    # Add check for if new_scene == current_scene and do nothing
    if new_scene == "Pong":
        currentLightProgram = Pong(beingPressed, "pong")
    else:
        currentLightProgram = General("general")

    lightController.lights = currentLightProgram.outputs

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

            updateBrightness()
            updateScene()

    finally:
        stopAllThreads()
        currentLightProgram.stopThread()
        lightController.stop()


threading.Thread(target=mainLoop).start()
lightController.autoUpdate()