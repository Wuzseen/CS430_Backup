import math
import numpy as np

def TVRPar(opts):
    dx = opts.xvrp
    dy = opts.yvrp
    dz = opts.zvrp
    multiMatrix = np.matrix([[1,0,0,-dx],[0,1,0,-dy],[0,0,1,-dz],[0,0,0,1]])
    return multiMatrix

def RPar(opts):
    Rz = Point(opts.xvpn,opts.yvpn,opts.zvpn).Normalize()
    VUP = Point(opts.xvup,opts.yvup,opts.zvup)
    Cross = VUP.Cross(Rz)
    Rx = Cross.Normalize()
    Ry = Rz.Cross(Rx)
    multiMatrix = np.matrix([[Rx.x,Rx.y,Rx.z,0],[Ry.x,Ry.y,Ry.z,0],[Rz.x,Rz.y,Rz.z,0],[0,0,0,1]])
    return multiMatrix

def SHPar(opts):
    PRP = Point(opts.xprp,opts.yprp,opts.zprp)
    CWx = (opts.umax + opts.umin) / 2
    CWy = (opts.vmax + opts.vmin) / 2
    CW = Point(CWx,CWy,0)
    DOP = CW.Subtract(PRP)
#shx = -1 * DOP.x / DOP.z
#    shy = -1 * DOP.y / DOP.z
    shx = (.5 * (opts.umax + opts.umin) - PRP.x) / PRP.z
    shy = (.5 * (opts.vmax + opts.vmin) - PRP.y) / PRP.z
    multiMatrix = np.matrix([[1,0,shx,0],[0,1,shy,0],[0,0,1,0],[0,0,0,1]])
    return multiMatrix
    
def TPar(opts):
    p1 = -1 * (opts.umax + opts.umin) / 2
    p2 = -1 * (opts.vmax + opts.vmin) / 2
    p3 = -1 * opts.F
    multiMatrix = np.matrix([[1,0,0,p1],[0,1,0,p2],[0,0,1,p3],[0,0,0,1]])
    return multiMatrix
   
def SPar(opts):
    p1 = 2 /(opts.umax - opts.umin)
    p2 = 2 /(opts.vmax - opts.vmin)
    p3 = 1 / (opts.F - opts.B)
    multiMatrix = np.matrix([[p1,0,0,0],[0,p2,0,0],[0,0,p3,0],[0,0,0,1]])
    return multiMatrix

def SPer(opts):
    vrpnew = -opts.zprp
    p3 = -1 / (vrpnew + opts.B)
    p1 = (-2 * vrpnew) / (opts.umax - opts.umin) * p3
    p2 = (-2 * vrpnew) / (opts.vmax - opts.umin) * p3
    multiMatrix = np.matrix([[p1,0,0,0],[0,p2,0,0],[0,0,p3,0],[0,0,0,1]])
    return multiMatrix
    
#PRP translate for pesrpective
def TPRPPer(opts):
    dx = opts.xprp
    dy = opts.yprp
    dz = opts.zprp
    multiMatrix = np.matrix([[1,0,0,-dx],[0,1,0,-dy],[0,0,1,-dz],[0,0,0,1]])
    return multiMatrix
    

def ParallelTranslationMatrix(opts):
    return np.dot(SPar(opts),np.dot(TPar(opts),np.dot(SHPar(opts),np.dot(RPar(opts),TVRPar(opts)))))

def PerspectiveTranslationMatrix(opts):
    return np.dot(SPer(opts),np.dot(SHPar(opts),np.dot(TPRPPer(opts),np.dot(RPar(opts),TVRPar(opts)))))

class Point:
    def __init__(self, xPos, yPos, zPos = 1):
# some opts changes the point to have an origin in the top left (from the bottom right)
# this is used to make the top left of the image the origin for XPM, as opposed to the bottom left in PS
        self.x = float(xPos)
        self.y = float(yPos)
        self.z = float(zPos)
    def Cross(self,o):
        x = self.y * o.z - self.z *o.y
        y = self.z * o.x - self.x * o.z
        z = self.x * o.y - self.y * o.x
        return Point(x,y,z)
    def PointScale(self,s):
        return Point(self.x * s, self.y * s, self.z * s)
    def Length(self):
        return ((self.x * self.x) + (self.y * self.y) + (self.z * self.z)) ** 0.5
    def Normalize(self):
        mag = self.Length()
        x = self.x / mag
        y = self.y / mag
        z = self.z / mag
        return Point(x,y,z)
    def OriginToTopLeft(self,someopts):
        self.y = float(someopts.yhigh) - float(someopts.ylow) - self.y
    def Subtract(self,o):
        return Point(self.x - o.x, self.y - o.y, self.z - o.z)
    def Translate(self,xoffset,yoffset,zoffset = 0):
# subtract difference of world origin (ylow/xlow)
        self.x += float(xoffset)
        self.y += float(yoffset)
        self.z += float(zoffset)
    def Scale(self,sx,sy,sz=1):
        self.x = float(sx) * float(self.x)
        self.y = float(sy) * float(self.y)
        self.z = float(sz) * float(self.z)
    def Rotate(self,degrees):
        degrees = math.radians(degrees)
        newX = self.x * math.cos(degrees) - self.y * math.sin(degrees)
        newY = self.x * math.sin(degrees) + self.y * math.cos(degrees)
        self.x = newX
        self.y = newY
    def Matrix(self):
        m = np.matrix([[self.x],[self.y],[self.z],[1]])
        return m
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
