#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - data format class                                          *
#*                                                                         *
#*   Copyright                                                             *
#*   (C) 2011 Ignacio Serantes <kde@aynoa.net>                             *
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

import datetime, os, re

from PyQt4.QtCore import *
from PyKDE4.nepomuk import *
from PyKDE4.soprano import *

from clsparql import *
from lfunctions import *

#BEGIN cldataformat.py

class cDataFormat():

    outFormat = 1  # 1- Text, 2- Html
    

    def formatAsText(self, data = [], structure = [], queryTime = 0, stdout = False):
        text = ''
        numColumns = len(structure)
        for row in data:
            value = ""
            uri = ""
            for i in range(0, numColumns):
                column = row[i]
                if column == '':
                    pass

                elif column[:9] == 'nepomuk:/':
                    uri = column

                else:
                    if value != "":
                        value += ', '
                        
                    value += column

            if uri != "":
                try:
                    nepomukResource = Nepomuk.Resource(uri)
                    altLabel = nepomukResource.property(NOC('nao:altLabel')).toString()
                    fullName = nepomukResource.property(NOC('nco:fullname')).toString()
                    identifier = nepomukResource.property(NOC('nao:identifier')).toString()
                    itemType = toUnicode(nepomukResource.resourceType().toString().split('#')[1])
                    prefLabel = nepomukResource.property(NOC('nao:prefLabel')).toString()
                    title = nepomukResource.property(NOC('nie:title')).toString()
                    url = nepomukResource.property(NOC('nie:url')).toString()
                    fullTitle = "%s  %s  %s  %s" % (fullName, title, prefLabel, altLabel)
                    fullTitle = fullTitle.strip().replace("  ", " - ")
                    line = "%s, %s, %s" % (url, fullTitle, itemType)
                    line = line.replace(", , ", ", ")
                    if line[:2] == ", ":
                        line = line[2:]

                except:
                    line = value

                if line == "":
                    line = "No data available"

            if line != '':
                print toUtf8(line)
                #text += line + '\n'

        return ""
        

    def formatAsHtml(self, data = [], structure = [], queryTime = 0, stdout = False):
        htmlQueryTime = time.time()
        
        text = ''
        text += '<html><head><title>Resouces available</title></head>\n' \
                    "<body>\n"
        text += "<table style=\"text-align:left; width: 100%;\" " \
                        "border=\"1\" cellpadding=\"2\" cellspacing=\"0\">" \
                    "<tbody>\n"

        numColumns = len(structure)
        for row in data:
            line = ""
            value = ""
            uri = ""
            for i in range(0, numColumns):
                column = row[i]
                if column == '':
                    pass

                elif column[:9] == 'nepomuk:/':
                    uri = column

                else:
                    if value != "":
                        value += ', '

                    value += column

            if uri != "":
                try:
                #if True:
                    nepomukResource = Nepomuk.Resource(uri)
                    altLabel = nepomukResource.property(NOC('nao:altLabel')).toString()
                    fullName = nepomukResource.property(NOC('nco:fullname')).toString()
                    identifier = nepomukResource.property(NOC('nao:identifier')).toString()
                    itemType = toUnicode(nepomukResource.resourceType().toString().split('#')[1])
                    prefLabel = nepomukResource.property(NOC('nao:prefLabel')).toString()
                    title = nepomukResource.property(NOC('nie:title')).toString()
                    url = nepomukResource.property(NOC('nie:url')).toString()
                    fullTitle = "%s  %s  %s  %s" % (fullName, title, prefLabel, altLabel)
                    fullTitle = fullTitle.strip().replace("  ", " - ")
                    if fullTitle == "":
                        fullTitle = identifier

                    if url == "" and fullTitle == "" and itemType == "":
                        line = ""
                        
                    else:
                        line = "<tr><td>%s</td><td>%s</td><td width=\"15px\">%s</td></tr>\n" % (url, fullTitle, itemType)

                except:
                #else:
                    line = "<tr><td>%s</td><td></td><td width=\"15px\"></td></tr>\n" % value

                if line == "":
                    line = "<tr><td>%s</td><td></td><td width=\"15px\"></td></tr>\n" % "No data available"

            if line != '':
                text += line + '\n'

        text += "</tbody></table>\n"
        text += "<br />\n%(records)s records found in %(seconds)f seconds." \
                    "&nbsp;HTML visualization builded in %(sechtml)s seconds." \
                    % {'records': len(data), 'seconds': queryTime, 'sechtml': time.time() - htmlQueryTime}
        text += "<br />--<br /><b>Powered by</b> <em>%(name)s</em> <b>%(version)s</b> released (%(date)s)" \
                        % {'name': "nepoogle", \
                            'version': "0.7git", \
                            'date': "2011-11-xx" \
                            }
        text += "</body>\n" \
                "</html>"

        return text
    
    
    def formatData(self, data = [], structure = [], queryTime = 0, stdout = False):
        if self.outFormat == 1:
            return self.formatAsText(data = [], structure = [], queryTime = 0, stdout = False)

        elif self.outFormat == 2:
            return self.formatAsHtml(data = [], structure = [], queryTime = 0, stdout = False)

        else:
            return ""
        
        
#END cldataformat.py
