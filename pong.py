from reference import *
import controller
import random

class Pong(controller.Controller):

    def __init__(self, beingPressed, name, fps=30, startImmediately=True, wallColor="white", backgroundColor="black"):
        controller.Controller.__init__(self, name, fps)

        self.beingPressed = beingPressed

        self.left = MovingWall("left", "white")
        self.right = MovingWall("right", "white")
        self.ball = Ball()

        self.height = .6 # Wall height in meters

        self.wallNumPixels = int((PIXELS_PER_STRING / 2.5) * self.height) # For reference

        # For quick use later we now make the arrays
        wallColor = toHex(wallColor)
        backgroundColor = toHex(backgroundColor)

        self.backgroundPixels = [backgroundColor for _ in range(PIXELS_PER_STRING - self.wallNumPixels)]
        self.wallPixels = [wallColor for _ in range(self.wallNumPixels)]

        self.outputs = {
            "lights": self.getLights(),
            "laser": self.getLaser()
        }

        if startImmediately:
            self.startThread()

    def getLights(self):

        # Make left wall
        leftY = int(self.left.pos * (PIXELS_PER_STRING / config["ceiling_size"][1]) - self.wallNumPixels / 2)
        leftColumn = self.backgroundPixels[:]
        leftColumn[leftY:leftY] = self.wallPixels

        # Make right wall
        rightY = int(self.right.pos * (PIXELS_PER_STRING / config["ceiling_size"][1]) - self.wallNumPixels / 2)
        rightColumn = self.backgroundPixels[:]
        rightColumn[rightY:rightY] = self.wallPixels

        lights = [leftColumn, rightColumn]

        # Add black in the middle
        for i in range(NUM_STRINGS - 2):
            lights.insert(1,[])

        # return ["red", "orange", "yellow", "green", "blue", "purple", "violet", "black", "white", "cyan"]
        return lights #[leftColumn, [],[],[],[],[],[],[],[],[],[], rightColumn]

    def getLaser(self):
        return self.ball.pos

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
        # print "left up"
    def moveLeftDown(self):
        self.left.move(self.left.pos + .07)
        # print "left down"
    def moveRightUp(self):
        self.right.move(self.right.pos - .07)
        # print "right up"
    def moveRightDown(self):
        self.right.move(self.right.pos + .07)
        # print "right down"

    def changeWallColor(self, color):
        self.wallPixels = [color for _ in range(self.wallNumPixels)]

    def tick(self):
        self.ball.move(self.left, self.right)
        self.ball.speedUp()
        self.moveWalls()


class Ball:
    def __init__(self):
        self.pos = [config["ceiling_size"][0] / 2., config["ceiling_size"][1] / 2.]  # center of the ball
        self.vel = [.02, .02]
        self.size = [25, 25]

    def restartBall(self):
        # self.pos is changed carefully without changing the pointer to the information
        self.pos[0] = config["ceiling_size"][0] / 2. # center x of the ball
        self.pos[1] = config["ceiling_size"][1] / 2. # center y of the ball
        self.vel = [random.choice([.03, -.03]),random.randint(-40,41)*.001]
        self.size = [25, 25]

    def move(self, left, right):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # If you hit the top or bottom
        if self.pos[1]<=0 or self.pos[1]>=config["ceiling_size"][1]:
            self.vel[1] = -self.vel[1]

        # If you are heading out of bounds
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
                self.restartBall()

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
