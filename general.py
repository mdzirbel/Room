from reference import *
import controller
import boto3
import colorsys

class General(controller.Controller):
    def getBrightness(self):
        try:
            response = self.table.get_item(
                Key={
                    'InfoId': 'Lights'
                }
            )
        except Exception as e:
            print e.response['Error']['Message']
        else:
            item = response['Item']
            return int(item['brightness'])

    def getColor(self):
        try:
            response = self.table.get_item(
                Key={
                    'InfoId': 'Lights'
                }
            )
        except Exception as e:
            print e.response['Error']['Message']
        else:
            item = response['Item']
            return item['color']  # json.dumps(item, indent=4, cls=DecimalEncoder)[0]

    def setColor(self, h, s, v):
        response = self.table.update_item(
            Key={
                'InfoId': 'Lights'
            },
            UpdateExpression="set color = :c",
            ExpressionAttributeValues={
                ':c': {"saturation": str(s), "hue": str(h), "brightness": str(v)}
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']['color']

    def setBrightness(self, brightness):
        response = self.table.update_item(
            Key={
                'InfoId': 'Lights'
            },
            UpdateExpression="set brightness = :b",
            ExpressionAttributeValues={
                ':b': str(brightness)
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']['brightness']

    def getScene(self):
        try:
            response = self.table.get_item(
                Key={
                    'InfoId': 'Lights'
                }
            )
        except Exception as e:
            print e.response['Error']['Message']
        else:
            item = response['Item']
            return item['scene']

    def __init__(self, name, fps=1, startImmediately=True):
        controller.Controller.__init__(self, name, fps)

        self.lights = []
        for i in range(NUM_STRINGS):
            self.lights.insert(1,[])

        self.color = {'hue': .3333333, 'saturation': 1, 'brightness': 1}

        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.Table('LightsStatus')


        if startImmediately:
            self.startThread()

    def updateValues(self):
        color = self.getColor()
        rgb = colorsys.hsv_to_rgb(float(color['hue']) / 360.0, float(color['saturation']), float(color['brightness']))
        for i in range(NUM_STRINGS):
            for k in range(PIXELS_PER_STRING):
                self.lights[i][k] = rgb

    def getLights(self):
        return self.lights


    def tick(self):
        if self.frameNum % self.fps == 0:
            self.updateValues()
