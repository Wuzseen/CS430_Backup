import sys
import numpy as np
import math
from vectors import *

#hey look, globals... :/
commandTypes = ["f","v"]
verts = []
tris = [] # list of vert indices (be sure to subtract 1....

def BuildSMF(cmdString,someopts):
    global verts
    global tris
    cmdArgs = cmdString.split()
    commandName = cmdArgs[0]
    if commandName not in commandTypes:
        print "SMF command not supported: " + cmdString
        print "Commands currently implemented:" 
        print commandTypes
        sys.exit()
    if commandName == "f": # subtract 1 since SMF is not 0 based.
        tris.append([int(cmdArgs[1]) - 1,int(cmdArgs[2]) - 1,int(cmdArgs[3]) - 1])
    elif commandName == "v":
        verts.append(Point(float(cmdArgs[1]),float(cmdArgs[2]),float(cmdArgs[3])))

def TheThirdDimension(someopts):
    if someopts.parallel is True:
        transMatrix = ParallelTranslationMatrix(someopts)
        m = [[1,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,0,1]]
    else:
        transMatrix = PerspectiveTranslationMatrix(someopts)
        d = someopts.zprp / (someopts.B - someopts.zprp)
        m = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,1/d,0]]
    newVerts = []
#   UNCOMMENT TO SEE TRANSFORMATION MATRIX
#    print transMatrix
    W = someopts.zvup
    for p in verts:
        if p is None:
            continue
        if someopts.parallel is True:
            inner = np.dot(transMatrix,p.Matrix())
            # reject test should go here....
            pNew = np.dot(m,inner)
            pApp = Point(pNew.item(0),pNew.item(1),pNew.item(2))
            newVerts.append(pApp)
        else:
            inner = np.dot(transMatrix,p.Matrix())
            pNew = np.dot(m,inner)
            zd = pNew.item(3)
            pApp = Point(pNew.item(0)/zd,pNew.item(1)/zd,d)
            newVerts.append(pApp)

    lineCommands = []
    for tri in tris:
        l1 = LineCommand(newVerts[tri[0]],newVerts[tri[1]])
        l2 = LineCommand(newVerts[tri[1]],newVerts[tri[2]])
        l3 = LineCommand(newVerts[tri[2]],newVerts[tri[0]])
        lineCommands.append(l1)
        lineCommands.append(l2)
        lineCommands.append(l3)
    return lineCommands
#newVerts.append(p.PointScale(transMatrix)) 

# bitwise operations found from online reference
# https://code.google.com/p/pgreloaded/source/browse/pygame2/algorithms.py?r=08fe7606e1b191f388f9ebd0ff68765fd34c83ef
# Marcus von Appen (see lines 23-33)
LEFT,RIGHT,BOTTOM,UP = 1,2,4,8
def ClippingAreaCode(pnt,WT,WB,WL,WR):
    code = 0 # bits arranged T/B/R/L
    x = pnt.x
    y = pnt.y
    if x < WL:
        code = LEFT
    elif x > WR:
        code = RIGHT
    if y > WT:
        code |= UP
    elif y < WB:
        code |= BOTTOM
    return code

class LineCommand:
    def __init__(self, pnt1, pnt2):
        self.point1 = Point(pnt1.x,pnt1.y,pnt1.z)
        self.point2 = Point(pnt2.x,pnt2.y,pnt2.z)
#clips to viewport, recursively
    def __str__(self):
        return "P1: " + str(self.point1) + " P2: " + str(self.point2)
    def minY(self):
        if self.point1.y < self.point2.y:
            return self.point1.y
        return self.point2.y
    def maxY(self):
        if self.point1.y > self.point2.y:
            return self.point1.y
        return self.point2.y
    def slope(self):
        dX = self.point1.x - self.point2.x
        dY = self.point1.y - self.point2.y
        if dX == 0: # if the slope is 0 or undefined, it should have been skipped
            return None
        return float(dY) / float(dX)
    def XOnScanY(self,scanY):
# y = mx + b... x = (y - b) / m
        if self.point1.x == self.point2.x:
            return int(self.point1.x)
        slope = self.slope()
        if slope == None:
            return None
        # b = y - mx
        b = self.point1.y - self.point1.x * slope
        return int(float(scanY - b) / float(slope))
