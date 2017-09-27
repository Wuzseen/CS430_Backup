#include <iostream>
#include <string>
#include <stdio.h>
#include <vector>
#include <stdlib.h>
#include <fstream>
#include <unistd.h>
#include "opthandler.h" // Contains opthandler struct and helper methods
#include "Commands.h"
#include "LineCommand.h"

using namespace std;

void Usage();
vector<Command*> ProcessCommands(struct Opthandler someOpts, vector<Command*>* commands);

int main(int argc, char* argv[]) {
    struct Opthandler opthelper = LoadDefaults(); // default args are overridden by getopt cycle
    int c, errors, argcount;
    errors = 0;
    argcount = 0;
    extern char* optarg;
    extern int optind, optopt;
    // Begin cmd arg parsing, some basic code from Open Group spec for Unix/Posix getopt
    while((c = getopt(argc, argv, ":f:s:r:m:n:a:b:c:d:")) != -1) { // Leading colon suppresses errors from getopt, fascinating.
        argcount++;
        switch(c) {
            case 'f':
                opthelper.psFile = string(optarg);
                break; 
            case 's':
                opthelper.scale = atof(optarg);
                break;
            case 'r':
                opthelper.rotation = atoi(optarg);
                break;
            case 'm':
                opthelper.xTranslation = atoi(optarg);
                break;
            case 'n':
                opthelper.yTranslation = atoi(optarg);
                break;
            case 'a':
                opthelper.xLowerBound = atoi(optarg);
                break;
            case 'b':
                opthelper.yLowerBound = atoi(optarg);
                break;
            case 'c':
                opthelper.xUpperBound = atoi(optarg);
                break;
            case 'd':
                opthelper.yUpperBound = atoi(optarg);
                break;
            case '?':
                fprintf(stderr, "Unrecognized option -%c\n",optopt);
                errors++;
        }
    }

    if(errors > 0) {
        Usage();
        return 0;
    }

    // Vector of pointer to abstract commands
    vector<Command*> commands = vector<Command*>();
    ProcessCommands(opthelper,&commands);

    // Clean up commands...
    for(int i = 0; i < commands.size(); i++) {
        delete commands[i];
    }
    commands.clear();
}

// Reads .ps file, converts into vector of commands.  Delimited by file structure %%%BEGIN and %%%END
vector<Command*> ProcessCommands(struct Opthandler someOpts, vector<Command*>* commands) {
    printf("Processing commands in %s.\n",someOpts.psFile.c_str()); 
    ifstream psFile(someOpts.psFile.c_str()); // Ifstream only uses a char*, not string :(
    string line;

    bool getCommand = false;
    while(getline(psFile, line)) {
        if(line == "%%%BEGIN") {
            printf("CHEESE AND CRACKERS\n");
        }
        printf("%s\n",line.c_str());
    }
}

void Usage() {
    printf("Takes command line opts, each with a required parameter, as specified in the assignment outline. (f,s,r,m,n,a,b,c,d)\n");
}
