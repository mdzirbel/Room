import time

# The ids to not track, so that timing debugging can be turned off easily from here
noTrack = ["set", "regular", "oneLightString", "allLights"]

roundPrecision = 8 # Number of decimal places to save/print

class CodeTimer:

    def __init__(self):
        self.startTimes = {}

    def start(self, trackId="current"):
        if not trackId in noTrack:
            self.startTimes[trackId] = round(time.time(), roundPrecision)

    def get(self, trackId="current"):
        if not trackId in noTrack:
            return round(time.time() - self.startTimes[trackId], roundPrecision)

    def print_time(self, trackId="current"):
        if not trackId in noTrack:
            print str(self.get(trackId))+"s since starting timer: \""+str(trackId)+"\""


"""

I checked how long this takes, to ensure it isn't slowing the code down. It isn't. Even a little. At precision 10 there isn't even a difference.
Code used:

codeTimer.start()
codeTimer.start("update")
lightController.update() # Update the gui / physical leds
codeTimer.print("update")
codeTimer.print()

returned:

0.1769356728s since starting id: "update"
0.1769356728s since starting id: "current"

"""