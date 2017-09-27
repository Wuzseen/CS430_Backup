from vectors import *

class XPMColor:
    def __init__(self,symbol,value):
        self.symbol = symbol
        self.value = value
    def __str__(self):
        return "\"" + self.symbol + " c " + self.value + "\"," 

def CreatePixels(someopts,commands):
    def Shade(z,front):
        ret = (z - -1) / (front - -1) * (19 - 0) + 0
#print(int(lScale * r))
        return 20 - int(ret)
    height = int(someopts.yviewhigh) - int(someopts.yviewlow) 
    width = int(someopts.xviewhigh) - int(someopts.xviewlow)
    pixels = [[0 for x in xrange(501)] for x in xrange(501)]
    zBuff = [[-1 for x in xrange(501)] for x in xrange(501)]
    pixelsToDrawBlack = []
    if someopts.parallel:
        FRONT = 0
    else:
        FRONT =  (someopts.zprp - someopts.F) / (someopts.B - someopts.zprp)
    for c in commands:
        polyPixels = c[0].pixelsToDraw(someopts)
        for p in polyPixels:
            xIndex = int(p.x) #- int(someopts.xlow)
            yIndex = int(p.y) #- int(someopts.ylow)
            pz = p.z
            if xIndex < len(pixels) and yIndex < len(pixels[0]):
                Z = zBuff[xIndex][yIndex]
                if pz < FRONT and pz > Z:
                    pixels[xIndex][yIndex] = 1 + 20 * (c[1] - 1) + Shade(pz,FRONT)  # cue index (1 is for the bg index): 1 + (index - 1) * 20 + shade
                    zBuff[xIndex][yIndex] = pz
#    t = (z + 1.0) / (front + 1.0)
#pixelsToDrawBlack.extend(c[0].pixelsToDraw(someopts))

#    for p in pixelsToDrawBlack: # pixels to draw black are points in world space
#        xIndex = int(p.x) #- int(someopts.xlow)
#        yIndex = int(p.y) #- int(someopts.ylow)
#        if xIndex < len(pixels) and yIndex < len(pixels[0]):
#            pixels[xIndex][yIndex] = 1
#pixels[int(p.x) - int(someopts.xlow)][int(p.y) - int(someopts.ylow)] = 1
    return pixels

def ColorGen():
    colors = []
    colors.append(XPMColor("---","#000000")) # black
    t = 1.0
    hexArr = []
    while t >= 0.0:
        intRep = int(255.0 * t)
        hexArr.append("%02x" % intRep)
        t -= 0.05 # 20 shades, .05 = 1/20
    for i in range(20):
        colors.append(XPMColor("r%02d" % i,"#%s0000" % hexArr[i]))
    for i in range(20):
        colors.append(XPMColor("g%02d" % i,"#00%s00" % hexArr[i]))
    for i in range(20):
        colors.append(XPMColor("b%02d" % i,"#0000%s" % hexArr[i]))
    return colors



def CreateXPM(someopts,commands):
    height = 501
    width = 501
    filehead = "/* XPM */\nstatic char *xpmOut[] = {\n/* width height num_colors chars_per_pixel */\n"
    print filehead
    colors = ColorGen()
    dimensionLine = "\"%d %d %d 3\",\n" % (width,height,len(colors)) # two clors for black & white, 500 is to force canvas size
    print dimensionLine
    print "/* colors */"
    for c in colors:
        print c
    print ''
    pixels = CreatePixels(someopts,commands)
    for i in range(height,-1,-1): # change y origin....
        line = []
        beginScan = False
        lastC = "-"
        for z in range(width):
            try:
                pixel = pixels[z][i]
                c = str(colors[pixel].symbol)
            except IndexError:
                c = "-"
            line.append(c)
            lastC = c
        for z in range(0, 501 - len(line)):
            line.append("-") # force it to 500 x 500
        print "\"" + "".join(line) + "\"",
        if i != height - 1:
            print ","
    print '\n'
    fileclose = "};"
    print fileclose
