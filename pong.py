from reference import *

class Pong:

    def __init__(self, beingPressed, fps=30, wallColor="white", backgroundColor="black"):
        self.fps = fps
        self.beingPressed = beingPressed

        self.left = MovingWall("left", "white")
        self.right = MovingWall("right", "white")
        self.ball = Ball()

        self.height = .6 # Wall height in meters

        self.wallNumPixels = int((150/2.5)*self.height) # For reference

        # For quick use later we now make the arrays
        wallColor = toHex(wallColor)
        backgroundColor = toHex(backgroundColor)

        self.backgroundPixels = [backgroundColor for _ in range(150-self.wallNumPixels)]
        self.wallPixels = [wallColor for _ in range(self.wallNumPixels)]

        self.keepRunningThread = True

        self.lights = {
            "lights": self.getLights(),
            "laser": self.getLaser()
        }

        threading.Thread(target=self.move).start()

    def stop(self):
        self.keepRunningThread = False

    def getLights(self):

        leftY = int(self.left.pos*(150/config["ceiling_size"][1])-self.wallNumPixels/2)
        leftColumn = self.backgroundPixels[:]
        leftColumn[leftY:leftY] = self.wallPixels

        rightY = int(self.right.pos*(150/config["ceiling_size"][1])-self.wallNumPixels/2)
        rightColumn = self.backgroundPixels[:]
        rightColumn[rightY:rightY] = self.wallPixels

        return [leftColumn, [],[],[],[],[],[],[],[],[],[], rightColumn]

    def updateLights(self):
        self.lights["lights"] = self.getLights()

    def getLaser(self):
        return self.ball.pos

    def updateLaser(self):
        self.lights["laser"] = self.getLaser()

    def moveWalls(self):
        if 'a' in self.beingPressed and not 'z' in self.beingPressed:
            self.moveLeftUp()
        if 'z' in self.beingPressed and not 'a' in self.beingPressed:
            self.moveLeftDown()
        if '/' in self.beingPressed and not '\'' in self.beingPressed:
            self.moveRightDown()
        if '\'' in self.beingPressed and not '/' in self.beingPressed:
            self.moveRightUp()

    def moveLeftUp(self):
        self.left.move(self.left.pos - .07)
        # print("left up")
    def moveLeftDown(self):
        self.left.move(self.left.pos + .07)
        # print("left down")
    def moveRightUp(self):
        self.right.move(self.right.pos - .07)
        # print("right up")
    def moveRightDown(self):
        self.right.move(self.right.pos + .07)
        # print("right down")

    def move(self):

        try:
            while self.keepRunningThread:

                startTime = time.time() # Record the start time of the function

                # Function code:
                self.ball.move(self.left, self.right)
                self.ball.speedUp()
                self.moveWalls()
                self.updateLights()

                elapsedTime = time.time() - startTime # Find the time it took to run move code
                time.sleep(1/self.fps - elapsedTime) # Sleep the time minus the time execution took

        finally:
            stopAllThreads()



class Ball:
    def __init__(self):
        self.pos = [config["ceiling_size"][0] / 2, config["ceiling_size"][1] / 2]  # center of the ball
        self.vel = [.02, .02]
        self.size = [25, 25]

    def startBall(self):
        self.pos = [config["ceiling_size"][0]/2, config["ceiling_size"][1]/2] # center of the ball
        self.vel = [.03,.03]
        self.size = [25, 25]

    def move(self, left, right):
        self.pos[0] = self.pos[0] + self.vel[0]
        self.pos[1] = self.pos[1] + self.vel[1]

        # If you hit the top or bottom
        if self.pos[1]<=0 or self.pos[1]>=config["ceiling_size"][1]:
            self.vel[1] = -self.vel[1]

        # If you may be moving out of bounds
        if self.pos[0] <= 0 or self.pos[0] >= config["ceiling_size"][0]:

            # If you hit a player wall
            if self.vel[0] > 0 and self.pos[0] > config["ceiling_size"][0]/2 and right.pos - right.height / 2 < self.pos[1] < right.pos + right.height / 2:
                offset = (self.pos[1] - right.pos) / right.height * 2
                self.vel[1] = self.vel[0] * offset * 1.2
                self.vel[0] = -self.vel[0]
            elif self.vel[0] < 0 and self.pos[0] < config["ceiling_size"][0]/2 and left.pos - left.height / 2 < self.pos[1] < left.pos + left.height / 2:
                offset = (self.pos[1] - left.pos) / left.height * 2
                self.vel[1] = - self.vel[0] * offset * 1.2
                self.vel[0] = -self.vel[0]
            else: # You moved out of bounds
                self.startBall()

    def speedUp(self):
        self.vel[0] *= 1.0015
        self.vel[1] *= 1.0015

class MovingWall:
    def __init__(self, side, color, height=.6):
        assert side == "right" or side == "left", "Side must be right or left"  # Ensure side is set correctly
        self.side = side
        self.pos = config["ceiling_size"][1] / 2 # Center position in meters
        self.height = height # Size in meters
        self.color = color

    def move(self, pos):
        self.pos = max(min(pos, config["ceiling_size"][1]-self.height/2), self.height/2)