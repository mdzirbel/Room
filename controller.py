from reference import *

# A subclass needs three things:
# A self.lights string initialized in the init
# Tick: what to do fps times per second
# getLights: returns what the lights are, called immediately after that tick (or never change outputs["lights"] to a different array)

class Controller(object):

    def __init__(self, name, fps):
        self.frameNum = 0
        self.name = name # The name of the thread, eg. "pong". Default "unnamed". Used for identifying/debugging purposed
        self.fps = fps # The fps to run at. Most use 30

        self.outputs = {
            "lights": "black",
            "laser": None
        }

        self.keepRunningThread = True

    def startThread(self):
        threading.Thread(target=self.moveController).start()

    def stopThread(self):
        self.keepRunningThread = False

    def updateLights(self):
        self.outputs["lights"] = self.getLights()

    def updateLaser(self):
        self.outputs["laser"] = self.getLaser()

    def getLaser(self):
        return self.outputs["laser"]

    def getLights(self):
        return self.outputs["lights"]

    def moveController(self):

        try:
            while self.keepRunningThread and threadsShouldBeRunning():

                startTime = time.time() # Record the start time of the function

                # Function code:
                self.tick()
                self.updateLights()
                self.frameNum += 1

                elapsedTime = time.time() - startTime  # Find the time it took to run move code
                toWait = 1 / self.fps - elapsedTime  # Calculate time to wait for next frame
                if toWait < -0.02:  # If the thread is severely behind, print out a warning
                    print self.name, "thread is behind by", round(toWait, 2), "seconds (1 / " + str(-round(1 / toWait, 2)) + " seconds)"
                elif toWait < 0:  # Continue to the next frame if it's just a little behind
                    pass
                else:  # If it's ahead wait for the next frame
                    time.sleep(toWait)  # Sleep the time minus the time execution took

        finally:
            stopAllThreads()