# find value on line where f(X) = scanY
    def Transform(self, xoff, yoff, sx, sy, theta):
        trans = np.matrix([[1,0,xoff],[0,1,yoff],[0,0,1]])
        rot = np.matrix([[math.cos(theta),-math.sin(theta),0],[math.sin(theta),math.cos(theta),0],[0,0,1]])
        scale= np.matrix([[sx,0,0],[0,sy,0],[0,0,1]])
        self.point1.Transform(trans * rot * scale)
    def ViewTransform(self,opts):
        if opts.parallel == True:
            WT = 1#int(opts.yviewhigh) 
            WB = -1#int(opts.yviewlow)
            WL = -1#int(opts.xviewlow)
            WR = 1#int(opts.xviewhigh)
        else:
            zproj = opts.zprp / (opts.B - opts.zprp) # d....
            WT = abs(zproj)#int(opts.yviewhigh) 
            WB = -abs(zproj)#int(opts.yviewlow)
            WL = -abs(zproj)#int(opts.xviewlow)
            WR = abs(zproj)#int(opts.xviewhigh)
        VT = int(opts.yviewhigh) 
        VB = int(opts.yviewlow)
        VL = int(opts.xviewlow)
        VR = int(opts.xviewhigh)
        self.point1.Translate(-WL,-WB)
        self.point2.Translate(-WL,-WB)
        Sx = float(VR - VL) / float(WR - WL)
        Sy = float(VT - VB) / float(WT - WB)
        self.point1.Scale(Sx,Sy)
        self.point2.Scale(Sx,Sy)
        self.point1.Translate(VL,VB)
        self.point2.Translate(VL,VB)
#self.point2 = Point(p2X,p2Y)
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
        if opts.parallel == True:
            WT = 1#int(opts.yviewhigh) 
            WB = -1#int(opts.yviewlow)
            WL = -1#int(opts.xviewlow)
            WR = 1#int(opts.xviewhigh)
        else:
            zproj = opts.zprp / (opts.B - opts.zprp) # d....
            WT = abs(zproj)#int(opts.yviewhigh) 
            WB = -abs(zproj)#int(opts.yviewlow)
            WL = -abs(zproj)#int(opts.xviewlow)
            WR = abs(zproj)
        pnt1Code = ClippingAreaCode(self.point1,WT,WB,WL,WR)
        pnt2Code = ClippingAreaCode(self.point2,WT,WB,WL,WR)
        lineOr = pnt1Code or pnt2Code
        if lineOr == 0: # line is completely visible, so draw it
            return True
        elif (pnt1Code & pnt2Code) != 0: # line is completely invisible, don't draw it.... parantheses
            return False
        # clip points, check clip again recursively 
        # bitwise comparisons with constants Left/Right/Bottom/Up (1,2,4,8) declared above
        newX = newY = 0
# (newY - y0) / (y1 - y0) = (newX - x0) / (x1 - x0)
        x0 = float(self.point1.x)
        x1 = float(self.point2.x)
        y0 = float(self.point1.y)
        y1 = float(self.point2.y)
        dY = y1 - y0
        dX = x1 - x0
        if lineOr & UP:
            newX = x0 + dX * ((float(WT) - y0) / dY)
            newY = WT
        elif lineOr & BOTTOM:
            newX = x0 + dX * ((float(WB) - y0) / dY)
            newY = WB
        elif lineOr & RIGHT:
            newY = y0 + dY * ((float(WR) - x0) / dX)
            newX = WR
        else:
            newY = y0 + dY * ((float(WL) - x0) / dX)
            newX = WL
        if lineOr == pnt1Code:
            self.point1.x = float(newX)
            self.point1.y = float(newY)
        else:
            self.point2.x = float(newX)
            self.point2.y = float(newY)
        return self.Clip(opts)

# This is the DDA algorithm
    def pixelsToDraw(self,opts): # the opts contains viewport size/location
        if self.Clip(opts) is False:
            return []
        self.ViewTransform(opts)
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
                X = int(pnt1.x)
                Y = int(pnt1.y)
                Points.append(Point(int(round(X)),int(round(Y))))
                while int(X) != int(pnt2.x):
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
                X = int(pnt1.x)
                Y = int(round(pnt1.y))
                Points.append(Point(int(round(X)),int(round(Y))))
                tar = int(round(pnt2.y)) - 1
                while Y != int(round(pnt2.y)):
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
                X = int(pnt1.x)
                Y = float(pnt1.y)
                Points.append(Point(int(round(X)),int(round(Y))))
                while X != int(round(pnt2.x)):
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
            while int(Y) != int(self.point2.y):
                Y = Y + flip
                Points.append(Point(int(round(X)),int(round(Y))))

        pixels = [] # clipping will have to happen at some point... but not right now
#for p in Points:
#            pixels.append(CoordToRow(p.x,p.y,int(opts.xhigh) - int(opts.xlow)))
        return Points
