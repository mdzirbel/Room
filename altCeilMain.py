import colorsys
import boto3
from threading import Thread
import datetime as dt
import time
from neopixel import *
from math import sin, cos, sqrt, atan2, radians
import random


class Alarm:
	slowRampBrightness = 25
	timeToRampSlow = 30#10 seconds to ramp to slowRampBrightness
	def __init__(self, timeToA):#time in sec from unix epoch
		self.timeToAlarm = timeToA
	def rampSlow(self):#time we are into ramping, -1 to timeToRampSlow in seconds
		now = time.time()
		return self.timeToAlarm-now
	def shouldTakeOver(self):
		#print str(self.rampSlow())+":"+str(self.timeToRampSlow >= self.rampSlow() > -1)
		return self.timeToRampSlow >= self.rampSlow() > -1  #if we are <= timeToRampSlow or one second past
	def getLights(self):
		timeTakeOver = self.rampSlow()
		if timeTakeOver<0:
			setColor(0,0,100)
			setBrightness(100)
			#setPower(True)
			time.sleep(1)
			return Color(255, 255, 255), 100
		else:
			brightness = int(((self.timeToRampSlow-self.rampSlow())/self.timeToRampSlow) * self.slowRampBrightness)
			return Color(255, 255, 255), brightness

#ID:AKIAIRWOF4IT7TVOJHXQ
#Sec:zH4ePkri9z0aBZcaKn9kyTLK5nA3SwPRvQdiYVbe



dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('LightsStatus')
#api = life360(authorization_token=authorization_token, username=username, password=password)
enableLife = False


currentColor = [0.0,0.0,0.0]
deltaColor = [0.0,0.0,0.0]
speed = 20.0#20 steps to next
stepsTaken = 20

currentBrightness = 0.0
deltaBrightness = 0
brightnessSpeed = 20.0#20 steps to next
brightnessStepsTaken = 20

alarms = []
#if api.authenticate():
def getBrightness():
	try:
		response = table.get_item(
			Key={
				'InfoId': 'Lights'
			}
		)
	except:
		print e.response['Error']['Message']
	else:
		item = response['Item']
		return int(item['brightness'])


def getColor():
	try:
		response = table.get_item(
			Key={
				'InfoId': 'Lights'
			}
		)
	except Exception as e:
		print e.response['Error']['Message']
	else:
		item = response['Item']
		return item['color']#json.dumps(item, indent=4, cls=DecimalEncoder)[0]

def setColor(h,s,v):
	response = table.update_item(
		Key={
			'InfoId': 'Lights'
		},
		UpdateExpression="set color = :c",
		ExpressionAttributeValues={
			':c': {"saturation": str(s),"hue": str(h),"brightness": str(v)}
		},
		ReturnValues="UPDATED_NEW"
	)
	return response['Attributes']['color']

