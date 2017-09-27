import math
import numpy as np

class Point:
    def __init__(self, xPos, yPos, zPos = 1):
# some opts changes the point to have an origin in the top left (from the bottom right)
# this is used to make the top left of the image the origin for XPM, as opposed to the bottom left in PS
        self.x = float(xPos)
        self.y = float(yPos)
        self.z = 1.0
    def OriginToTopLeft(self,someopts):
        self.y = float(someopts.yhigh) - float(someopts.ylow) - self.y
    def Transform(self,matrix):
        print matrix
    def Translate(self,xoffset,yoffset,zoffset = 0):
# subtract difference of world origin (ylow/xlow)
        self.x += float(xoffset)
        self.y += float(yoffset)
        self.z += float(zoffset)
    def Scale(self,sx,sy,sz=1):
        self.x = int(float(sx) * float(self.x))
        self.y = int(float(sy) * float(self.y))
        self.z = int(float(sz) * float(self.z))
    def Rotate(self,degrees):
        degrees = math.radians(degrees)
        newX = self.x * math.cos(degrees) - self.y * math.sin(degrees)
        newY = self.x * math.sin(degrees) + self.y * math.cos(degrees)
        self.x = newX
        self.y = newY
    def __str__(self):
        return "{X}/{Y}/{Z}".format(X=self.x,Y=self.y,Z=self.z)

class Vector:
    def __init__(self):
        self.points = []
    def add(self,point):
        self.points.append(point)

 # converts a given coordinate X/Y on a grid with width 'width' into its row     major index
# this assumes the grid can be laid out in row major order...
def CoordToRow(x,y,width,offset=0):
    val = y * width + x
    return val - offset

def RowToPoint(index,width):
    x = index // width # integer division
    y = index % width
    return Point(x,y)
