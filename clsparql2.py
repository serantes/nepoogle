#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - SPARQL library.                                            *
#*                                                                         *
#*   Copyright (C) 2011-2012 Ignacio Serantes <kde@aynoa.net>              *
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

import gettext, time

from PyQt4.QtCore import *
from PyKDE4.nepomuk2 import Nepomuk2
from PyKDE4.soprano import Soprano

from PyQt4.QtGui import *

from clsparql import *
from lfunctions import *
from lglobals import *


_ = gettext.gettext


#BEGIN clsparql2.py
#
# cSparqlBuilder2 class
#
class cSparqlBuilder2():

    _private_query_header = "SELECT DISTINCT %s\n" \
                            "WHERE {\n\n"
    _private_query_footer = "}\n"

    caseInsensitiveSort = True
    columns = ""
    command = ""
    # [id, ['resultColumn', [fields], [ontologyFilter], [ontologyTypeFilter]]]
    # fields: [id, 'ontology', useAsOptional, useToSort]...
    commands = [ \
                [_('--actors'), ['?x1', [[0, 'nco:fullname', True, True]], ['nmm:actor->nco:fullname'], ['nco:Contact']]], \
                [_('--albums'), ['?r', [[0, 'nie:title', True, True]], ['nie:title'], ['nmm:MusicAlbum']]], \
                [_('--audios'), ['?r', [[0, 'nie:url', True, True]], ['nie:title'], ['nfo:Audio']]], \
                #[_('--connect'), ['', [], [], []]], \
                [_('--composers'), ['?x1', [[0, 'nco:fullname', True, True]], ['nmm:composer->nco:fullname'], ['nco:Contact']]], \
                [_('--contacts'), ['?r', [[0, 'nco:fullname', True, True]], ['nco:fullname'], ['nco:Contact']]], \
                [_('--creators'), ['?x1', [[0, 'nco:fullname', True, True]], ['nco:creator->nco:fullname'], ['nco:Contact']]], \
                #[_('--daemonize'), ['', [], [], []]], \
                [_('--directors'), ['?x1', [[0, 'nco:fullname', True, True]], ['nmm:director->nco:fullname'], ['nco:Contact']]], \
                #[_('--disconnect'), ['', [], [], []]], \
                #[_('--findduplicates'), ['SELECT DISTINCT ?hash AS ?id\nWHERE {\n  ?x0 nao:userVisible 1 .\n  ?x0 nfo:hasHash ?hash .\n}\nGROUP BY ?hash\nHAVING (COUNT(?x0) > 1)\nORDER BY ?hash', [], [], []]], \
                #[_('--findduplicatemusic'), ['SELECT DISTINCT ?hash AS ?id\nWHERE {\n  ?x0 nao:userVisible 1 .\n  ?x0 nfo:hasHash ?hash .\n  ?x0 a nmm:MusicPiece .\n}\nGROUP BY ?hash\nHAVING (COUNT(?x0) > 1)\nORDER BY ?hash', [], [], []]], \
                #[_('--findduplicatephotos'), ['SELECT DISTINCT ?hash AS ?id\nWHERE {\n  ?x0 nao:userVisible 1 .\n  ?x0 nfo:hasHash ?hash .\n  ?x0 a nexif:Photo .\n}\nGROUP BY ?hash\nHAVING (COUNT(?x0) > 1)\nORDER BY ?hash', [], [], []]], \
                [_('--genres'), ['\'ont://nmm:genre\' AS ?id ?v', [[0, 'nmm:genre', True, True]], ['nmm:genre'], []]], \
                [_('--help'), ['help', [], [], []]], \
                [_('--images'), ['?r', [[0, 'nie:url', True, True], [1, 'nie:title', True, True]], ['nie:url'], ['nfo:RasterImage']]], \
                [_('--movies'), ['?r', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['nie:title'], ['nmm:Movie']]], \
                [_('--musicpieces'), ['?r', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['nie:title'], ['nmm:MusicPiece']]], \
                [_('--newcontact'), ['newcontact', [], [], []]], \
                [_('--nextepisodestowatch'), ['SELECT ?r\nWHERE {\n  ?r nmm:series ?series .\n  ?r nmm:season ?season .\n  ?r nmm:episodeNumber ?episode . FILTER(?season*1000+?episode = ?se)\n  ?r rdf:type nmm:TVShow .\n  {\n    SELECT ?series MIN(?s*1000+?e) AS ?se ?seriesTitle\n    WHERE {\n      ?r a nmm:TVShow ; nmm:series ?series ; nmm:episodeNumber ?e ; nmm:season ?s .\n      OPTIONAL { ?r nuao:usageCount ?u . } . FILTER(!BOUND(?u) or (?u < 1)) .\n      OPTIONAL { ?series nie:title ?seriesTitle . } .\n    }\n  }\n}\nORDER BY bif:lower(?seriesTitle)\n', [], [], []]], \
                [_('--notindexed'), ['notindexed', [], [], []]], \
                [_('--performers'), ['?x1', [[0, 'nco:fullname', True, True]], ['nmm:performer->nco:fullname'], ['nco:Contact']]], \
                [_('--playlist'), ['playlist', [], [], []]], \
                [_('--playmixed'), ['playmixed', [], [], []]], \
                [_('--producers'), ['?x1', [[0, 'nco:fullname', True, True]], ['nmm:producer->nco:fullname'], ['nco:Contacts']]], \
                #[_('--quit'), ['quit', [], [], []]], \
                [_('--showupdates'), ['SELECT DISTINCT ?r\nWHERE {\n  ?g nao:maintainedBy ?v . ?v nao:identifier "%s"^^xsd:string .\n  GRAPH ?g {\n    ?r nao:lastModified ?lastModified .\n  } .\n}\nORDER BY DESC(?lastModified)\n', [], [], []]], \
                [_('--shownepoogleupdates'), ['SELECT DISTINCT ?r\nWHERE {\n  ?g nao:maintainedBy ?v . ?v nao:identifier "nepoogle"^^xsd:string .\n  GRAPH ?g {\n    ?r nao:lastModified ?lastModified .\n  } .\n}\nORDER BY DESC(?lastModified)\n', [], [], []]], \
                [_('--tags'), ['?r', [[0, 'nao:prefLabel', True, True], [2, 'nao:altLabel', True, True]], ['nao:prefLabel'], ['nao:Tag']]], \
                [_('--topics'), ['?r', [[0, 'pimo:tagLabel', True, True]], ['nao:identifier'], ['pimo:Topic']]], \
                [_('--tvseries'), ['?r', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['nie:title'], ['nmm:TVSeries']]], \
                [_('--tvshows'), ['?r', [[0, 'nie:url', True, True], [1, 'nie:title', True, True]], ['nie:title'], ['nmm:TVShow']]], \
                [_('--videos'), ['?r', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['nie:title'], ['nfo:Video']]], \
                [_('--writers'), ['?x1', [[0, 'nco:fullname', True, True]], ['nmm:writer->nco:fullname'], ['nco:Contact']]] \
            ]

    enableInference = False

    engine = 0 # 0- Nepomuk.QueryParse(), 1- internal

    externalParameters = []

    #fields = [[0, 'rdf:type', True], [1, 'nao:identifier', True], [2, 'nie:url', True], [3, 'nie:title', False], [4, 'nao:prefLabel', False],
    #            [5, 'nao:description', False], [6, 'nao:numericRating', False]]
    # 'nmm:genre', 'nmm:releaseDate', ''
    fields = [ \
                [0, 'nie:url', True, True], \
                [1, 'nie:title', True, True], \
                [2, 'nco:fullname', True, True], \
                [3, 'nao:prefLabel', True, True], \
                [4, 'nao:altLabel', True, True] \
            ]
    filters = []

    getOptionalFields = True
    indentationLevel = 1
    #ontologyFilters = ['_nao:description', '_nao:identifier', '/nie:url', 'nao:hasTag->$nao:identifier', '%nie:plainTextContent']
    #ontologyFilters = ['_nao:description', '_nao:identifier', '_nie:url', 'nao:hasTag->$nao:identifierhttp://celebstar.org/wp-content/uploads/2011/06/Janina-Gavankar-pictures-3.jpg']
    ontologyFilters = ['nao:description', '%nao:identifier', '%nie:url', 'nao:hasTag->%nao:identifier', 'nco:fullname', 'nie:title']
    #ontologyFilters = ['?p0', '%nie:url']
    outputResultField = "?id"
    resultField = "?r"
    resultsetLimit = 0
    resultsetOffset = 0
    searchForUrlsTooInBasicSearch = True
    sortSuffix = '_sort'
    stdoutQuery = False

    shortcuts = [ \
                    ['_nmm:actor->nco:fullname',_('actor'), _('ac')], \
                    ['_nmm:actor?->nco:fullname', _('actors'), _('acs')], \
                    ['_nmm:albumArtist->nco:fullname', _('albumartist'), _('aa')], \
                    ['nmm:musicAlbum->nie:title', _('album'), _('al')], \
                    ['rdf:type=nmm:MusicAlbum->nie:title',_('albums'), _('als')], \
                    ['nao:altLabel', _('altlabel'), _('all')], \
                    ['?ont->nco:fullname', _('contact'), _('co')], \
                    ['rdf:type=nco:Contact->nco:fullname', _('contacts'), _('cos')], \
                    ['nao:created', _('created'), _('cd')], \
                    ['nie:contentCreated', _('contentcreated'), _('cc')], \
                    ['_nco:creator->nco:fullname', _('creator'), _('cr')], \
                    ['_nco:creator?->nco:fullname', _('creators'), _('crs')], \
                    ['nfo:depiction<-nco:fullname', _('cdepictions'), _('cds')], \
                    ['nao:description', _('description'), _('de')], \
                    ['_nmm:director->nco:fullname', _('director'), _('di')], \
                    ['_nmm:director?->nco:fullname', _('directors'), _('dis')], \
                    ['nmm:setNumber', _('discnumber'), _('dn')], \
                    ['nfo:duration', _('duration'), _('du')], \
                    ['nmm:episodeNumber', _('episode'), _('ep')], \
                    ['nexif:flash', _('flash'), _('fl')], \
                    ['nco:fullname', _('fullname'), _('fn')], \
                    ['!nmm:genre', _('genre'), _('ge')], \
                    ['_nao:hasTag->%nao:identifier', _('hastag'), _('ht')], \
                    ['nfo:height', _('height'), _('he')], \
                    ['kext:indexingLevel', _('indexinglevel'), _('il')], \
                    ['nao:isRelated<-nco:fullname', _('isrelated'), _('ir')], \
                    ['nexif:meteringMode', _('meteringmode'), _('mm')], \
                    ['nie:mimeType', _('mimetype'), _('mt')], \
                    ['rdf:type=nmm:Movie->nie:title', _('movies'), _('mos')], \
                    ['rdf:type=nmm:MusicPiece->nie:title',_('musicpieces'),  _('mps')], \
                    ['nie:url', _('name'), _('na')], \
                    ['nao:numericRating', _('numericrating'), _('nr')], \
                    ['_nmm:performer->nco:fullname', _('performer'), _('pe')], \
                    ['_nmm:performer?->nco:fullname', _('performers'), _('pes')], \
                    ['nmm:musicAlbum=?vma->nmm:performer->nco:fullname',_('performeralbum'), _('pa')], \
                    ['_nmm:producer->nco:fullname', _('producer'), _('pr')], \
                    ['_nmm:producer?->nco:fullname', _('producers'), _('prs')], \
                    ['nco:photo<-nco:fullname', _('photos'), _('ps')], \
                    ['nuao:usageCount', _('playcount'), _('pc')], \
                    ['nao:prefLabel', _('preflabel'), _('pl')], \
                    ['nao:numericRating', _('rating'), _('ra')], \
                    ['nmm:releaseDate', _('releasedate'), _('rd')], \
                    ['nexif:saturation', _('saturation'), _('sa')], \
                    ['nexif:sharpness', _('sharpness'), _('sh')], \
                    ['nmm:season', _('season'), _('se')], \
                    ['nmm:setNumber', _('setnumber'), _('sn')], \
                    ['nao:identifier', _('tag'), _('ta')], \
                    ['nfo:depiction<-nie:title', _('tdepictions'), _('tds')], \
                    ['nie:title', _('title'), _('ti')], \
                    ['nmm:trackNumber', _('tracknumber'), _('tn')], \
                    ['nmm:series->nie:title', _('tvserie'), _('ts')], \
                    ['rdf:type=nmm:TVSeries->nie:title', _('tvseries'), _('tvs')], \
                    ['nmm:series->nie:title', _('tvshow'), _('tv')], \
                    ['rdf:type=nmm:TVShow->nie:title', _('tvshows'), _('tvw')], \
                    ['!rdf:type', _('type'), _('ty')], \
                    ['%nie:url', _('url'), _('ur')], \
                    ['nuao:usageCount', _('usagecount'), _('uc')], \
                    ['nfo:width', _('width'), _('wi')], \
                    ['nexif:whiteBalance', _('whitebalance'), _('wb')], \
                    ['_nmm:writer->nco:fullname', _('writer'), _('wr')], \
                    ['_nmm:writer?->nco:fullname', _('writers'), _('wrs')] \
                ]

    subqueryResultField = resultField

    tempData = ['', [], [], []]

    #typeFilters = ['nao#Tag', 'nfo#FileDataObject']
    typeFilters = []

    visibilityFilter = ""

    warningsList = []


    def __init__(self):
        pass


    def __del__(self):
        pass


    def buildQuery(self, searchString = ''):
        if ((self.command == '') and (self.filters == []) and (searchString != '')):
            self.filters = self.stringQueryConversion(searchString.strip())

        if (self.command == ''):
            pass

        else:
            idx = lindex(self.commands, self.command, 0)
            if (idx >= 0):
                if (self.commands[idx][1][0] == ''):
                    raise Exception("Sorry, command <b>%s</b> not implemented yet." % self.command)

                elif (self.commands[idx][1][0].strip().upper()[:7] == "SELECT "):
                    # It's a full query.
                    query = self.commands[idx][1][0].strip()
                    if self.stdoutQuery:
                        print toUtf8(query)

                    if (query.find("%s") >= 0):
                        if (len(self.filters) < 1):
                            raise Exception("Command \"%s\"requires one parameter." % self.command)

                        query = query % self.filters[0][0]

                    return query

                else:
                    self.tempData = self.commands[idx][1]

            else:
                raise Exception("Unknown command <b>%s</b>, try <b>--help</b> command." % self.command)

            # Comandos especiales.
            if self.tempData[0] == 'help':
                raise Exception(self.tempData[0])

            elif (self.tempData[0] == "notindexed"):
                try:
                    self.command == self.tempData[0].split(":")[1]

                except:
                    self.command = ""

                raise Exception(self.tempData[0])

            elif (self.tempData[0] == 'newcontact'):
                raise Exception(self.tempData[0])

            elif (self.tempData[0] in ('playlist', 'playmixed')):
                self.externalParameters = [self.tempData[0]]
                self.tempData = ['', [], [], []]

        if (self.tempData[0] == ''):
            if (self.columns == ""):
                columns = '%s AS %s' % (self.resultField, self.outputResultField)

            else:
                columns = self.columns

        else:
            if (self.tempData[0].lower().find(" as ") < 0):
                columns = '%s AS %s' % (self.tempData[0], self.outputResultField)

            else:
                columns = self.tempData[0]

        footer = self._private_query_footer
        header = self._private_query_header % columns
        having = self.bsHaving()
        limits = self.bsResulsetLimits()
        optionalFields = self.bsOptionalFields()
        sort = self.bsSort()
        subqueries = self.bsSubqueries()

        #SELECT DISTINCT ?r AS ?id
        #WHERE {
        #
        #  { subquery } [[UNION] { subquery }...
        #
        #  [optional { ?r ?p ?v . }]...
        #
        #}
        #ORDER BY bif:lower(?v)...

        query = header \
                + subqueries \
                + optionalFields \
                + footer \
                + having \
                + sort \
                + limits

        if self.stdoutQuery:
            print toUtf8(query)

        self.tempData = ['', [], [], []]

        return query


    def buildDateFilter(self, val, op):
        if (op == "=="):
            op = "="

        dateType = None
        val = val.upper()
        typeMark = val[-1]

        if (typeMark in ("Y", "M", "D")):
            val = val[:-1]

        else:
            typeMark = None

        try:
            intVal = int(val)
            if (typeMark == None):
                if ((intVal >= 1) and (intVal <= 12)):
                    typeMark = "M"

                elif ((intVal > 12) and (intVal <= 31)):
                    typeMark = "D"

                else:
                    typeMark = "Y"

            val = intVal

            if (typeMark == "Y"):
                dateFilter = "FILTER(bif:year(?v) %s %s) ." % (op, val)

            elif (typeMark == "M"):
                dateFilter = "FILTER(bif:month(?v) %s %s) ." % (op, val)

            elif (typeMark == "D"):
                dateFilter = "FILTER(bif:dayofmonth(?v) %s %s) ." % (op, val)

            else:
                raise Exception("Can't recognized <b>%s</b> as date format." % self.command)

        except:
            dateFilter =  "FILTER(xsd:date(?v) %s \"%s\"^^xsd:date) ." % (op, val)

        return dateFilter


    def buildFloatFilter(self, val, op, precision = 4):
        if (op in ("=", "==")):
            # Workaround for the precision problem.
            if vartype(val) in ("str", "unicode"):
                val = round(float(val), precision)

            val = round(val, precision)
            adjustmentNumber = "0.%0" + "%sd1" % (precision - 1)
            adjustmentNumber = float(adjustmentNumber % 0)
            val2 = val + adjustmentNumber
            val -= adjustmentNumber
            return "FILTER((?v >= %(val)s) and (?v < %(val2)s)) ." % {'op': op, 'val': val, 'val2': val2}

        else:
            return "FILTER(?v %(op)s %(val)s) ." % {'op': op, 'val': val}


    def buildTimeFilter(self, val, op):
        if op == "==":
            op = "="

        dateType = None
        val = val.upper()
        typeMark = val[-1]

        if (typeMark in ("H", "M", "S")):
            val = val[:-1]

        else:
            typeMark = None

        try:
            intVal = int(val)
            if (typeMark == None):
                if ((intVal >= 1) and (intVal <= 24)):
                    typeMark = "H"

                elif ((intVal > 24) and (intVal <= 60)):
                    typeMark = "M"

                else:
                    typeMark = "S"

            if (typeMark == "H"):
                intVal = intVal*60*60

            elif (typeMark == "M"):
                intVal = intVal*60

            else:
                pass

            return "FILTER(?v %s %s) ." % (op, intVal)

        except:
            pass

        #BUG: nfo:duration>3:25 da error.
        try:
            splitTime = val.split(":")
            if len(splitTime) == 3:
                intVal = int(splitTime[0])*60*60 + int(splitTime[1])*60 + int(splitTime[2])

            elif len(splitTime) == 2:
                intVal = int(splitTime[0])*60 + int(splitTime[1])

            elif len(splitTime) == 1:
                intVal = int(splitTime[0])

            else:
                raise Exception("Can't recognized <b>%s</b> as time format." % self.command)

        except:
            raise Exception("Can't recognized <b>%s</b> as time format." % self.command)

        return "FILTER(?v %s %s) ." % (op, intVal)


    def buildExpressionFilter(self, valType, operator, value):
        # If string is between " they must be removed.
        if (value[0] == value[-1] == '"'):
            value = value[1:-1]

        filterExpression = ""

        if (value == "") or (value == ".*"):
            pass

        elif (valType in ('number', 'int', 'integer')):
            if (operator == "=="):
                operator = "="

            filterExpression = "FILTER(?v %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "float"):
            filterExpression = self.buildFloatFilter(value, operator)

        elif ((valType == "date") or (valType == "datep")):
            filterExpression = self.buildDateFilter(value, operator)

        elif ((valType == "datetime") or (valType == "datetimep")):
            filterExpression = self.buildDateFilter(value, operator)

        elif ((valType == "seconds") or (valType == "time") or (valType == "duration")):
            filterExpression = self.buildTimeFilter(value, operator)

        elif (valType == "aperturevalue"):
            if value[0].lower() == 'f':
                value = value[1:]

            filterExpression = self.buildFloatFilter(value, operator)

        elif (valType == "exposurebiasvalue"):
            valTerms = value.split("/")
            if (len(valTerms) > 1):
                value = float(valTerms[0])/float(valTerms[1])

            filterExpression = self.buildFloatFilter(value, operator)

        elif (valType == "exposuretime"):
            valTerms = value.split("/")
            if (len(valTerms) > 1):
                value = float(valTerms[0])/float(valTerms[1])

            filterExpression = self.buildFloatFilter(value, operator, 6)

        elif (valType == "flash"):
            value = value.lower()
            if (value.lower() in NEXIF_FLASH_LOWER):
                value = lindex(NEXIF_FLASH_LOWER, value)

            else:
                value = 0

            if (value == 0):
                operator = "="

            else:
                value = 0
                operator = ">"

            filterExpression = "FILTER(bif:bit_and(xsd:integer(?v), 1) %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "focallength"):
            valTerms = value.split("/")
            if (len(valTerms) > 1):
                value = float(valTerms[0])/float(valTerms[1])

            filterExpression = self.buildFloatFilter(value, operator)

        elif (valType == "indexinglevel"):
            if (value.lower() in KEXT_INDEXING_LEVEL_LOWER):
                value = lindex(KEXT_INDEXING_LEVEL_LOWER, value)

            else:
                value = "-1" # A value not defined in NEXIF_WHITE_BALANCE

            filterExpression = "FILTER(xsd:integer(?v) %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "meteringmode"):
            if (value.lower() in NEXIF_METERING_MODE_LOWER):
                value = lindex(NEXIF_METERING_MODE_LOWER, value)
                if (value == 7):
                    value = 255

            else:
                value = "-1" # A value not defined in NEXIF_METERING_MODE

            filterExpression = "FILTER(xsd:integer(?v) %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "orientation"):
            if operator == "==":
                operator = "="

            filterExpression = "FILTER(?v %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "saturation"):
            if (value.lower() in NEXIF_SATURATION_LOWER):
                value = lindex(NEXIF_SATURATION_LOWER, value)

            else:
                value = "-1" # A value not defined in NEXIF_SATURATION

            filterExpression = "FILTER(xsd:integer(?v) %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "sharpness"):
            if (value.lower() in NEXIF_SHARPNESS_LOWER):
                value = lindex(NEXIF_SHARPNESS_LOWER, value)

            else:
                value = "-1" # A value not defined in NEXIF_SHARPNESS

            filterExpression = "FILTER(xsd:integer(?v) %(op)s %(val)s) ." % {'op': operator, 'val': value}

        elif (valType == "whitebalance"):
            if (value.lower() in NEXIF_WHITE_BALANCE_LOWER):
                value = lindex(NEXIF_WHITE_BALANCE_LOWER, value)

            else:
                value = "-1" # A value not defined in NEXIF_WHITE_BALANCE

            filterExpression = "FILTER(xsd:integer(?v) %(op)s %(val)s) ." % {'op': operator, 'val': value}

        else:
            # String.
            if (operator == "=="):
                filterExpression = "FILTER(?v %(op)s \"%(val)s\"^^xsd:string) ." % {'op': "=", 'val': value}

            else:
                value = value.replace('(', '\\\(').replace(')', '\\\)').replace('+', '\\\+')
                if (operator == "="):
                    filterExpression = "FILTER(REGEX(?v, \"%(val)s\"^^xsd:string, 'i')) ." % {'val': value}

                elif (operator == "!="):
                    filterExpression = "FILTER(!REGEX(?v, \"%(val)s\"^^xsd:string, 'i')) ." % {'val': value}

                else:
                    filterExpression = "FILTER(?v %(op)s \"%(val)s\"^^xsd:string) ." % {'op': operator, 'val': value}

        return filterExpression


    def ontologyConversion(self, ontology = ''):
        ont = ontology.strip().lower()

        if (ont == ''):
            ontology = ''

        elif (ont.find(':') > 0):
            pass

        else:
            idx = lindex(self.shortcuts, ont, 1)
            if (idx == None):
                # Miramos en las abreviaturas.
                idx = lindex(self.shortcuts, ont, 2)

            if (idx >= 0):
                ontology = self.shortcuts[idx][0]

            else:
                if (ontology[0] != "?"): # A variable is set instead an ontology.
                    raise Exception("Unknown ontology <b>%s</b>." % ontology)

        return ontology


    def bsOptionalFields(self):
        if not self.getOptionalFields:
            return ""

        if (self.tempData[1] == []):
            fields = self.fields
            subqueryResultField = self.subqueryResultField

        else:
            fields = self.tempData[1]
            subqueryResultField = self.tempData[0]
            if (self.tempData[0].lower().find(" as ") >= 0):
                subqueryResultField = self.subqueryResultField

        text = ""
        for item in fields:
            if not item[2]:
                continue

            try:
                text += "  optional { %(resultField)s %(ontology)s ?%(field)s . }\n" \
                            % {'resultField': subqueryResultField, 'ontology': item[1], 'field': item[1].split(":")[1]}

            except:
                pass

        if (text != None):
            text += "\n"

        return text


    def bsHaving(self):
        return '\n'
        #return "HAVING !(?type = <http://www.w3.org/2000/01/rdf-schema#Resource>)\n"
        #return "HAVING (?type = <http://www.w3.org/2000/01/rdf-schema#Resource>)\n"
        #return "GROUP BY (?x0)\n"


    def bsResulsetLimits(self):
        text = ''
        if self.resultsetLimit > 0:
            text += "LIMIT %s\n" % self.resultsetLimit

        if self.resultsetOffset > 0:
            text += "OFFSET %s" % self.resultsetOffset

        return text


    def bsSort(self):
        if self.tempData[1] == []:
            fields = self.fields

        else:
            fields = self.tempData[1]

        sortText = ""
        for item in fields:
            if item[3]:
                try:
                    columnName = "?" + item[1].split(":")[1]
                    if self.caseInsensitiveSort:
                        sortText += "bif:lower(%s) " % columnName

                    else:
                        sortText += columnName + " "

                except:
                    pass

        if (sortText != ""):
            sortText = "ORDER BY " + sortText + "\n"

        return sortText


    def bsSubqueryTerm(self, term, indentationLevel = 2):
        # term[0] - value
        # term[1] - operator
        # term[2] - ontology
        indent = ("%%%ds" % (indentationLevel*2)) % ""
        indent2 = ("%%%ds" % ((indentationLevel+1)*2)) % ""
        indent3 = ("%%%ds" % ((indentationLevel+2)*2)) % ""
        strTerm = ""

        try:
            value = term[0]

        except:
            value = ""

        try:
            operator = term[1]
            if (operator == ''):
                operator = '='

        except:
            operator = "="

        try:
            ontologies = term[2]

        except:
            ontologies = ""

        if (ontologies == ""):
            # There aren't ontologies, generic text search.
            if (operator == "!="):
                strTerm += indent + "%s a ?v1 . FILTER NOT EXISTS {\n" % (self.subqueryResultField)
                strTerm += indent2 + "{\n"
                strTerm += indent3 + "%s ?p1 ?v2 . FILTER(bif:contains(?v2, \"'%s'\")) .\n" % (self.subqueryResultField, value)
                strTerm += indent2 + "} UNION {\n"
                strTerm += indent3 + "%s ?p2 [ ?p3 ?v2 ] . FILTER(bif:contains(?v2, \"'%s'\")) .\n" % (self.subqueryResultField, value)
                strTerm += indent2 + "} .\n"
                strTerm += indent + "} .\n"

            else:
                strTerm += indent + "{\n"
                strTerm += indent2 + "%s ?p ?v . FILTER(bif:contains(?v, \"'%s'\")) .\n" % (self.subqueryResultField, value)
                strTerm += indent + "} UNION {\n"
                strTerm += indent2 + "%s ?p1 [ ?p2 ?v ] . FILTER(bif:contains(?v, \"'%s'\")) .\n" % (self.subqueryResultField, value)
                if self.searchForUrlsTooInBasicSearch:
                    strTerm += indent + "} UNION {\n"
                    strTerm += indent2 + "%s nie:url ?v . FILTER(REGEX(?v, \"%s\"^^xsd:string, 'i')) .\n" % (self.subqueryResultField, value)

                strTerm += indent + "}\n"

        else:
            # There are ontologies.
            i = numInverseRelations = relationAdjustmentResource = relationAdjustmentValue = 0
            ontologies = self.ontologyConversion(ontologies)
            ontologyElements = re.split('->|<-', ontologies)
            ontologyRelations = re.findall('->|<-', ontologies)

            optionalUsage = False
            clause = ""
            fieldUsedAsResult = "?x%d " % 0
            for ontology in ontologyElements:
                ontology = self.ontologyConversion(ontology)
                valType = ""
                if (ontology[0] == "%"):
                    ontology = ontology[1:]
                    value = toN3(value)

                elif (ontology[0] == "_"):
                    ontology = ontology[1:]
                    optionalUsage = optionalUsage or (operator == "!=")

                elif (ontology[0] == "!"):
                    ontology = ontology[1:]
                    optionalUsage = optionalUsage or (operator == "!=")

                elif ((value == "") and (operator == "!=")):
                    optionalUsage = True

                if (ontology[-1] == "?"): # Use this ontology as the result one.
                    fieldUsedAsResult = "?x%d " % (i+1)
                    ontology = ontology[:-1]

                valType = self.ontologyVarType(ontology)
                if (ontology.find('=') >= 0):
                    rName = "?x%d" % (i)
                    clause += "%(r)s %(ont)s %(v)s . " % {'ont': ontology.split('=')[0], 'r': rName, 'v': ontology.split('=')[1]}

                else:
                    # Here is where relations are stablished:
                    # Normal sample:  { ?r ?ont1 ?x1 . ?x1 ?ont2 ?x2 . FILTER(REGEX(?x2, "text"^^xsd:string, 'i')) }
                    # Inverse sample: #{ ?x1 ?ont1 ?r . ?x1 ?ont2 ?x2 . FILTER(REGEX(?x2, "iu"^^xsd:string, 'i')) }

                    try:
                        doSwap = (ontologyRelations[i] == "<-")

                    except:
                        doSwap = False

                    if doSwap:
                        vName = "?x%d" % i
                        rName = "?x%d" % (i + 1)

                    else:
                        rName = "?x%d" % i
                        vName = "?x%d" % (i + 1)

                    clause += "%(r)s %(ont)s %(v)s . " % {'ont': ontology, 'r': rName, 'v': vName}
                    i += 1

            clause = clause.replace(fieldUsedAsResult, self.subqueryResultField + " ").replace("?x%d " % i, "?v ")
            if optionalUsage:
                strTerm = indent + self.subqueryResultField + " a ?v1 . FILTER NOT EXISTS {\n" \
                            + indent2 + clause + self.buildExpressionFilter(valType, "=", value) + "\n" \
                            + indent + "}\n"

            else:
                strTerm = indent + clause + self.buildExpressionFilter(valType, operator, value) + "\n"

        return strTerm


    def bsSubquery(self, term, isUnion = False):
        if (term[0] == "("):
            indent = "%%%ds" % (self.indentationLevel*2)
            subquery = (indent + "{\n") % ""
            self.indentationLevel += 1

        elif (term[0] == ")"):
            self.indentationLevel -= 1
            indent = "%%%ds" % (self.indentationLevel*2)
            subquery = ("\n" + indent + "}") % ""

        else:
            strTerm = self.bsSubqueryTerm(term, self.indentationLevel + 2)
            subquery = ""

            if (strTerm != ""):
                indent = "%%%ds" % (self.indentationLevel*2)
                indent2 = "%%%ds" % ((self.indentationLevel+1)*2)
                if isUnion:
                    subquery += "{\n"

                else:
                    subquery += (indent + "{\n") % ("")

                subquery += "\n"
                subquery += (indent2 + "SELECT DISTINCT %s\n") % ("", self.subqueryResultField)
                subquery += (indent2 + "WHERE {\n\n") % ("")
                subquery += strTerm + '\n'
                subquery += (indent2 + "}\n") % ("")
                subquery += "\n"
                subquery += (indent + "}") % ("")

        return subquery


    def bsSubqueries(self):
        subqueries = ""
        # First filter term for rdf:type ontology,
        # for example: ?r rdf:type nmm:Movie
        if (self.tempData[3] == []):
            typeFilters = self.typeFilters

        else:
            typeFilters = self.tempData[3]

        for item in typeFilters:
            # Two spaces for indentation level.
            try:
                resultField = self.tempData[0]
                if (resultField == ""):
                    resultField = self.resultField

            except:
                resultField = self.resultField

            subqueries += "  %s rdf:type %s .\n" % (resultField, item)

        for item in self.tempData[2]:
            if (self.filters == []):
                filterValue = ".*"

            else:
                filterValue = self.filters[0][0]
                self.filters = []

            subqueries += self.bsSubqueryTerm([filterValue, "=", item], self.indentationLevel)

        #[termino [<and | or> termino]...
        #[[u'iu', '=', u'performer'], ['and', '', ''], [u'iu', '=', u'_nco:creator->nco:fullname']]
        unionClause = ""
        for term in self.filters:
            if (term[0] == "and"):
                unionClause = ""

            elif (term[0] == "or"):
                unionClause = " UNION "

            else:
                subquery = self.bsSubquery(term, unionClause == " UNION ")
                if (subquery != ""):
                    subqueries += unionClause + subquery

        return subqueries + "\n\n"


    def ontologyVarType(self, ontology = ''):
        try:
            ontType = ontologyInfo(ontology)[2]

        except:
            ontType = None

        return ontType


    def split(self, string = ''):
        #print string
        specialChars = [":", "+", "-", ">", "<", "="]
        results = []
        if (string != ''):
            breakChar = ' '
            newItem = True
            for i in range(0, len(string)):
                #print breakChar, string[i], results
                if (string[i] == breakChar):
                    if breakChar in ("'", '"'):
                        results[-1] += breakChar

                    newItem = True
                    breakChar = ' '
                    continue

                if ((string[i] == '"' or string[i] == "'")):
                    if ((i == 0) or (string[i-1] not in specialChars)):
                        if string[i] == breakChar:
                            newItem = True

                    if breakChar == ' ':
                        breakChar = string[i]

                if (breakChar == " "):
                    if string[i] in ("(", ")"):
                        results += [string[i]]
                        newItem = True
                        continue

                if (newItem and ((results == []) or (results[-1] != ''))):
                    results += ['']
                    newItem = False

                results[-1] += string[i]

        #for result in results:
            #if ((result != "") and (result[0] == "-") and (result[1] != "-")):
            #    i = lindex(self.warningsList, "BUG001", 0)
            #    if i != None:
            #        self.warningsList[i] += [result]

            #    else:
            #        self.warningsList = [["BUG001", result]]

        #    if result == "(" or result == ")":
        #        raise Exception(_("Syntax error, parenthesis are not supported. Use quotes to search for parenthesis characters."))

        #print 'Results:', results
        return results


    def stringQueryConversion(self, string = ''):
        if string == '':
            raise Exception("Type something to start querying.")

        allFilters = []
        oneFilter = []

        if string[:3].lower() in ('e0 ', 'e1 ', 'e2 '):
            string = string[3:]

        items = self.split(string)
        #print toUtf8(string)
        #print toUtf8(items)

        self.command = ""
        command = ""
        commandsFound = 0
        addAnd = False
        for item in items:
            if item[:2] == '--':
                command = item
                commandsFound += 1
                continue
                #oneFilter = [item, '', '']

            elif item.lower() == 'or':
                oneFilter = ['or', '', '']
                addAnd = False

            elif item.lower() == 'and':
                oneFilter = ['and', '', '']
                addAnd = False

            else:
                if addAnd == True:
                    allFilters += [['and', '', '']]

                ontology = ''
                while True:
                    if item == "":
                        item = ".*"

                    if item[0] in ('"', "'") and item[-1] in ('"', "'"):
                        parts = [item[1:-1], '', '']

                    else:
                        parts = item.partition(':')

                    if parts[1] == ':':
                        ontology += parts[0] + ':'
                        item = parts[2]

                    else:
                        ontology = ontology[0:-1]
                        data = parts[0]
                        break

                if data == '':
                    raise Exception(_("Syntax error, please check your search text."))

                if data == '':
                    operator = ''

                else:
                    operator = data[0]

                #Hack operador negativo.
                if ((len(data) > 1) and (operator == "-")):
                    # "-<" ==> ">"
                    if data[1] == "<":
                        operator = ">"
                        if (len(data) > 2) and (data[2] == "="):
                            data = ">" + data[3:]

                        else:
                            data = ">=" + data[2:]

                    # "->" ==> "<"
                    elif data[1] == ">":
                        operator = "<"
                        if (len(data) > 2) and (data[2] == "="):
                            data = "<" + data[3:]

                        else:
                            data = "<=" + data[2:]
                #Hack operador negativo.

                dataIndex = 1
                if operator == "=" and (len(data) > 1) and data[1] == "-":
                    pass

                elif operator == '-':
                    operator = '!='

                elif operator == '+':
                    operator = '=='

                elif operator == '>':
                    operator = data[1]
                    if operator == '=':
                        operator = '>='
                        dataIndex = 2

                    else:
                        operator = '>'

                elif operator == '<':
                    operator = data[1]
                    if operator == '=':
                        operator = '<='
                        dataIndex = 2

                    else:
                        operator = '<'

                else:
                    operator = '='
                    dataIndex = 0

                try:
                    data = data[dataIndex:]
                    if (data[0] == data[-1] == '"') or (data[0] == data[-1] == "'"):
                        data = data[1:-1]

                except:
                    data = ""

                oneFilter = [data, operator, ontology]
                addAnd = True

            # A little bit of language improvement.
            if oneFilter[2] == "":
                for op in (">=", "<=", ">", "<", "="):
                    oneFilterDummy = oneFilter[0].split(op)
                    if len(oneFilterDummy) > 1:
                        oneFilter[0] = oneFilterDummy[1]
                        oneFilter[1] = op
                        oneFilter[2] = oneFilterDummy[0]
                        break

            try:
                if oneFilter[0][0] == "=":
                    oneFilter[0] = oneFilter[0][1:]

            except:
                pass

            # A little bit of language improvement.

            allFilters += [oneFilter]

        # Check basic errors.
        if allFilters != [] and (allFilters[-1][0] in ('and', 'or')):
            allFilters = []
            raise Exception(_("Syntax error, please check your search text."))

        if ((commandsFound > 0) and (len(allFilters) > 1)):
            if command.lower() not in ('--playlist', '--playmixed'):
                allFilters = []
                raise Exception(_("Syntax error, commands and queries are mutual exclude."))

        # ¿Es un comando?
        if commandsFound > 1:
            raise Exception(_("Syntax error, only one command per query."))

        elif commandsFound == 1:
            dummy = command.split(':')
            command = dummy[0].lower()

            # Commands that don't support filters.
            if command in ("--playlist", "--playmixed"):
                if (len(dummy) > 1):
                    raise Exception(_("Syntax error, command <b>%s</b> don't support an associated filter.") % command)

            # Commands that support filters.
            elif ((len(dummy) > 1) and (dummy[1] != "")):
                if dummy[1][0] == '-':
                    allFilters = [[dummy[1][1:], '!=', '']]

                elif dummy[1][0] == '+':
                    allFilters = [[dummy[1][1:], '==', '']]

                else:
                    allFilters = [[dummy[1], '=', '']]

            else:
                allFilters = []

        # Commands associated to queries.
        if ((len(allFilters) == 0) and (command in ("--playlist", "--playmixed"))):
            raise Exception(_("Syntax error, command <b>%s</b> require an associated query.") % command)

        self.command = command
        return allFilters


    def executeQuery(self, query = []):
        try:
            if DO_NOT_USE_NEPOMUK:
                model = Soprano.Client.DBusModel('org.kde.NepomukStorage', '/org/soprano/Server/models/main')

            else:
                model = Nepomuk2.ResourceManager.instance().mainModel()

            queryTime = time.time()
            if self.enableInference:
                result = model.executeQuery(query, Soprano.Query.QueryLanguageSparql)

            else:
                result = model.executeQuery(query, Soprano.Query.QueryLanguageSparqlNoInference)

            queryTime = time.time() - queryTime

        except:
            raise Exception("Seems like Nepomuk is not running.")

        structure = []
        data = []

        if result.isValid():
            for bindings in result.allBindings():
                if structure == []:
                    for bindingName in bindings.bindingNames():
                        if bindingName[-len(self.sortSuffix):] == self.sortSuffix:
                            continue

                        structure += [toUnicode(bindingName.toUtf8())]

                aRow = []
                for bindingName in bindings.bindingNames():
                    # Fields to case insensitive sort must be ignored.
                    if bindingName[-len(self.sortSuffix):] == self.sortSuffix:
                        continue

                    #value = toUnicode(toPercentEncoding(bindings[bindingName].toString()))
                    value = toUnicode(bindings[bindingName].toString())

                    if value != '':
                        if bindingName == 'type':
                            value = os.path.basename(toUnicode(value))
                            value = value.split("#")
                            try:
                                value = '[' + value[1] + ']'

                            except:
                                value = value[0]

                        elif value[:7] == 'file://' or value[:7] == 'http://' or value[:8] == 'https://':
                            # Novedad en kde 4.7.0
                            qurl = QUrl()
                            qurl.setEncodedUrl(toUtf8(value))
                            value = toUnicode(qurl.toString())
                            # Novedad en kde 4.7.0

                        aRow += [value]

                if len(aRow) > 0:
                    if len(aRow) < len(structure):
                        for i in range(len(aRow), len(structure)):
                            aRow += ['']

                    data += [aRow]

            result.close()

        else:
            result.close()
            raise Exception('Can\'t execute query, check syntax and test if Nepomuk is running.')

        return data, structure, queryTime

#END clsparql.py
