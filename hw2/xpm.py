from vectors import *

class XPMColor:
    def __init__(self,symbol,value):
        self.symbol = symbol
        self.value = value
    def __str__(self):
        return "\"" + self.symbol + " c " + self.value + "\"," 

def CreatePixels(someopts,commands):
    height = int(someopts.yhigh) - int(someopts.ylow) 
    width = int(someopts.xhigh) - int(someopts.xlow)
# 2d buffer
    pixels = [[0 for x in xrange(height + 1)] for x in xrange(width + 1)] # 0 based so add 1
    pixelsToDrawBlack = []
    for c in commands:
        # apply any translations to the command
#        c.Rotate(float(someopts.rotation))
#        c.Translate(float(someopts.xtranslation),float(someopts.ytranslation))
#        c.Scale(float(someopts.scale),float(someopts.scale)) # x and y are explicit and z defaults to 1... could add scaling in specific axes later
        pixelsToDrawBlack.extend(c.pixelsToDraw(someopts))
    sX = int(someopts.xlow)
    sY = int(someopts.yhigh) - int(someopts.ylow)
    wX = 0 # the world origin is 0,0 but the screen might not be!
    wY = 0

    for p in pixelsToDrawBlack: # pixels to draw black are points in world space
        xIndex = int(p.x) - int(someopts.xlow)
        yIndex = int(p.y) - int(someopts.ylow)
        if xIndex < len(pixels) and yIndex < len(pixels[0]):
            pixels[int(p.x) - int(someopts.xlow)][int(p.y) - int(someopts.ylow)] = 1
    return pixels

def CreateXPM(someopts,commands):
    height = int(someopts.yhigh) - int(someopts.ylow)
    width = int(someopts.xhigh) - int(someopts.xlow)
    filehead = "/* XPM */\nstatic char *xpmOut[] = {\n/* width height num_colors chars_per_pixel */\n"
    print filehead
    dimensionLine = "\"%d %d 2 1\",\n" % (width,height) # two clors for black & white
    print dimensionLine
    print "/* colors */"
    colors = []
    colors.append(XPMColor("-","#ffffff")) # white
    colors.append(XPMColor("X","#000000")) # black
    for c in colors:
        print c
    print ''
    pixels = CreatePixels(someopts,commands)
    for i in range(height,-1,-1): # change y origin....
        line = []
        for z in range(width):
            pixel = pixels[z][i]
            line.append(str(colors[pixel].symbol))
        print "\"" + "".join(line) + "\"",
        if i != height - 1:
            print ","
    print '\n'
    fileclose = "};"
    print fileclose
