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
from PyKDE4.kdeui import *
from PyKDE4.nepomuk import *
from PyKDE4.soprano import *

from clsparql import *
from lfunctions import *

#BEGIN cldataformat.py
# This must be outside class to avoid lost this information creating and releasing objects.
ontologiesInfo = []
    #['nao:created', 'datetime'], \
    #['nao:lastmodified', 'datetime'], \
    #['nao:numericrating', 'number'], \
    #['nfo:averagebitrate', 'number'], \
    #['nfo:duration', 'seconds'], \
    #['nfo:height', 'number'], \
    #['nfo:samplerate', 'number'], \
    #['nfo:width', 'number'], \
    #['nie:contentcreated', 'datetimep'], \
    #['nie:contentsize', 'size'], \
    #['nie:lastmodified', 'datetime'], \
    #['nmm:episodenumber', 'number'], \
    #['nmm:releasedate', 'datep'], \
    #['nmm:season', 'number'], \
    #['nmm:setnumber', 'number'], \
    #['nmm:tracknumber', 'number'], \
    #['nuao:usagecount', 'number'] \

_CONST_ICON_DOLPHIN = 1
_CONST_ICON_KONQUEROR = 2
_CONST_ICON_PROPERTIES = 4
_CONST_ICON_REMOVE = 8
_CONST_ICON_SYSTEM_RUN = 16

# Order is relevant, is display order.
_CONST_ICONS_LIST = (_CONST_ICON_PROPERTIES, _CONST_ICON_REMOVE, \
                        _CONST_ICON_DOLPHIN, _CONST_ICON_KONQUEROR, \
                        _CONST_ICON_SYSTEM_RUN)

