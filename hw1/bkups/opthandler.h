#ifndef opthandler
#define opthandler

#include <stdio.h>
#include <string>

#define PS_DEF "hw1.ps"
#define SCALE_DEF 1.0
#define ROT_DEF 0
#define XT_DEF 0
#define YT_DEF 0
#define XLOW_DEF 0
#define YLOW_DEF 0
#define XHI_DEF 499
#define YHI_DEF 499

using namespace std;

struct Opthandler{
    string psFile;
    float scale;
    int rotation;
    int xTranslation;
    int yTranslation;
    int xLowerBound;
    int yLowerBound;
    int xUpperBound;
    int yUpperBound;
};

struct Opthandler LoadDefaults() {
    struct Opthandler opts;
    opts.psFile = PS_DEF;
    opts.scale = SCALE_DEF;
    opts.rotation = ROT_DEF;
    opts.xTranslation = XT_DEF;
    opts.yTranslation = YT_DEF;
    opts.xLowerBound = XLOW_DEF;
    opts.yLowerBound = YLOW_DEF;
    opts.xUpperBound = XHI_DEF;
    opts.yUpperBound = YHI_DEF;
    return opts;
}

void PrintOpts(struct Opthandler opts) {
   printf("PSFile: %s\n"
           "Scale: %.2f\n"
           "Rotation: %d\n"
           "(XTran,YTran): (%d,%d)\n"
           "(XLowerBound,XUpperBound): (%d,%d)\n"
           "(YLowerBound,YUpperBound): (%d,%d)\n",
            opts.psFile.c_str(),opts.scale,opts.rotation,opts.xTranslation,opts.yTranslation,opts.xLowerBound,opts.xUpperBound,opts.yLowerBound,opts.yUpperBound);
}

#endif
