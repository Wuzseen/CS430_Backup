#ifndef CMD_H
#define CMD_H

#include <iostream>
#include <stdio.h>

class Command {
    public:
        virtual void Print() = 0;
        Command() {
            printf("Command created.\n");
        }
        virtual ~Command();
};

#endif
