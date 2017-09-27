import sys
import numpy as np
import math
from vectors import *

#hey look, globals... :/
commandTypes = ["Line","moveto","lineto","stroke"]
cursorPosition = Point(0,0)
currentPolygon = []

def resetCursor():
    cursorPosition = Point(0,0)
# returns a lit of post script line commands based on the strings in the ps file
# if it returns none, that means it's part of a polygon.  Otherwise a list of lines to be drawn will be returned
def GetPSCommand(cmdString,someopts):
    global currentPolygon
    global cursorPosition
    cmdArgs = cmdString.split()
    commandName = cmdArgs[-1]
    r = float(someopts.rotation)
    xt = float(someopts.xtranslation)
    yt = float(someopts.ytranslation)
    s = float(someopts.scale)
    if commandName not in commandTypes:
        print "PS command not supported: " + cmdString
        print "Commands currently implemented:" 
        print commandTypes
        sys.exit()
    if commandName == "Line":
        firstPointX = int(cmdArgs[0])
        firstPointY = int(cmdArgs[1])
        secondPointX = int(cmdArgs[2])
        secondPointY = int(cmdArgs[3])
        lc = LineCommand(Point(firstPointX,firstPointY),Point(secondPointX,secondPointY))
        lc.Rotate(r)
        lc.Translate(xt,yt)
        lc.Scale(s,s)
        return [lc]
    elif commandName == "lineto":
        cursorPosition.x = int(cmdArgs[0])
        cursorPosition.y = int(cmdArgs[1])
        currentPolygon.append(PointAtCursor(r,xt,yt,s))
        return None
    elif commandName == "moveto":
        cursorPosition.x = int(cmdArgs[0])
        cursorPosition.y = int(cmdArgs[1])
        currentPolygon.append(PointAtCursor(r,xt,yt,s))
        return None
    elif commandName == "stroke":
        if len(currentPolygon) < 2:
            print "INVALID VERTS TO MAKE POLYGON"
            sys.exit()
        return ClipCurrentPolygon(someopts)

def PointAtCursor(r,xt,yt,s):
    p = Point(cursorPosition.x,cursorPosition.y)
    p.Rotate(r)
    p.Translate(xt,yt)
    p.Scale(s,s)
    return p

def ClipCurrentPolygon(someopts):
    def Inside(p,edge):
        if edge[2] == "r":
            return p.x <= edge[0].x# and p.y < edge[0].y and p.y > edge[1].y
        if edge[2] == "b":
            return p.y >= edge[0].y# and p.x < edge[0].x and p.x > edge[1].x
        if edge[2] == "l":
            return p.x >= edge[0].x# and p.y > edge[0].y and p.y < edge[1].y
        if edge[2] == "t":
            return p.y <= edge[0].y# and p.x > edge[0].x and p.x < edge[1].x
# intersection algebra with help from the wikipedia page: http://rosettacode.org/wiki/Sutherland-Hodgman_polygon_clipping#Python
# comments explaining implementation are my own
    def ComputeIntersection(p1,p2,edge,right="t"):
        minus = 0
        if right == "r": # was having some problems with clipping on the right viewport being off by a pixel... the line was clipped but was 1 pixel out of the view
            minus = 1
        p3 = edge[0]
        p4 = edge[1]
        x1y2 = p1.x * p2.y
        y1x2 = p1.y * p2.x
        x3y4 = p3.x * p4.y
        y3x4 = p3.y * p4.x
        detXTop = (x1y2 - y1x2) * (p3.x - p4.x) - (p1.x - p2.x) * (x3y4 - y3x4)
        detYTop = (x1y2 - y1x2) * (p3.y - p4.y) - (p1.y - p2.y) * (x3y4 - y3x4)
        detBot = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        return Point(int(float(detXTop)/float(detBot)) - minus,float(detYTop)/float(detBot))
    global currentPolygon
    WT = int(someopts.yhigh) 
    WB = int(someopts.ylow)
    WL = int(someopts.xlow)
    WR = int(someopts.xhigh)
    clippingEdges = []
    clippingEdges.append([Point(WR,WT),Point(WR,WB),"r"]) # top right, bot right
    clippingEdges.append([Point(WR,WB),Point(WL,WB),"b"]) # bot right, bot left
    clippingEdges.append([Point(WL,WB),Point(WL,WT),"l"]) # bot left, top left
    clippingEdges.append([Point(WL,WT),Point(WR,WT),"t"]) # top left, top right
    vertList = currentPolygon
    # sutherland hodgman
    for edge in clippingEdges:
        inputList = list(vertList) # copy it...
        vertList = [] # replace polygon points with null list, going to become a list of lines
        s = inputList[-1]
        for E in inputList:
            if Inside(E,edge) == True:
                if Inside(s,edge) == False:
                    vertList.append(ComputeIntersection(s,E,edge,edge[2]))
                vertList.append(E)
            elif Inside(s,edge) == True:
                vertList.append(ComputeIntersection(s,E,edge,edge[2]))
            s = E

#lineCommands.append(LineCommand(vertList[0],vertList[-1])) # the very last line!
    lineCommands =[]
    lineCommands.append(LineCommand(vertList[0],vertList[-1]))
#    print str(lineCommands[0].point1) + ":" + str(lineCommands[0].point2)
    for i in range(len(vertList) - 1):
        lineCommands.append(LineCommand(vertList[i],vertList[i+1]))
# uncomment line below to debug which lines are being drawn in poly
    for lc in lineCommands:
            print str(lc.point1) + ":" + str(lc.point2)
    currentPolygon = []
    return lineCommands


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
        WT = int(opts.yhigh) 
        WB = int(opts.ylow)
        WL = int(opts.xlow)
        WR = int(opts.xhigh)
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
            self.point1.x = int(newX)
            self.point1.y = int(newY)
        else:
            self.point2.x = int(newX)
            self.point2.y = int(newY)
        return self.Clip(opts)

# This is the DDA algorithm
    def pixelsToDraw(self,opts): # the opts contains viewport size/location
        if self.Clip(opts) is False:
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
                X = int(pnt1.x)
                Y = int(pnt1.y)
                Points.append(Point(int(round(X)),int(round(Y))))
                while int(X) != int(pnt2.x) - 1:
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
            while int(Y) != int(self.point2.y):
                Y = Y + flip
                Points.append(Point(int(round(X)),int(round(Y))))

        pixels = [] # clipping will have to happen at some point... but not right now
#for p in Points:
#            pixels.append(CoordToRow(p.x,p.y,int(opts.xhigh) - int(opts.xlow)))
        return Points
