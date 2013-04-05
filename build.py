#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - build script.                                              *
#*                                                                         *
#*   Copyright (C) 2011-13 Ignacio Serantes <kde@aynoa.net>                *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, write to the                         *
#*   Free Software Foundation, Inc.,                                       *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.         *
#***************************************************************************

import os, stat, sys

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
            if (line.strip() == "#IF BUILD"):
                currExp = "IF"
                continue

            elif (line.strip() == "#ELSE"):
                currExp = "ELSE"
                continue

            elif (line.strip() == "#ENDIF"):
                currExp = ""
                continue

            if (currExp == "ELSE"):
                pass

            else:
                if (line.strip()[:9] == "#INCLUDE "):
                    addFileName = line.strip()[9:].strip()
                    addFile(outFile, addFileName)
                    print(" +++ \"%s\" file added." % addFileName)

                else:
                    outFile.write(line)

    except:
        raise

    finally:
        inFile.close()
        outFile.close()

    try:
        fd = os.open(outFileName, os.O_RDONLY )

        try:
            # Change permissions.
            os.fchmod(fd, stat.S_IREAD + stat.S_IWRITE + stat.S_IEXEC + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH)

        finally:
            os.close(fd)

    except:
        raise


inFileName = outFileName = None
try:
    inFileName = sys.argv[1]
    outFileName = sys.argv[2]

except:
    pass

print "Script builder v0.2\n"

if (outFileName == None):
    print("usage: build.py nepoogle nepoogle.py")

else:
    if not os.path.exists(inFileName):
        print("ERROR: \"%s\" file don\'t exists." % (inFileName))

    else:
        if (inFileName == outFileName):
            print("ERROR: input and output file can't be the same.")

        elif os.path.exists(outFileName):
            print("ERROR: \"%s\" file exists, delete before proceeding." % (outFileName))

        else:
            build(inFileName, outFileName)
            print(" >>> \"%s\" file has been built." % outFileName)

print("")