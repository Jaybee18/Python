from window import Window
import pygame
from math import atan2, cos, degrees, pi, radians, sin, sqrt, tan, isinf
import bezier
import numpy

step = 1

class Point:
    def __init__(self, pos, angle, end) -> None:
        self.pos = pos
        self.angle = angle
        self.radius = 30
        self.street = Street(pos, end)

        self.street.angleStart = self.angle
        if(end[0] < pos[0]):
            self.street.angleStart += 180

        self.street.update()

def calculatePoints(curve):
    global step
    
    res = []
    for x in range(int(curve.length/step)):
        p = curve.evaluate(x/int(curve.length/step)).tolist()
        res.append((p[0][0], p[1][0]))
    
    return res

def getGradientAt(curve, point:float):
    tmp = curve.evaluate_hodograph(point)
    m = tmp[1][0] / tmp[0][0]
    return m

def getTangentAt(curve, point:float):
    tmp = curve.evaluate(point)
    spacePoint = [tmp[0][0], tmp[1][0]]
    tmp = curve.evaluate_hodograph(point)
    m = tmp[1][0] / tmp[0][0]
    samplePoint = [spacePoint[0] + tmp[0][0], spacePoint[1] + tmp[1][0]]
    b = samplePoint[1] - m * samplePoint[0]
    f = lambda x: m * x + b
    return f

def getNormalAt(curve, point:float):
    tmp = curve.evaluate(point)
    spacePoint = [tmp[0][0], tmp[1][0]]
    tmp = curve.evaluate_hodograph(point)
    m = tmp[1][0] / tmp[0][0]
    m = -1/m
    samplePoint = [spacePoint[0] + m, spacePoint[1] + m]
    b = samplePoint[1] - m * samplePoint[0]
    f = lambda x: m * x + b
    return f

def getAngleBetweenVectors(v1, v2):
    return atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])

def movePointY(p, delta):
    return [p[0], p[1] + delta]

def movePointX(p, delta):
    return [p[0] + delta, p[1]]

def getDistanceBetweenPoints(p1, p2):
    return sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
def rotatePoint(center, point, angle):
    newPoint = point.copy()

    s = sin(angle)
    c = cos(angle)

    newPoint[0] -= center[0]
    newPoint[1] -= center[1]
    
    xnew = newPoint[0] * c - newPoint[1] * s
    ynew = newPoint[0] * s + newPoint[1] * c

    newPoint[0] = xnew + center[0]
    newPoint[1] = ynew + center[1]

    return newPoint

def calculateEdgepoints(curve, points, offset):
    global w, step
    res = []
    for p in points:
        center = p
        rp = movePointX(center, offset)
        
        location = points.index(p)/int(curve.length/step)
        grad = getGradientAt(curve, location)
        angle = numpy.arctan(grad) + pi/2

        #print(grad)
        #if isneginf(grad) or grad == 0.0:
        #    print(p)
        #    w.drawPoint(list(p), color=(0, 0, 255))

        newP = rotatePoint(center, rp, angle)
        res.append(newP)
    return res

class Street:
    def __init__(self, p1, p2) -> None:
        self.start = p1
        self.end = p2
        self.curve = None
        self.angleStart = 0.0
        self.angleEnd = 0.0
        self.points = []
        self.upperPoints = []
        self.lowerPoints = []

        self.update()

    def update(self):
        xDelta = self.end[0] - self.start[0]
        yDelta = self.end[1] - self.start[1]
        controlPoints = [self.start, [self.start[0] + xDelta/2, self.start[1]], [self.start[0] + xDelta/2, self.end[1]], self.end]
        controlPoints[2] = rotatePoint(controlPoints[3], controlPoints[2], radians(self.angleEnd))
        controlPoints[1] = rotatePoint(controlPoints[0], controlPoints[1], radians(self.angleStart))
        nodes = numpy.asfortranarray([
            [controlPoints[0][0], controlPoints[1][0], controlPoints[2][0], controlPoints[3][0]],
            [controlPoints[0][1], controlPoints[1][1], controlPoints[2][1], controlPoints[3][1]]
        ])
        self.curve = bezier.Curve(nodes, degree=3)
        self.points = calculatePoints(self.curve)
        self.upperPoints = calculateEdgepoints(self.curve, self.points, 20)
        self.lowerPoints = calculateEdgepoints(self.curve, self.points, -20)

    def draw(self, w:Window) -> None:
        # draw curve
        for i in range(len(self.points)-1):
            if(i % 40 <= 10):
                w.drawLine(self.points[i], self.points[i+1])
            w.drawPoint(self.upperPoints[i])
            w.drawPoint(self.lowerPoints[i])
            continue
            w.drawLine(self.upperPoints[i], self.upperPoints[i+1])
            w.drawLine(self.lowerPoints[i], self.lowerPoints[i+1])

w = Window((600, 600))
snapPoints = [Point((500, 500), 90, (1000, 600)), 
              Point((500, 300), 0, (600, 300)), 
              Point((500, 100), 320, (1000, 300)),
              Point((300, 500), 180, (0,1300))]
p1 = (0, 50)
p2 = [400, 300]
curve = None
angleEnd = 0.0
angleStart = 0.0
mouseDown = False
street = Street(p1, p2)

#delta = 10
#def down() : p2[1] -= delta
#def up()   : p2[1] += delta
#def left() : p2[0] -= delta
#def right(): p2[0] += delta
#w.bindFunction(pygame.K_s, up, [w.KEYHOLD])
#w.bindFunction(pygame.K_w, down, [w.KEYHOLD])
#w.bindFunction(pygame.K_a, left, [w.KEYHOLD])
#w.bindFunction(pygame.K_d, right, [w.KEYHOLD])

def pressed(): global mouseDown; mouseDown = not mouseDown
w.bindFunction(w.MOUSELEFT, pressed, [pygame.MOUSEBUTTONDOWN])

xDelta = p2[0] - p1[0]
yDelta = p2[1] - p1[1]
controlPoints = [p1, [p1[0] + xDelta/2, p1[1]], [p1[0] + xDelta/2, p2[1]], p2]

while 1:
    w.clear()

    if mouseDown:
        street.end = pygame.mouse.get_pos()
    
    for p in snapPoints:
        p.street.draw(w)
        if getDistanceBetweenPoints(p.pos, street.end) < p.radius:
            street.angleEnd = p.angle
            street.end = p.pos

    street.update()
    street.draw(w)

    w.update()
