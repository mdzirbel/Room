from reference import *
import controller
import colorsys

class General(controller.Controller):
    def __init__(self, name, fps=1, startImmediately=True):
        controller.Controller.__init__(self, name, fps, True)

        self.lights = []
        for i in range(NUM_STRINGS):
            self.lights.append([])
            for k in range(PIXELS_PER_STRING):
                self.lights[i].append("black")

        self.color = {'hue': .3333333, 'saturation': 1, 'brightness': 1}


        if startImmediately:
            self.startThread()

    def updateValues(self):
        color = getColorAWS()
        rgb = colorsys.hsv_to_rgb(float(color['hue']) / 360.0, float(color['saturation']), float(color['brightness']))
        for i in range(NUM_STRINGS):
            for k in range(PIXELS_PER_STRING):
                self.lights[i][k] = (rgb[0]*255, rgb[1]*255, rgb[2]*255)

    def getLights(self):
        return self.lights

    def tick(self):
        if self.frameNum % self.fps == 0:
            self.updateValues()
