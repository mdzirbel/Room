from reference import *
import controller


class General(controller.Controller):


    def __init__(self, name, fps=1, startImmediately=True):
        controller.Controller.__init__(self, name, fps)

        self.outputs['lights'] = []
        for i in range(NUM_STRINGS):
            self.outputs['lights'].insert(1,[])

        if startImmediately:
            self.startThread()

    def updateValues(self):
        pass

    def getLights(self):
        return self.outputs['lights']


    def tick(self):
        if self.frameNum % self.fps == 0:
            self.updateValues()
