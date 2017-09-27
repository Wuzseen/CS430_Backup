#ifndef LINECMD_H
#define LINECMD_H

#include <iostream>
#include <stdio.h>
#include "Commands.h"


class LineCommand : public Command {
    public:
        void Print() {
            printf("Hello, line command here.\n");
        }
        
        LineCommand() {
            printf("Line command created.\n");
        }
};

#endif
