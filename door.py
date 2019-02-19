import RPi.GPIO as GPIO
import time
import boto3
import Adafruit_ADS1x15
import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
pwm = GPIO.PWM(12, 100)
pwm.start(5)

currentServoPos = 0
angleStep = 3

easyOpen = False

def calcAngle(ang):
    return ang/180.0*22.0+2.5
    setServo(0)
    setServo(180)


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('LightsStatus')
def getLock():
    try:
        response = table.get_item(
            Key={
                'InfoId': 'Lights'
            }
        )
    except Exception as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        return item['lockState'] == 'true'

def getAuto():
    try:
        response = table.get_item(
            Key={
                'InfoId': 'Lights'
            }
        )
    except Exception as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        return item['autoBrightness'] == 'true'
def setBrightness(brightness):
    if brightness<0:
        brightness = 0
    if brightness>100:
        brightness = 100
    print("brightness to: "+str(brightness))
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
def getBrightness():
    try:
        response = table.get_item(
            Key={
                'InfoId': 'Lights'
            }
        )
    except:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        return int(item['brightness'])
def setLock(lock):
    global wasLocked
    wasLocked = lock
    if lock:
        lockS = 'true'
    else:
        lockS = 'false'
    response = table.update_item(
        Key={
            'InfoId': 'Lights'
        },
        UpdateExpression="set lockState = :l",
        ExpressionAttributeValues={
            ':l': str(lockS)
        },
        ReturnValues="UPDATED_NEW"
    )
    if response['Attributes']['lockState'] == 'true':
        return 'LOCKED'
    else:
        return 'UNLOCKED'
def setServo(ang):
    time.sleep(.05)
    setLED(True, True, False)
    if ang==-1:
        pwm.ChangeDutyCycle(0)
        return
    global angleStep
    global currentServoPos
    #print(currentServoPos)
    if abs(ang-currentServoPos)>angleStep:
        if ang-currentServoPos>0:
            currentServoPos = currentServoPos+angleStep
            pwm.ChangeDutyCycle(calcAngle(currentServoPos))
        else:
            currentServoPos = currentServoPos-angleStep
            pwm.ChangeDutyCycle(calcAngle(currentServoPos))
        setServo(ang)
    else:#Within stepSize degrees of our target
        pwm.ChangeDutyCycle(calcAngle(ang))
        setServo(-1)#Turn off servo after we dont need it moving anymore
def getSomeoneHome():
    try:
        response = table.get_item(
            Key={
                'InfoId': 'Lights'
            }
        )
    except Exception as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        return item['home']=='True'
def lock():
    global easyOpen
    setServo(lockAng)
    setServo(neuAng)
    setLock(True)
    if easyOpen:
        setLED(False, False, True)
    else:
        setLED(True, False, False)
def unlock():
    setServo(unlockedAng)
    setServo(neuAng)
    setLock(False)
    setLED(False, True, False)
def setLED(red, green, blue):
    GPIO.output(17, red)
    GPIO.output(27, green)
    GPIO.output(22, blue)
wasLocked = False
timeDoorOpen = 0
lockAng = 0
neuAng = 90
unlockedAng = 180
setServo(lockAng)
setServo(unlockedAng)
setServo(neuAng)
lock()
ticker = 0
timeCovered = 0
targetVal = 1700
tol = 200
try:
    while True:
        adcVal = adc.read_adc(3, gain=GAIN)
        ambi = adc.read_adc(0, gain=GAIN)
        doorClosed = GPIO.input(23)
        if ticker%5==0:# once every time iterations, or .5 seconds
            currentLock = getLock()
            if currentLock and not wasLocked:
                lock()
            if not currentLock and wasLocked:
                unlock()
            wasLocked = currentLock
            now = datetime.datetime.now()
            print("Door open time: "+str(timeDoorOpen)+", Time Covered:"+str(timeCovered)+", Locked:"+str(wasLocked)+", ADC:"+str(adcVal)+", easyOpen:"+str(easyOpen)+", ambi:"+str(ambi)+", hour: "+str(now.hour))
            brightness = getBrightness()
            if ticker%20==0 and getAuto() and (brightness>10 or (12 < now.hour < 20) and doorClosed):
                if ambi<targetVal-tol:
                    setBrightness(brightness+2)
                elif ambi>targetVal+tol:
                    setBrightness(brightness-2)
            if adcVal<100:
                timeCovered = timeCovered + 1
            else:
                timeCovered = 0
            if timeCovered>=60 or (timeCovered>1 and easyOpen):
                easyOpen = False
                unlock()
        if GPIO.input(24):
            if wasLocked:
                unlock()
            else:
                lock()
            time.sleep(1)
        if GPIO.input(25):
            easyOpen = True
            unlock()
        ticker = ticker + 1
        if timeDoorOpen>10 and doorClosed:
            #time.sleep(.2)
            lock()
        if not doorClosed:
            timeDoorOpen = timeDoorOpen + 1
        else:
            timeDoorOpen = 0
        time.sleep(.1)
except Exception as e:
    print(e)
finally:
    pwm.stop()
    GPIO.cleanup()