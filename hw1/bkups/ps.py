import sys
import numpy as np
import math
from vectors import *

commandTypes = ["Line"]

# returns a type of post script command based on the string
def GetPSCommand(cmdString,someopts):
    cmdArgs = cmdString.split()
    commandName = cmdArgs[-1]
    if commandName not in commandTypes:
        print "PS command not supported: " + cmdString
        print "Commands currently implemented" 
        print commandTypes
        sys.exit()

    if commandName == "Line":
        firstPointX = int(cmdArgs[0])
        firstPointY = int(cmdArgs[1])
        secondPointX = int(cmdArgs[2])
        secondPointY = int(cmdArgs[3])
        # The opts parameter changes the origin from bot left, to top left
        return LineCommand(Point(firstPointX,firstPointY),Point(secondPointX,secondPointY))

# bitwise operations found from online reference
# https://code.google.com/p/pgreloaded/source/browse/pygame2/algorithms.py?r=08fe7606e1b191f388f9ebd0ff68765fd34c83ef
# Marcus von Appen (see lines 23-33)
LEFT,RIGHT,BOTTOM,UP = 1,2,4,8
def ClippingAreaCode(pnt,WT,WB,WL,WR):
    code = 0 # bits arranged T/B/R/L
    x = pnt.x
    y = pnt.y
    if x < WL:
#print "OFF LEFT CLIPPING"
        code = LEFT
    elif x > WR:
#print "OFF RIGHT CLIPPING"
        code = RIGHT
    if y > WT:
        code |= UP
    elif y < WB:
        code |= BOTTOM
#    print bin(code)
    return code

class LineCommand:
    def __init__(self, pnt1, pnt2):
        self.point1 = pnt1
        self.point2 = pnt2
#clips to viewport, recursively
    def Transform(self, xoff, yoff, sx, sy, theta):
        trans = np.matrix([[1,0,xoff],[0,1,yoff],[0,0,1]])
        rot = np.matrix([[math.cos(theta),-math.sin(theta),0],[math.sin(theta),math.cos(theta),0],[0,0,1]])
        scale= np.matrix([[sx,0,0],[0,sy,0],[0,0,1]])
        self.point1.Transform(trans * rot * scale)
    def Rotate(self, deg):
        self.point1.Rotate(deg)
        self.point2.Rotate(deg)
    def Translate(self, xoff, yoff, zoff=0):
        self.point1.Translate(xoff,yoff,zoff)
        self.point2.Translate(xoff,yoff,zoff)
    def Scale(self, sx,sy,sz=1):
        self.point1.Scale(sx,sy,sz)
        self.point2.Scale(sx,sy,sz)
    def Clip(self,opts):
#        print "ITERATION"
        WT = int(opts.yhigh) 
        WB = int(opts.ylow)
        WL = int(opts.xlow)
        WR = int(opts.xhigh)
        pnt1Code = ClippingAreaCode(self.point1,WT,WB,WL,WR)
        pnt2Code = ClippingAreaCode(self.point2,WT,WB,WL,WR)
        lineOr = pnt1Code or pnt2Code
        if lineOr == 0: # line is completely visible, so draw it
#            "print visible..."
            return True
        elif (pnt1Code & pnt2Code) != 0: # line is completely invisible, don't draw it.... parantheses
#            print "Invisible"
            return False
        # clip points, check clip again recursively 
        # bitwise comparisons with constants Left/Right/Bottom/Up (1,2,4,8) declared above
        newX = newY = 0
# (newY - y0) / (y1 - y0) = (newX - x0) / (x1 - x0)
        x0 = float(self.point1.x)
        x1 = float(self.point2.x)
        y0 = float(self.point1.y)
        y1 = float(self.point2.y)
