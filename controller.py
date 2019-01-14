from reference import *

class Controller(object):

    def __init__(self, name, fps):

        self.name = name # The name of the thread, eg. "pong". Default "unnamed". Used for identifying/debugging purposed
        self.fps = fps # The fps to run at. Most use 30

        self.keepRunningThread = True

    def startThread(self):
        threading.Thread(target=self.moveController).start()

    def stopThread(self):
        self.keepRunningThread = False

    def updateLights(self):
        self.lights["lights"] = self.getLights()

    def updateLaser(self):
        self.lights["laser"] = self.getLaser()

    def moveController(self):

        try:
            while self.keepRunningThread and threadsShouldBeRunning():

                startTime = time.time() # Record the start time of the function

                # Function code:
                self.tick()
                self.updateLights()

                elapsedTime = time.time() - startTime # Find the time it took to run move code
                toWait = 1/self.fps - elapsedTime # Time to wait in seconds
                if toWait < 0:
                    print(self.name+"thread is behind by",toWait,"seconds")
                else:
                    time.sleep(toWait) # Sleep the time minus the time execution took

        finally:
            stopAllThreads()
