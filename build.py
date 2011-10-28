#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

def addFile(outFile, fileName):
    if not os.path.exists(fileName):
        raise Exception("ERROR: \"%s\" file don\'t exists." % fileName)

    f = open(fileName, 'r')

    copyLine = False
    beginTag = "#BEGIN %s" % fileName
    endTag = "#END %s" % fileName

    try:
        lines = f.readlines()
        for line in lines:
            if line.strip() == beginTag:
                copyLine = True

            elif line.strip() == endTag:
                copyLine = False

            elif copyLine:
                outFile.write(line)

    finally:
        f.close()


def build(inFileName = '', outFileName = ''):

    inFile = open(inFileName, 'r')
    outFile = open(outFileName, 'w')

    currExp = ""
    try:
        lines = inFile.readlines()
        for line in lines:
            if line.strip() == "#IF BUILD":
                currExp = "IF"
                continue

            elif line.strip() == "#ELSE":
                currExp = "ELSE"
                continue
                
            elif line.strip() == "#ENDIF":
                currExp = ""
                continue

            if currExp == "ELSE":
                pass

            else:
                if line.strip()[:9] == "#INCLUDE ":
                    addFileName = line.strip()[9:].strip()
                    addFile(outFile, addFileName)
                    print " +++ \"%s\" file added." % addFileName

                else:
                    outFile.write(line)

    except:
        raise
    
    finally:
        inFile.close()
        outFile.close()

    
inFileName = sys.argv[1]
outFileName = sys.argv[2]

print "Script builder v0.1"

if not os.path.exists(inFileName):
    print "ERROR: \"%s\" file don\'t exists." % (inFileName)

else:
    if os.path.exists(outFileName):
        print "ERROR: \"%s\" file exists, delete before proceeding." % (outFileName)

    else:
        build(inFileName, outFileName)
        print " >>> \"%s\" file has been builded." % outFileName
