from reference import *
import controller
import boto3


class General(controller.Controller):


    def __init__(self, name, fps=1, startImmediately=True):
        controller.Controller.__init__(self, name, fps)

        self.outputs['lights'] = []
        for i in range(NUM_STRINGS):
            self.outputs['lights'].insert(1,[])

        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.Table('LightsStatus')

        if startImmediately:
            self.startThread()

    def updateValues(self):
        pass

    def getLights(self):
        return self.outputs['lights']


    def tick(self):
        if self.frameNum % self.fps == 0:
            self.updateValues()