def setBrightness(brightness):
	response = table.update_item(
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

def getScene():
	try:
		response = table.get_item(
			Key={
				'InfoId': 'Lights'
			}
		)
	except Exception as e:
		print e.response['Error']['Message']
	else:
		item = response['Item']
		return item['scene']


def getDist(tlat1, tlon1, tlat2, tlon2):
	R = 6373.0
	#print str(tlat1)+":"+str(tlon1)+":"+str(tlat2)+":"+str(tlon2)
	lat1 = radians(float(tlat1))
	lon1 = radians(float(tlon1))
	lat2 = radians(float(tlat2))
	lon2 = radians(float(tlon2))
	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = R * c

	#print "Result:", distance
	return distance

def setSomeoneHome(home):
	response = table.update_item(
		Key={
			'InfoId': 'Lights'
		},
		UpdateExpression="set home = :h",
		ExpressionAttributeValues={
			':h': str(home)
		},
		ReturnValues="UPDATED_NEW"
	)
	return response['Attributes']['home']


color = {'hue': .3333333, 'saturation': 1, 'brightness': 1}
#power = 'OFF'
scene = 'no scene'
brightness = 0
registerUpdates = True
dormLocation = {'lat': 39.9958422, 'lon': -83.0129177}
wasSomeoneHome = True
brightnessTicker = 0
brightnessEveryOther = 1
def updateValues():
	global color
	global scene
	global brightness
	global someoneHome
	global wasSomeoneHome
	global brightnessTicker
	global brightnessEveryOther
	someoneHome = False
	while registerUpdates:
		brightness = getBrightness()
		if brightness != 0:
			if brightness < 10 and brightness != 0:
				brightnessEveryOther = (10-brightness)%10
			else:
				brightnessEveryOther = 1
			if brightness < 11:
				brightness = 11
			brightness = int((float(brightness)-10)/9*10)#takes 10-100 and changes it to 1-100
		else:
			brightnessEveryOther = 1
		color = getColor()
		scene = getScene()
		if brightnessTicker%int((60*60)/90)==0:#every 10 seconds
			if dt.datetime.now().hour>21 or dt.datetime.now().hour<6:
				if brightness>10:
					pass
					#setBrightness(brightness-1)
		brightnessTicker = brightnessTicker + 1
		#print power+":"+str(float(color['hue'])/360.0), str(color['saturation']), str(color['brightness'])+":"+str(brightness)
		"""try:
			if enableLife:
				circles = api.get_circles()
				theCircleIWant = 0
				someoneHome = False
				for i in range(len(circles)):
					if circles[i]['name'] == 'Dorm':
						theCircleIWant = circles[i]
				if theCircleIWant != 0:
					circle = api.get_circle(theCircleIWant['id'])
					if 'members' in circle:
						for i in range(len(circle['members'])):
							memlocation = circle['members'][i]['location']
							if 'latitude' in memlocation:
								kmAway = getDist(dormLocation['lat'], dormLocation['lon'], memlocation['latitude'], memlocation['longitude'])
							else:
								kmAway = 99999
							#print circle['members'][i]
							#print circle['members'][i]['firstName']+":"+str(kmAway)+":"+str(time.time()-int(memlocation['timestamp']))+":"+circle['members'][i]['issues']['disconnected']
							if kmAway<.07 and (circle['members'][i]['features']['disconnected']=='0'):# and (time.time()-int(memlocation['timestamp']))<500:
								someoneHome = True
					setSomeoneHome(someoneHome)
				if wasSomeoneHome and not someoneHome:
					print 'Someone was home but not anymore, turning off lights'
					setPower(False)
				wasSomeoneHome = someoneHome
			print 'Power:'+str(power)+', Brightness:'+str(brightness)+', Someone Home:'+str(someoneHome)
		except:
			print "Life Error"
			#print someoneHome
			#id = circles[0]['id']
			#circle = api.get_circle(id)"""
		time.sleep(1)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
	return Color(0, pos * 3, 255 - pos * 3)


timer = 0

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0)
strip.begin()
strip2 = Adafruit_NeoPixel(LED_COUNT, LED_PIN2, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
strip2.begin()

oldScene = 'no scene'
def initScene():
	if scene == 'scene3':
		initStars()
	elif scene == 'scene4':
		initRain()
def initStars():
	for ll in range(len(dataBuffer)):
		for ii in range(strip.numPixels()):
			dataBuffer[ll][ii] = 0
	"""while starsInSky<10:
		val = int(random.random() * strip.numPixels())
		stripNum = int(random.random() * 2)
		if dataBuffer[stripNum][val]==0:
			dataBuffer[stripNum][val] = int(random.random()*100)
			starsInSky = starsInSky + 1"""
rainSpeed = 10
def initRain():#goingTo<<16 | speed<<8 | current
	for ll in range(len(dataBuffer)):
		for ii in range(strip.numPixels()):
			redefineRain(ll,ii)
def redefineRain(stripNum, ledNum):
	goingTo = int(random.random() * 255)
	speed = int(random.random() * (rainSpeed-1))+1#0 to rainspeed
	current = int(random.random() * 255)
	dataBuffer[stripNum][ledNum] = goingTo << 16 | speed << 8 | current
def defineRain(stripNum, ledNum, goingTo, speed, current):
	dataBuffer[stripNum][ledNum] = goingTo << 16 | speed << 8 | current
thread = Thread(target = updateValues)
thread.start()
dataBuffer = [[],[]]
dataBuffer[0] = [0 for _ in range(strip.numPixels())]
dataBuffer[1] = dataBuffer[0][:]
starBlue = 20
chaseTicker = 0#number count
chaseCounter = 0#once ever blank cycles
numberEvery = 4
#alarms.append(Alarm(time.time()+11))

try:
	while True:
		timer = timer + 1
		if timer > 255:
			timer = 0
		if scene != oldScene:
			initScene()
		oldScene = scene
		takenOver = False
		for alarm in alarms:
			if alarm.shouldTakeOver():
				takenOver = True
				lightsFromAlarm = alarm.getLights()
				brightness = lightsFromAlarm[1]
				for i in range(strip.numPixels()):
					#print alarm.getLights()
					strip.setPixelColor(i,  lightsFromAlarm[0])
					strip2.setPixelColor(i, lightsFromAlarm[0])
		if brightnessStepsTaken == brightnessSpeed and brightness!=currentBrightness:
			deltaBrightness = (brightness - currentBrightness) / brightnessSpeed
			brightnessStepsTaken = 0
		elif brightnessStepsTaken < brightnessSpeed:
			brightnessStepsTaken += 1
		if brightnessStepsTaken < brightnessSpeed:
			currentBrightness += deltaBrightness
		if scene == 'scene6':
			chaseCounter += 1
			if chaseCounter%1==0:
				chaseTicker += 1
		elif scene == 'scene3':
			if random.random() > .7:
				foundSpot = False
				while not foundSpot:
					val = int(random.random() * strip.numPixels())
					stripNum = int(random.random() * 2)
					if dataBuffer[stripNum][val] == 0:
						dataBuffer[stripNum][val] = 1
						foundSpot = True
		if not takenOver:
			if scene == 'no scene':
				rgb = colorsys.hsv_to_rgb(float(color['hue']) / 360.0, float(color['saturation']), float(color['brightness']))
				# currentColors[0][i] = rgb
				# print stepsTaken[i]==speed
				#print rgb
				if stepsTaken == speed and (abs(currentColor[0] - rgb[0])>.001 or abs(currentColor[1] - rgb[1])>.001 or abs(currentColor[2] - rgb[2])>.001):  # we are done and it just changed, we need to calcualte new deltas and reset stepsTaken
					deltaColor[0] = (rgb[0] - currentColor[0]) / speed  # G, it will take 'speed' steps to get to proper color
					deltaColor[1] = (rgb[1] - currentColor[1]) / speed  # R
					deltaColor[2] = (rgb[2] - currentColor[2]) / speed  # B
					stepsTaken = 0
				elif stepsTaken < speed:
					stepsTaken += 1
				if stepsTaken < speed:  # we are changing values
					currentColor[0] = currentColor[0] + deltaColor[0]
					currentColor[1] = currentColor[1] + deltaColor[1]
					currentColor[2] = currentColor[2] + deltaColor[2]
				#print str(deltaColor[1])+":"+str(currentColor[1])+":"+str(stepsTaken)
			for i in range(strip.numPixels()):
				colorRGB = [0,0]
				if scene == 'scene1':
					colorRGB[0] = wheel(timer)
					colorRGB[1] = wheel(timer)
				elif scene == 'scene2':
					colorRGB[0] = wheel((timer+int(i/float(strip.numPixels())*255.0))%255)
					colorRGB[1] = wheel((timer+int(i/float(strip.numPixels())*255.0))%255)
				elif scene == 'scene3':
					for l in range(len(dataBuffer)):
						if dataBuffer[l][i]!=0:
							if dataBuffer[l][i]<50:
								colorRGB[l] = Color(int(dataBuffer[l][i]/50.0*255), int(dataBuffer[l][i]/50.0*255), int(dataBuffer[l][i]/50.0*255))
							else:
								colorStar = int((50-(dataBuffer[l][i]-50))/50.0*255)
								blueColor = colorStar
								if colorStar < starBlue:
									blueColor = starBlue
								colorRGB[l] = Color(colorStar, colorStar, blueColor)
							dataBuffer[l][i] = dataBuffer[l][i] + 2
							if dataBuffer[l][i]>=100:
								dataBuffer[l][i] = 0
						else:
							colorRGB[l] = Color(0,0,starBlue)
				elif scene == 'scene4':
					for l in range(len(dataBuffer)):
						current = (dataBuffer[l][i]) & 0b11111111
						speed = (dataBuffer[l][i] >> 8) & 0b11111111
						goingTo = (dataBuffer[l][i] >> 16) & 0b11111111
						if abs(current-goingTo)<speed:
							colorRGB[l] = Color(0,0,goingTo)
							redefineRain(l, i)
						else:
							if current>goingTo:
								current = current - speed
							else:
								current = current + speed
							defineRain(l, i, goingTo, speed, current)
							colorRGB[l] = Color(0,0,current)
				elif scene == 'scene5':
					for l in range(2):
						if random.random()>.99:
							dataBuffer[l][i] = Color(int(random.random()*255), int(random.random()*255), int(random.random()*255))
						colorRGB[l] = dataBuffer[l][i]
				elif scene == 'scene6':
					for l in range(2):
						if (i+chaseTicker)%numberEvery==0:
							rgb = colorsys.hsv_to_rgb(float(color['hue']) / 360.0, float(color['saturation']), float(color['brightness']))
							colorRGB[l] = Color(int(rgb[1]*255), int(rgb[0]*255), int(rgb[2]*255))
						else:
							colorRGB[l] = 0
				else:
					if(i%brightnessEveryOther)==0:
						colorRGB[0] = Color(int(currentColor[1]*255), int(currentColor[0]*255), int(currentColor[2]*255))
						colorRGB[1] = Color(int(currentColor[1]*255), int(currentColor[0]*255), int(currentColor[2]*255))
					else:
						colorRGB[0] = 0
						colorRGB[1] = 0
				strip.setPixelColor(i, colorRGB[0])
				strip2.setPixelColor(i, colorRGB[1])
		#print time.time()
		strip.setBrightness(int(currentBrightness*2.55))
		strip2.setBrightness(int(currentBrightness*2.55))
		strip.show()
		strip2.show()
		time.sleep(.002)
finally:
	registerUpdates = False