class cDataFormat():

    columnCount = 3
    data = []
    model = None
    outFormat = 1  # 1- Text, 2- Html
    queryString = ""
    renderSize = 50
    renderedDataRows = 0
    renderedDataText = ""
    structure = []

    iconDelete = KIconLoader().iconPath('edit-delete', KIconLoader.Small)
    iconDocumentInfo = KIconLoader().iconPath('documentinfo', KIconLoader.Small)
    iconDocumentProp = KIconLoader().iconPath('document-properties', KIconLoader.Small)
    iconFileManager = KIconLoader().iconPath('system-file-manager', KIconLoader.Small)
    iconKonqueror = KIconLoader().iconPath('konqueror', KIconLoader.Small)
    iconNavigateFirst = KIconLoader().iconPath('go-first', KIconLoader.Small)
    iconNavigateLast = KIconLoader().iconPath('go-last', KIconLoader.Small)
    iconNavigateNext = KIconLoader().iconPath('go-next', KIconLoader.Small)
    iconNavigatePrevious = KIconLoader().iconPath('go-previous', KIconLoader.Small)
    iconProcessIdle = KIconLoader().iconPath('process-idle', KIconLoader.Small)
    iconSystemRun = KIconLoader().iconPath('system-run', KIconLoader.Small)
    iconSystemSearch = KIconLoader().iconPath('system-search', KIconLoader.Small)

    htmlPageHeader = "<html>\n" \
                        "<head>\n" \
                        "<title>%(title)s</title>\n" \
                        "<style type=\"text/css\">" \
                        "    body {%(body_style)s}\n" \
                        "    tr {%(tr_style)s}\n" \
                        "    p {%(p_style)s}\n" \
                        "</style>\n" \
                        "</head>\n" \
                        "<body>\n" \
                        % {"title": "%s", \
                            "body_style": "font-size:small;", \
                            "p_style": "font-size:small;", \
                            "tr_style": "font-size:small;" \
                            }
    htmlPageFooter = "</body>\n" \
                        "</html>"

    htmlProgramInfo =  "<br />--<br /><b>Powered by</b> <em>%(name)s</em> <b>%(version)s</b> released (%(date)s)" \
                        % {'name': "nepoogle", \
                            'version': "0.7git", \
                            'date': "2011-11-xx" \
                            }
                            
    htmlTableHeader = "<table style=\"text-align:left; width: 100%;\" " \
                            "border=\"1\" cellpadding=\"1\" cellspacing=\"0\">" \
                        "<tbody>\n"
    htmlTableFooter = "</tbody></table>\n"
    htmlTableColumn1 = "<td>%s</td>"
    htmlTableColumn2 = "<td width=\"40px\">%s</td>"
    htmlTableColumn3 = "<td width=\"65px\">%s</td>"
    htmlTableRow = "<tr>" + htmlTableColumn1 + htmlTableColumn2 + htmlTableColumn3 + "</tr>"

    htmlViewerTableHeader = "<table style=\"text-align:left; width: 100%%;\" " \
                                "border=\"0\" cellpadding=\"3\" cellspacing=\"0\">" \
                                "<tbody>\n"
    htmlViewerTableFooter = "</tbody></table>\n"
    
    htmlStyleIcon = "align=\"center\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 14px; height: 14px;\""
    htmlStyleNavigate  = "align=\"center\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 20px; height: 20px;\""

    htmlStadistics = "%(records)s records found in %(seconds)f seconds." \
                        "&nbsp;HTML visualization builded in %(sechtml)s seconds." \
                        
    htmlLinkDolphin = "<a title=\"Open with Dolphin\" href=\"dolp:/%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconFileManager) \
                        + "</a>"
    htmlLinkInfo = "<a title=\"%(uri)s\" href=\"%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDocumentInfo) \
                        + "</a>"
    htmlLinkKonqueror = "<a title=\"Open with Konqueror\" href=\"konq:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconKonqueror) \
                            + "</a>"
    htmlLinkNavigateFirst = "<a \"Go %(to)s\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "first", "style": htmlStyleNavigate, "icon": iconNavigateFirst}
    htmlLinkNavigateLast = "<a \"Go %(to)s\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "last", "style": htmlStyleNavigate, "icon": iconNavigateLast}
    htmlLinkNavigatePrevious = "<a \"Go %(to)s\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "previous", "style": htmlStyleNavigate, "icon": iconNavigatePrevious}
    htmlLinkNavigateNext = "<a \"Go %(to)s\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "next", "style": htmlStyleNavigate, "icon": iconNavigateNext}
    htmlLinkOpenLocation = "<a title=\"Open location %(uri)s\" href=\"file://%(uri)s\">" \
                                + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconFileManager) \
                                + "</a>"
    htmlLinkProperties = "<a title=\"Properties\" href=\"prop:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDocumentInfo) \
                            + "</a>"
    htmlLinkRemove = "<a title=\"Remove\" href=\"remove:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDelete) \
                            + "</a>"
    htmlLinkSearch = "<a title=\"%(uri)s\" href=\"query:/%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconSystemSearch) \
                        + "</a>"
    htmlLinkSearchRender = "<img align=\"bottom\" border=\"0\" hspace=\"0\" vspace=\"0\" " \
                                "style=\"width: 14px; height: 14px;\" " \
                                " src=\"file://%s\">" % (iconSystemSearch)
    htmlLinkSystemRun = "<a title=\"Open file %(uri)s\" href=\"run:/file://%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconSystemRun) \
                        + "</a>"

    ontologyFormat = [ \
                        ["nmm:MusicAlbum", \
                            "{nie:title|l|s:album}<br />" \
                            "Performers: {SPARQL}SELECT DISTINCT ?uri ?value WHERE { ?r nmm:musicAlbum <%(uri)s> . ?r nmm:performer ?uri . ?uri nco:fullname ?value . } ORDER BY ?value|l|s:performer{/SPARQL}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nmm:MusicPiece", \
                            "{nfo:fileName|l|of|ol}<br />" \
                            "Title: <em>[{nmm:setNumber}x]{nmm:trackNumber} - {nie:title}</em><br />" \
                            "Album: {nmm:musicAlbum->nie:title|l|s:album}<br \>" \
                            "Performer: {SPARQL}SELECT DISTINCT '%(nmm:performer)s' as ?uri ?value WHERE { <%(nmm:performer)s> nco:fullname ?value . } ORDER BY ?value|l|s:performer{/SPARQL}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Audio", \
                            "{nfo:fileName|l|of|ol}[<br />Title: {nie:title}][<br />url: {nie:url}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:FileDataObject", \
                            "{nie:url|l|of|ol}[<br />Title: {nie:title}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Folder", \
                            "{nfo:fileName|l|of|ol}[<br />url: {nie:url}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nfo:RasterImage", \
                            "{nfo:fileName|l|of|ol}[<br />Title: {nie:title}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Video", \
                            "{nfo:fileName|l|of|ol}[<br />Title: {nie:title}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_SYSTEM_RUN], \
                        ["nao:Tag", \
                            "{nao:prefLabel|l|of|ol|s:hasTag}[<br />Other labels: {nao:altLabel}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nco:Contact", \
                            "{nco:fullname|l|s:contact}[<br />Other labels: {nao:altLabel}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nexif:Photo", \
                            "{nfo:fileName|l|of|ol}[<br />Title: {nie:title}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nie:InformationElement", \
                            "{nfo:fileName|l|of|ol}[<br />Other labels: {nao:altLabel}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["rdfs:Resource", \
                            "{nie:url|l|of|ol}[<br />Title: {nie:title}]", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE] \
                    ]


    def __init__(self, searchString = "", model = None):
        self.searchString = searchString
        if model == None:
            self.model = Nepomuk.ResourceManager.instance().mainModel()

        else:
            self.model = model

    
    def ontologyLabel(ontology = '', reverse = False):
        if self.Model == None:
            return "", "", "", ""
            
        i = lindex(ontologiesInfo, ontology, column = 0)

        if i == None:
            # Data tipes
            #SELECT DISTINCT ?range
            #WHERE {
            #    [] rdfs:range ?range . FILTER(REGEX(?range, "^http://www.w3.org/2001/XMLSchema")) .
            #}
            #ORDER BY ?range
            #Result: boolean, date, dateTime, duration, float, int, integer, nonNegativeInteger, string
            #http://www.w3.org/2001XMLSchema#boolean
            #SELECT DISTINCT ?range
            #WHERE {
            #    nao:userVisible rdfs:range ?range .
            #}
            #ORDER BY ?range
            #SELECT DISTINCT *
            #WHERE {
            #    ?r nao:userVisible ?v . FILTER(?v != "false"^^xsd:boolean) .
            #}

            # Must search for ontology.
            query = "SELECT ?label ?range\n" \
                    "WHERE {\n" \
                        "\t%s rdfs:range ?range\n" \
                        "\tOPTIONAL { %s rdfs:label ?label . }\n" \
                    "}" % (ontology, ontology)
            data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
            if data.isValid():
                while data.next():
                    label = toUnicode(data["?label"].toString())
                    rlabel = label
                    ontType = toUnicode(data["?range"].toString())
                    displayType = ontType

        else:
            # Information is available.
            label = ontologiesInfo[i, 0]
            rlabel = ontologiesInfo[i, 1]
            ontType = ontologiesInfo[i, 2]
            displayType = ontologiesInfo[i, 3]

        return label, rlabel, ontType, displayType


    def formatAsText(self, data = [], structure = [], queryTime = 0, stdout = False):
        text = ""
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
                #try:
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

                #except:
                #    line = value

            else:
                for i in range(0, numColumns):
                    if line != "":
                        line += ", "
                        
                    line += "%s" % row[i]

                line += ", Unknown"

            if line != '':
                print toUtf8(line)
                #text += line + '\n'

        return text
        

    def htmlRenderLink(self, id = 'uri', par1 = '', par2 = ''):
        if id == 'uri':
            title = "title=\"%s\"" % par1
            href = "href=\"%s\"" % par1
            value = par2

        elif id == 'album':
            title = "title=\"album:+\'%s\'\"" % par1
            href = "href=\"query:/album:+\'%s\'\"" % par1
            value = self.htmlLinkSearchRender

        elif id == 'contact':
            title = "title=\"contact:+\'%s\'\"" % par1
            href = "href=\"query:/contact:+\'%s\'\"" % par1
            value = self.htmlLinkSearchRender

        elif id == 'navigator':
            return "%s%s%s%s" % (self.htmlLinkNavigateFirst, \
                                    self.htmlLinkNavigatePrevious, \
                                    self.htmlLinkNavigateNext, \
                                    self.htmlLinkNavigateLast)

        elif id == 'ontology':
            title = "title=\"%s:+\'%s\'\"" % (par1, par2)
            href = "href=\"query:/%s:+\'%s\'\"" % (par1, par2)
            value = self.htmlLinkSearchRender

        elif id == 'performer':
            title = "title=\"performer:+\'%s\'\"" % par1
            href = "href=\"query:/performer:+\'%s\'\"" % par1
            value = self.htmlLinkSearchRender

        elif id == 'tag':
            title = "title=\"hasTag:+\'%s\'\"" % par1
            href = "href=\"query:/hasTag:+\'%s\'\"" % par1
            value = self.htmlLinkSearchRender

        # This is an exception.
        elif id == 'unplugged':
            htmlLinkInfo = "<img %s src=\"file://%s\">" % (self.htmlImgStyle, iconDocumentInfo)
            if par1 == '':
                return "<b>[Unplugged<a title=\"uuid:%s\" href=\"prop:/%s\">%s</a>]</b><em>%s</em>" \
                        % (par2[8:].split('/')[0], \
                            par2[8:].split('/')[0], \
                            htmlLinkInfo, \
                            '/' + '/'.join(par2[8:].split('/')[1:]) \
                            )

            else:
                return "<b>[Unplugged<a title=\"uuid:%s\" href=\"prop:/%s\">%s</a>]</b><a title=\"%s\" href=\"%s\"><em>%s</em></a>" \
                        % (par2[8:].split('/')[0], \
                            par2[8:].split('/')[0], \
                            htmlLinkInfo, \
                            par1, \
                            par1, \
                            '/' + '/'.join(par2[8:].split('/')[1:]) \
                            )

        elif id == 'url':
            title = "title=\"%s\"" % par1
            href = "href=\"%s\"" % par1
            value = par2
            #TODO: añadir un icono que indique que es un enlace externo.

        else:
            return ''

        return "<a %s %s>%s</a>" % (title, href, value)


    def readValues(self, resource, valuesName):
        values = []
        if valuesName[:7].lower() == "sparql:":
            # A query.
            #TODO: test malformed queries.
            query = valuesName[7:]
            variables = re.findall('\%\((.*?)\)s', query)
            for var in variables:
                if var == "uri":
                    query = query.replace("%(" + var + ")s", toUnicode(resource.uri()))

                else:
                    query = query.replace("%(" + var + ")s", toUnicode(resource.property(NOC(var)).toString()))
                
            queryResultSet = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
            if queryResultSet.isValid():
                while queryResultSet.next():
                    values += [[toUnicode(queryResultSet["uri"].toString()), \
                                toUnicode(queryResultSet["value"].toString())]]

        else:
            elements = valuesName.split("->")
            if len(elements) > 1:
                # A simple relation.
                uri = toUnicode(resource.property(NOC(elements[0])).toString())
                if uri != "":
                    query = 'SELECT DISTINCT ?value\n' \
                            'WHERE {\n' \
                                '\t<%s> %s ?value .\n' \
                            '}\n' \
                            % (uri, elements[1])
                    queryResultSet = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
                    if queryResultSet.isValid():
                        value = ""
                        while queryResultSet.next():
                            if value != "":
                                value += ", "

                            values += [[uri, toUnicode(queryResultSet["value"].toString())]]

            elif len(elements) == 1:
                # A property.
                if elements[0] == "uri":
                    values += [[toUnicode(resource.uri()), toUnicode(resource.uri())]]

                else:
                    propertyValue = toUnicode(resource.property(NOC(elements[0])).toString())
                    #TODO: Some special formats, this must be improved.
                    if elements[0] == "nmm:trackNumber":
                        if len(propertyValue) < 2:
                            propertyValue = "0" + propertyValue
                        
                    values += [[toUnicode(resource.uri()), propertyValue]]

            #else:
                #values = []

        return values
        

    def processFormatPattern(self, pattern):
        pattern = toUnicode(pattern)
        data = pattern
        
        variablesTmp = re.findall('\{(.*?)\}', pattern)
        sparqlItems = re.findall('\{SPARQL\}(.*?)\{/SPARQL\}', pattern)
        variables = []
        foundSparql = False
        i = 0
        for var in variablesTmp:
            if var == "SPARQL":
                foundSparql = True
                if i < len(sparqlItems):
                    variables += ["SPARQL:" + sparqlItems[i]]
                    i += 1

            elif foundSparql:
                if var == "/SPARQL":
                    foundSparql = False

            else:
                variables += [var]

        optionals = re.findall('\[(.*?)\]', pattern)
        optionalsEmpty = list(optionals)

        return data, variables, optionals, optionalsEmpty

        
    def formatResource(self, resource, itemType, pattern):
        # Variables substitution.
        data, variables, optionals, optionalsEmpty = self.processFormatPattern(pattern)
        for variable in variables:
            variable = toUnicode(variable)
            elements = variable.split("|")
            addLink = addOpenFile = addOpenLocation = addSearch = False
            for item in elements:
                if item == "l":
                    addLink = True

                elif item == "of":
                    addOpenFile = True
                    
                elif item == "ol":
                    addOpenLocation = True

                elif item == "s" or item[:2] == "s:":
                    addSearch = True
                    searchTerm = item.split(":")
                    if len(searchTerm) > 1:
                        searchTerm = searchTerm[1]

                    else:
                        searchTerm = elements[0]

                else:
                    values = self.readValues(resource, item)

            formatValue = ""
            for value in values:
                if formatValue != "":
                    formatValue += ", "

                if len(value) == 1:
                    displayValue += [""]
                    
                if addLink:
                    if value[1] == "":
                        displayValue = value[0]
                        
                    else:
                        displayValue = value[1]
                        
                    formatValue += "<a title=\"%s\" href=\"%s\">%s</a>" % (value[0], value[0], displayValue)

                else:
                    formatValue += value[1]

                if addSearch:
                    formatValue += " " + self.htmlLinkSearch % {"uri": "%s:+'%s'" % (searchTerm, value[1])}

                if addOpenFile:
                    valuesTmp = self.readValues(resource, 'nie:url')
                    if valuesTmp != [] and valuesTmp[0] != [] and valuesTmp[0][1] != "":
                        formatValue += " " + self.htmlLinkSystemRun % {"uri": valuesTmp[0][1]}

                if addOpenLocation:
                    valuesTmp = self.readValues(resource, 'nie:url')
                    if valuesTmp != [] and valuesTmp[0] != [] and valuesTmp[0][1] != "":
                        url = os.path.dirname(valuesTmp[0][1])
                        formatValue += " " + self.htmlLinkOpenLocation % {"uri": url}

            if variable[:7].lower() == "sparql:":
                data = data.replace("{SPARQL}" + variable[7:] + "{/SPARQL}", formatValue)

            else:
                data = data.replace("{" + variable + "}", formatValue)

            for i in range(0, len(optionalsEmpty)):
                optionals[i] = optionals[i].replace("{" + variable + "}", formatValue)
                optionalsEmpty[i] = optionalsEmpty[i].replace("{" + variable + "}", "")

        # Empty optionals are eliminated.
        for i in range(0, len(optionalsEmpty)):
            data = data.replace("[" + optionalsEmpty[i] + "]", "")

        # Remove brackets from not empty optionals.
        for i in range(0, len(optionals)):
            data = data.replace("[" + optionals[i] + "]", optionals[i])

        return data.strip()
        
        
    def getResourceIcons(self, resource, itemType, iconsAssociated):
        icons = ""
        for i in _CONST_ICONS_LIST:
            if (i & iconsAssociated):
                if (i == _CONST_ICON_DOLPHIN):
                    icons += self.htmlLinkDolphin % {"uri": toUnicode(resource.uri())}

                elif (i == _CONST_ICON_KONQUEROR):
                    icons += self.htmlLinkKonqueror % {"uri": toUnicode(resource.uri())}

                elif (i == _CONST_ICON_PROPERTIES):
                    icons += self.htmlLinkProperties % {"uri": toUnicode(resource.uri())}

                elif (i == _CONST_ICON_REMOVE):
                    icons += self.htmlLinkRemove % {"uri": toUnicode(resource.uri())}

                elif (i == _CONST_ICON_SYSTEM_RUN):
                    icons += self.htmlLinkSystemRun % {"uri": toUnicode(resource.uri())}

            #else:
                #pass

        return icons

    def formatHtmlLine(self, uri):
        nepomukResource = Nepomuk.Resource(uri)
        uri = toUnicode(nepomukResource.uri())
        itemType = NOCR(nepomukResource.resourceType().toString())
        #itemType = toUnicode(nepomukResource.resourceType().toString().split('#')[1])
        
        i = lindex(self.ontologyFormat, itemType, column = 0)
        if (i == None):
            formatPattern = "{uri|l|of}"
            iconsAssociated = _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE

        else:
            formatPattern = self.ontologyFormat[i][1]
            iconsAssociated = self.ontologyFormat[i][2]

        # formatPattern.
        displayInfo = self.formatResource(nepomukResource, itemType, formatPattern)

        if displayInfo == "":
            line = ""

        else:
            # Icons
            icons = self.getResourceIcons(nepomukResource, itemType, iconsAssociated)

            column1 = displayInfo
            column2 = itemType.split(":")[1]
            column3 = icons
            line = self.htmlTableRow % (column1, column2, column3)

        return line


    def formatResourceInfo(self, uri = "", knownShortcuts = [], ontologyValueTypes = [], stdout = False):
        if uri == "":
            return self.renderedDataText

        query = "SELECT DISTINCT ?x ?ont ?val\n" \
                "WHERE {\n" \
                    "\t<" + uri + "> ?ont ?val .\n"\
                "}\n"

        if stdout:
            print toUtf8(query)

        script = ""
        #script = \
        #        "<script type=\"text/javascript\">function getObjectXY(o){var x,y;c=o;if(o.offsetParent){x=y=0;do{x+=o.offsetLeft;if(o.style.borderLeftWidth!='')x+=parseInt(o.style.borderLeftWidth);else o.style.borderLeftWidth='0px';y+=o.offsetTop;if(o.style.borderTopWidth!='')y+=parseInt(o.style.borderTopWidth);else o.style.borderTopWidth='0px';}while(o=o.offsetParent);}return [x-parseInt(c.style.borderLeftWidth),y-parseInt(c.style.borderLeftWidth)];}function retInt(s,f){if(typeof s=='number')return s;var result=s.indexOf(f);return parseInt(s.substring(0,(result!=-1)?result:s.length));}function getMouseXY(e){var x=0,y=0;if(!e)e=window.event;if(e.pageX||e.pageY){x=e.pageX;y=e.pageY;}else if(e.clientX||e.clientY){x=e.clientX+document.body.scrollLeft+document.documentElement.scrollLeft;y=e.clientY+document.body.scrollTop+document.documentElement.scrollTop;}return [x,y];}function mouseWheel(){var s=this;var w=function(e,o,d){};s.wheelHandler=function(e){var d=0;if(!e)e=window.event;if(e.wheelDelta)d=e.wheelDelta/120;else if(e.detail)d=-e.detail/3;if(e.preventDefault)e.preventDefault();e.returnValue=false;if(d)w(e,this,d);};s.init=function(o,c){if(o.addEventListener)o.addEventListener('DOMMouseScroll',this.wheelHandler,false);o.onmousewheel=this.wheelHandler;w=c;};this.setCallback=function(c){w=c;}}function viewer(args){var s=this;s.outerFrame=null;var i=null,imageSource=null,parent=null,replace=null,preLoader=null;var frame=['400px','400px',true];var zoomFactor='10%';var m='300%';i=args['image']?args['image']:null;imageSource=args['imageSource']?args['imageSource']:null;parent=args['parent']?args['parent']:null;replace=args['replace']?args['replace']:null;preLoader=args['preLoader']?args['preLoader']:null;frame=args['frame']?args['frame']:['400px','400px',true];zoomFactor=args['zoomFactor']?args['zoomFactor']:'10%';m=args['maxZoom']?args['maxZoom']:'300%';s.frameElement=s.f=null;var oW,oH,l=0;var lm=null,sp=5;var mo=null;s.getFrameDimension=function(){return [s.f.clientWidth,s.f.clientHeight];};s.setDimension=function(w,h){i.width=Math.round(w);i.height=Math.round(h);};s.getDimension=function(){return [i.width,i.height];};s.setPosition=function(x,y){i.style.left=(Math.round(x)+'px');i.style.top=(Math.round(y)+'px');};s.getPosition=function(){return [retInt(i.style.left,'px'),retInt(i.style.top,'px')];};s.setMouseCursor=function(){var d=s.getDimension();var fd=s.getFrameDimension();var c='crosshair';if(d[0]>fd[0]&&d[1]>fd[1])c='move';else if(d[0]>fd[0])c='e-resize';else if(d[1]>fd[1])c='n-resize';i.style.cursor=c;};s.maxZoomCheck=function(w,h){if(typeof w=='undefined'||typeof h=='undefined'){var t=s.getDimension();w=t[0],h=t[1];}if(typeof m=='number'){return((w/oW)>m||(h/oH)>m);}else if(typeof m=='object'){return(w>m[0]||h>m[1]);}};s.fitToFrame=function(w,h){if(typeof w=='undefined'||typeof h=='undefined'){w=oW,h=oH;}var fd=s.getFrameDimension(),nW,nH;nW=fd[0];nH=Math.round((nW*h)/w);if(nH>(fd[1])){nH=fd[1];nW=Math.round((nH*w)/h);}return [nW,nH];};s.getZoomLevel=function(){return l;};s.zoomTo=function(nl,x,y){var fd=s.getFrameDimension();if(nl<0||x<0||y<0||x>=fd[0]||y>=fd[1])return false;var d=s.fitToFrame(oW,oH);for(var n=nl;n>0;n--)d[0]*=zoomFactor,d[1]*=zoomFactor;var cW=i.width,cH=i.height;var p=s.getPosition();p[0]-=((x-p[0])*((d[0]/cW)-1)),p[1]-=((y-p[1])*((d[1]/cH)-1));p=s.centerImage(d[0],d[1],p[0],p[1]);if(!s.maxZoomCheck(d[0],d[1])){l=nl;s.setDimension(d[0],d[1]);s.setPosition(p[0],p[1]);s.setMouseCursor();}else return false;return true;};s.centerImage=function(w,h,x,y){if(typeof w=='undefined'||typeof h=='undefined'){var t=s.getDimension();w=t[0],h=t[1];};if(typeof x=='undefined'||typeof y=='undefined'){var t=s.getPosition();x=t[0],y=t[1];}var fd=s.getFrameDimension();if(w<=fd[0])x=Math.round((fd[0] - w)/2);if(h<=fd[1])y=Math.round((fd[1] - h)/2);if(w>fd[0]){if(x>0)x=0;else if((x+w)<fd[0])x=fd[0]-w;}if(h>fd[1]){if(y>0)y=0;else if((y+h)<fd[1])y=fd[1]-h;}return [x,y];};s.relativeToAbsolute=function(x,y){if(x<0||y<0||x>=s.f.clientWidth||y>=s.f.clientHeight)return null;return [x-retInt(i.style.left,'px'),y-retInt(i.style.top,'px')];};s.reset=function(){var d=s.fitToFrame(oW,oH);var p=s.centerImage(d[0],d[1],0,0);s.setDimension(d[0],d[1]);s.setPosition(p[0],p[1]);l=0;};s.moveBy=function(x,y){var p=s.getPosition();p=s.centerImage(i.width,i.height,p[0]+x,p[1]+y);s.setPosition(p[0],p[1]);};s.hide=function(){if(s.outerFrame)s.outerFrame.style.display='none';else s.f.style.display='none';};s.show=function(){if(s.outerFrame)s.outerFrame.style.display='block';else s.f.style.display='block';};s.onload=null;s.onmousewheel=function(e,o,direction){s.f.focus();if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();if((l+direction)>=0){var mp=getMouseXY(e);var fp=getObjectXY(s.f);s.zoomTo(l+direction,mp[0]-fp[0],mp[1]-fp[1]);}};s.onmousemove=function(e){if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();var mp=getMouseXY(e);var p=s.getPosition();p[0]+=(mp[0]-lm[0]),p[1]+=(mp[1]-lm[1]);lm=mp;p=s.centerImage(i.width,i.height,p[0],p[1]);s.setPosition(p[0],p[1]);};s.onmouseup_or_out=function(e){if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();i.onmousemove=i.onmouseup=i.onmouseout=null;i.onmousedown=s.onmousedown;};s.onmousedown=function(e){s.f.focus();if(!e)e=window.event,e.returnValue=false;else if(e.preventDefault)e.preventDefault();lm=getMouseXY(e);i.onmousemove=s.onmousemove;i.onmouseup=i.onmouseout=s.onmouseup_or_out;};s.onkeypress=function(e){var k;if(window.event)e=window.event,k=e.keyCode,e.returnValue=false;else if(e.which)k=e.which,e.preventDefault();k=String.fromCharCode(k);var p=s.getPosition();var LEFT='a',UP='w',RIGHT='d',DOWN='s',CENTER_IMAGE='c',ZOOMIN='=',ZOOMOUT='-';if(k==LEFT)p[0]+=sp;else if(k==UP)p[1]+=sp;else if(k==RIGHT)p[0]-=sp;else if(k==DOWN)p[1]-=sp;else if(k==CENTER_IMAGE||k=='C')s.reset();else if(k==ZOOMIN||k=='+'||k=='x'||k=='X')s.zoomTo(l+1,s.f.clientWidth/2,s.f.clientHeight/2);else if((k==ZOOMOUT||k=='z'||k=='Z')&&l>0)s.zoomTo(l-1,s.f.clientWidth/2,s.f.clientHeight/2);if(k==LEFT||k==UP||k==RIGHT||k==DOWN){p=s.centerImage(i.width,i.height,p[0],p[1]);s.setPosition(p[0],p[1]);sp+=2;}};s.onkeyup=function(e){sp=5;};s.setZoomProp=function(nZF,nMZ){if(nZF==null)zoomFactor=10;zoomFactor=1+retInt(nZF,'%')/100;if(typeof nMZ=='string')m=retInt(nMZ,'%')/100;else if(typeof nMZ=='object'&&nMZ!=null){m[0]=retInt(nMZ[0],'px');m[1]=retInt(nMZ[1],'px');}else m='300%';};s.setFrameProp=function(newFrameProp){s.f.style.width=newFrameProp[0];s.f.style.height=newFrameProp[1];};s.initImage=function(){i.style.maxWidth=i.style.width=i.style.maxHeight=i.style.height=null;oW=i.width;oH=i.height;var d=s.fitToFrame(oW,oH);s.setDimension(d[0],d[1]);if(frame[2]==true)s.f.style.width=(Math.round(d[0])+'px');if(frame[3]==true)s.f.style.height=(Math.round(d[1])+'px');var p=s.centerImage(d[0],d[1],0,0);s.setPosition(p[0],p[1]);s.setMouseCursor();mo=new mouseWheel();mo.init(i,s.onmousewheel);i.onmousedown=s.onmousedown;s.f.onkeypress=s.onkeypress;s.f.onkeyup=s.onkeyup;if(viewer.onload!=null)viewer.onload(s);if(s.onload!=null)s.onload();};s.preInitImage=function(){if(preLoader!=null){i.style.left=((s.f.clientWidth-i.width)/2)+'px';i.style.top=((s.f.clientHeight-i.height)/2)+'px';}i.onload=s.initImage;i.src=imageSource;};s.setNewImage=function(newImageSource,newPreLoader){if(typeof newImageSource=='undefined')return;imageSource=newImageSource;if(typeof newPreLoader!=='undefined')preLoader=newPreLoader;if(preLoader!=null){i.onload=s.preInitImage;i.src=preLoader;return;}i.onload=s.initImage;i.src=imageSource;};s.setZoomProp(zoomFactor,m);s.frameElement=s.f=document.createElement('div');s.f.style.width=frame[0];s.f.style.height=frame[1];s.f.style.border=\"0px solid #000\";s.f.style.margin=\"0px\";s.f.style.padding=\"0px\";s.f.style.overflow=\"hidden\";s.f.style.position=\"relative\";s.f.style.zIndex=2;s.f.tabIndex=1;if(i!=null){if(parent !=null){i.parentNode.removeChild(i);parent.appendChild(s.f);}else if(replace !=null){i.parentNode.removeChild(i);replace.parentNode.replaceChild(s.f,replace);}else i.parentNode.replaceChild(s.f,i);i.style.margin=i.style.padding=\"0\";i.style.borderWidth=\"0px\";i.style.position='absolute';i.style.zIndex=3;s.f.appendChild(i);if(imageSource!=null)s.preInitImage();else s.initImage();}else{if(parent!=null)parent.appendChild(s.f);else if(replace!=null)replace.parentNode.replaceChild(s.f,replace);i=document.createElement('img');i.style.position='absolute';i.style.zIndex=3;s.f.appendChild(i);s.setNewImage(imageSource);}};viewer.onload=null;</script>"
        #imageViewer = "<img title=\"%(url)s\" src=\"%(url)s\" style=\"width:400px;\" "\
        #                "onLoad=\"new viewer({image: this, frame: ['400px','250px']});\"/>"
        output = self.htmlPageHeader % {'title': 'Resource viewer', 'script': script} \
                    + '<b title=\"%(uri)s\"><h2>Resource viewer</b>&nbsp;&nbsp;%(navigator)s</h2><hr>' \
                        % {'uri': uri, "navigator": self.htmlRenderLink("navigator")}
        output += self.htmlViewerTableHeader

        data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        if data.isValid():
            processedData = []
            images = []
            defaultType = NOCR(Nepomuk.Resource(uri).type())
            while data.next():
                currOnt = NOCR(data["ont"].toString())
                value = toUnicode(data["val"].toString())
                valueType = lvalue(ontologyValueTypes, currOnt.lower().strip(), 0, 1)
                if valueType == 'date':
                    value = formatDate(value[:19])

                elif valueType == 'datep':
                    if value[-6:] ==  "-01-01":
                        value = value.replace('-01-01', '')

                elif valueType == 'datetime':
                    value = formatDateTime(value[:19])

                elif valueType == 'datetimep':
                    value = formatDateTime(value[:19], True)

                elif valueType == 'number':
                    value = "%d" % int(float(value))

                elif valueType == 'seconds':
                    value = "%s" % datetime.timedelta(0,int(value),0)
                    #i = 0
                    #while True:
                    #    if not value[i] in ("0", ":"):
                    #        break
                    #
                    #    else:
                    #        i += 1

                    #value = value[i:]

                elif valueType == 'size':
                    value = "%s" % "%0.2f MiB" % (int(value)/1024.00/1024.00)

                #else:
                    #pass

                if value[:9] == 'nepomuk:/':
                    resource = Nepomuk.Resource(value)
                    value = ''
                    if resource.hasType(NOC('nao:Tag', True)):
                        #altLabels = QStringListToString(resource.altLabels())
                        ontLabel = '_' + currOnt + '->%nao:identifier'

                    elif resource.hasType(NOC('nco:Contact', True)):
                        #altLabels = QStringListToString(resource.altLabels())
                        ontLabel =  '_' + currOnt + '->nco:fullname'

                    elif resource.hasType(NOC('nfo:Folder', True)):
                        ontLabel = currOnt + '->nfo:fileName'

                    elif resource.hasType(NOC('nmm:MusicAlbum', True)):
                        ontLabel = currOnt + '->nie:title'

                    elif resource.hasType(NOC('rdfs:Resource', True)):
                        ontLabel = ''
                        ext = os.path.splitext(toUnicode(resource.genericLabel()))[1][1:]
                        if ext != '' and ext in QImageReader.supportedImageFormats():
                            if resource.hasProperty(NOC('nie:url')):
                                images += [toUnicode(resource.property(NOC('nie:url')).toString())]

                    else:
                        value = toUnicode(resource.type())

                    if value == '':
                        shorcut = lvalue(knownShortcuts, ontLabel, 0, 1)
                        if shorcut == None:
                            shorcut = ontLabel

                        value = '<!--' + toUnicode(resource.genericLabel()) + '-->' \
                                    + self.htmlRenderLink('uri', resource.uri(), resource.genericLabel())
                        if ontLabel != '':
                            print shorcut, resource.genericLabel()
                            value += ' ' + self.htmlRenderLink('ontology', shorcut, resource.genericLabel())

                elif currOnt == '22-rdf-syntax-ns:type':
                    value = NOCR(value)
                    if value == defaultType:
                        value = '<em>' + value + '</em>'

                elif currOnt == 'nie:url':
                    url = fromPercentEncoding(value)
                    ext = os.path.splitext(url)[1][1:].lower()
                    if ext != '' and ext in QImageReader.supportedImageFormats():
                        if fileExists(value):
                            images += [value]

                    value = ''
                    if url[:7] == 'file://':
                        value += url
                        if (os.path.exists(url[7:]) or os.path.islink(url[7:])):
                            value += ' ' + self.htmlLinkSystemRun % {"uri": url}
                            value += ' ' + self.htmlLinkOpenLocation % {"uri": os.path.dirname(url)}

                    elif url[:8] == 'filex://':
                        value += self.htmlRenderLink('unplugged', \
                                                        '', \
                                                        url \
                                                    )
#                                            url[8:].split('/')[0], \
#                                            '/' + '/'.join(url[8:].split('/')[1:]))

                elif currOnt == 'nmm:genre':
                    value = value + ' ' + self.htmlRenderLink('ontology', 'genre', value)

                else:
                    if fileExists(value):
                        ext = os.path.splitext(value)[1][1:]
                        if ext != '' and ext in QImageReader.supportedImageFormats():
                            images += [value]

                        if value[:7] != 'file://':
                            value = 'file://' + value

                        value = '<a title=\"%(url)s\" href=\"%(url)s\">%(name)s</a>' \
                                    % {'url': value, 'name': os.path.basename(value)}

                    else:
                        # No es un fichero así que añadimos los links si hay urls.
                        value = addLinksToText(value)

                if value != '':
                    processedData += [[currOnt, ontologyToHuman(currOnt), value]]

        text = ''
        if len(processedData) > 0:
            processedData = sorted(processedData, key=lambda row: row[1] + row[2])
            oldOnt = ''
            for row in processedData:
                if (oldOnt != row[1]):
                    if text != '':
                        text += '</td></tr>\n'

                    text += '<tr><td valign=\"top\" width=\"100px\">' \
                            '<b title=\"%s\">%s</b>:</td><td>%s' \
                                % (row[0], row[1], row[2])
                    oldOnt = row[1]

                else:
                    text += ', ' + row[2]

        if text == '':
            output += '<p>No data found for the uri %s.</p>\n' % uri

        else:
            output += text

        # Reverse resources.
        query = "select ?uri ?ont\n" \
                "   where { " \
                "       ?uri ?ont <%s> ." \
                "}" \
                "order by ?ont" % uri
        data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        reverseResources = []
        if data.isValid():
            while data.next():
                uri = toUnicode(data["uri"].toString())
                res = Nepomuk.Resource(uri)
                val = fromPercentEncoding(toUnicode(res.genericLabel()))
                reverseResources += [[uri, NOCR(data["ont"].toString()), val]]

            tmpOutput = ''
            if len(reverseResources) > 0:
                reverseResources = sorted(reverseResources, key=lambda revRes: revRes[1] + revRes[2])
                oldOnt = ''
                for item in reverseResources:
                    if oldOnt != item[1]:
                        if tmpOutput != '':
                            output += tmpOutput.replace('</a><', '</a>, <')
                            tmpOutput = ''

                        output += '<tr><td valign=\"top\" width=\"100px\"><b title=\"%s\">%s</b>:</td><td>' \
                                    % (item[1], ontologyToHuman(item[1], True))
                        oldOnt = item[1]

                    tmpOutput += '<!-- ' + item[2] + '-->' \
                                    + self.htmlRenderLink('uri', item[0], item[2]) # \
                                    #+ ' ' + self.htmlRenderLink('ontology', item[1], item[2])

                tmpOutput = tmpOutput.replace('</a><', '</a>, <')

            output += tmpOutput + '</td></tr>\n'

        output += self.htmlViewerTableFooter + "<hr>\n"

        # Resource images.
        if len(images) > 0:
            for image in images:
                if image[:7] != 'file://':
                    image = 'file://' + image

                output += '<img title=\"%(url)s\" style=\"height:auto;width:400px;scalefit=1\" src=\"%(url)s\"><br />\n' \
                            % {'url': image}
                #output += imageViewer % {'url': image}

            output += '<hr>\n'

        output += self.htmlPageFooter

        if stdout:
            print toUtf8(output)

        self.renderedDataText == output

        return output

        
    def formatAsHtml(self, param1 = None, structure = [], queryTime = 0, stdout = False):
        if self.searchString[:9] == "nepomuk:/":
            return self.formatResourceInfo()
        
        htmlQueryTime = time.time()

        text = self.htmlPageHeader % ("Query results")
        text += self.htmlTableHeader
        if vartype(param1) == "list":
            #self.renderedDataText = ""
            #self.renderedDataRows = 0
            if self.data == []:
                self.data = list(param1)
                self.structure = list(structure)
                
            rowsToRender = self.renderSize

        else:
            if param1 == "all":
                rowsToRender = len(self.data)

            elif param1 == "more":
                rowsToRender = self.renderSize

            else:
                rowsToRender = 0

        if self.renderedDataRows < len(self.data):
            numColumns = len(self.structure)
            for i in range(self.renderedDataRows, min(len(self.data), rowsToRender + self.renderedDataRows)):
                row = self.data[i]
                icons = ""
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
                    #try:
                    if True:
                        line = self.formatHtmlLine(Nepomuk.Resource(uri))

                    #except:
                    else:
                        line = self.htmlTableRow % (value, "", "")

                else:
                    for i in range(0, numColumns):
                        if line != "":
                            line += "<br />\n"

                        line += "%s" % row[i]

                    line = self.htmlTableRow % (line, "", "")

                if line != '':
                    self.renderedDataText += line + "\n"

                self.renderedDataRows += 1

        text += self.renderedDataText
        if self.renderedDataRows < len(self.data):
            text += '<tr><td><a href="render2:/more">%s more</a>, <a href="render2:/all">all records</a></td>' \
                    '<td>%s of %s records</td><td></td><tr>' \
                        % (min(self.renderSize, len(self.data) - self.renderedDataRows), self.renderedDataRows, len(self.data))
        
        text += self.htmlTableFooter
        text += "<br />\n" + self.htmlStadistics \
                    % {'records': len(self.data), \
                        'seconds': queryTime, \
                        'sechtml': time.time() - htmlQueryTime}
        text += self.htmlProgramInfo
        text += self.htmlPageFooter

        return text
    
    
    def formatData(self, data = [], structure = [], queryTime = 0, stdout = False):
        if self.outFormat == 1:
            return self.formatAsText(data = [], structure = [], queryTime = 0, stdout = False)

        elif self.outFormat == 2:
            return self.formatAsHtml(data = [], structure = [], queryTime = 0, stdout = False)

        else:
            return ""
        
        
#END cldataformat.py