#        print "Pnt 1: {xo}/{yo} Pnt 2: {xb}/{yb}".format(xo=x0,yo=y0,xb=x1,yb=y1)
#        print str(WL) + " <- WL\n" + str(WR) + " <- WR\n",
#        print str(WT) + " <- WT\n" + str(WB) + " <- WB\n",
#        print "Pnt 1: " + format(pnt1Code, '#06b') + '\n',
#        print "Pnt 2: " + format(pnt2Code, '#06b') + '\n',
#        print "LineOr: " + format(lineOr, '#06b') + '\n',
        dY = y1 - y0
        dX = x1 - x0
        if lineOr & UP:
#            print "Off top"
            newX = x0 + dX * ((float(WT) - y0) / dY)
            newY = WT
        elif lineOr & BOTTOM:
#            print "Off bot"
            newX = x0 + dX * ((float(WB) - y0) / dY)
            newY = WB
        elif lineOr & RIGHT:
#            print "Off right"
            newY = y0 + dY * ((float(WR) - x0) / dX)
            newX = WR
        else:
#            print "Off left"
            newY = y0 + dY * ((float(WL) - x0) / dX)
            newX = WL
        if lineOr == pnt1Code:
            self.point1.x = int(newX)
            self.point1.y = int(newY)
        else:
            self.point2.x = int(newX)
            self.point2.y = int(newY)
        return self.Clip(opts)

# This is the DDA algorithm
    def pixelsToDraw(self,opts): # the opts contains viewport size/location
        if self.Clip(opts) is False:
            print "Returning empty list"
            return []
        dX = self.point2.x - self.point1.x #run
        dY = self.point2.y - self.point1.y #rise
        slope = None
        Points = []
        # could be optimized/improved, don't need so many branching conditionals... maybe on a rainy day
        if dX != 0:
            slope = float(dY) / float(dX)
            if slope == 0: # horizontal line
                pnt1 = self.point1
                pnt2 = self.point2
                if dX <= 0: # point 2 is to the left so flip the points to make the algorithm 'easier'
                    tmp = pnt1
                    pnt1 = pnt2
                    pnt2 = tmp
                X = pnt1.x
                Y = pnt1.y
                Points.append(Point(int(round(X)),int(round(Y))))
                while X != pnt2.x - 1:
                    X = X + 1
                    Points.append(Point(int(round(X)),int(round(Y))))
            elif abs(slope) >= 1.0: # dY = 1...
                deltaX = 1.0 / slope
                pnt1 = self.point1
                pnt2 = self.point2
                if dY <= 0: # point 2 is below so flip the points to make the algorithm 'easier'
                    tmp = pnt1
                    pnt1 = pnt2
                    pnt2 = tmp
                X = float(pnt1.x)
                Y = pnt1.y
                Points.append(Point(int(round(X)),int(round(Y))))
                while Y != pnt2.y - 1:
                    X = X + deltaX
                    Y = Y + 1
                    Points.append(Point(int(round(X)),int(round(Y))))
            else: # dX = 1...
                deltaY = slope
                pnt1 = self.point1
                pnt2 = self.point2
                if dX <= 0: # point 2 is to the left so flip the points to make the algorithm 'easier'
                    tmp = pnt1
                    pnt1 = pnt2
                    pnt2 = tmp
                X = pnt1.x
                Y = float(pnt1.y)
                Points.append(Point(int(round(X)),int(round(Y))))
                while X != pnt2.x - 1:
                    X = X + 1
                    Y = Y + deltaY
                    Points.append(Point(int(round(X)),int(round(Y))))
        else: # this is a vertical line...
            X = self.point1.x
            Y = self.point1.y
            flip = 1
            if Y - self.point2.y > 0: # go down
                flip = -1
            Points.append(Point(int(round(X)),int(round(Y))))
            while Y != self.point2.y:
                Y = Y + flip
                Points.append(Point(int(round(X)),int(round(Y))))

        pixels = [] # clipping will have to happen at some point... but not right now
#for p in Points:
#            pixels.append(CoordToRow(p.x,p.y,int(opts.xhigh) - int(opts.xlow)))
        return Points
