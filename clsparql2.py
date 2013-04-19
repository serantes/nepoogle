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

    columns = ""
    command = ""

    # [id, ['resultColumn', [fields], [ontologyFilter], [ontologyTypeFilter]]]
    # fields: [id, 'ontology', useAsOptional, useToSort, ascending]...
    commands = [ \
                [_('--actors'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nmm:actor->nco:fullname'], ['nco:Contact']]], \
                [_('--albums'), ['?r', [[0, 'nie:title', True, True, True]], ['nie:title'], ['nmm:MusicAlbum']]], \
                [_('--audios'), ['?r', [[0, 'nie:url', True, True, True]], ['nie:title'], ['nfo:Audio']]], \
                #[_('--connect'), ['', [], [], []]], \
                [_('--composers'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nmm:composer->nco:fullname'], ['nco:Contact']]], \
                [_('--contacts'), ['?r', [[0, 'nco:fullname', True, True, True]], ['nco:fullname'], ['nco:Contact']]], \
                [_('--creators'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nco:creator->nco:fullname'], ['nco:Contact']]], \
                #[_('--daemonize'), ['', [], [], []]], \
                [_('--directors'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nmm:director->nco:fullname'], ['nco:Contact']]], \
                #[_('--disconnect'), ['', [], [], []]], \
                #[_('--findduplicates'), ['SELECT DISTINCT ?hash AS ?id\nWHERE {\n  ?x0 nao:userVisible 1 .\n  ?x0 nfo:hasHash ?hash .\n}\nGROUP BY ?hash\nHAVING (COUNT(?x0) > 1)\nORDER BY ?hash', [], [], []]], \
                #[_('--findduplicatemusic'), ['SELECT DISTINCT ?hash AS ?id\nWHERE {\n  ?x0 nao:userVisible 1 .\n  ?x0 nfo:hasHash ?hash .\n  ?x0 a nmm:MusicPiece .\n}\nGROUP BY ?hash\nHAVING (COUNT(?x0) > 1)\nORDER BY ?hash', [], [], []]], \
                #[_('--findduplicatephotos'), ['SELECT DISTINCT ?hash AS ?id\nWHERE {\n  ?x0 nao:userVisible 1 .\n  ?x0 nfo:hasHash ?hash .\n  ?x0 a nexif:Photo .\n}\nGROUP BY ?hash\nHAVING (COUNT(?x0) > 1)\nORDER BY ?hash', [], [], []]], \
                [_('--genres'), ['\'ont://nmm:genre\' AS ?id ?v', [[0, 'nmm:genre', True, True, True]], ['nmm:genre'], []]], \
                [_('--help'), ['help', [], [], []]], \
                [_('--images'), ['?r', [[0, 'nie:url', True, True, True], [1, 'nie:title', True, True, True]], ['nie:url'], ['nfo:RasterImage']]], \
                [_('--movies'), ['?r', [[0, 'nie:title', True, True, True], [1, 'nie:url', True, True, True]], ['nie:title'], ['nmm:Movie']]], \
                [_('--musicpieces'), ['?r', [[0, 'nie:title', True, True, True], [1, 'nie:url', True, True, True]], ['nie:title'], ['nmm:MusicPiece']]], \
                [_('--musicplayer'), ['musicplayer', [], [], []]], \
                [_('--newcontact'), ['newcontact', [], [], []]], \
                [_('--nextepisodestowatch'), ['SELECT ?r\nWHERE {\n  ?r nmm:series ?series .\n  ?r nmm:season ?season .\n  ?r nmm:episodeNumber ?episode . FILTER(?season*1000+?episode = ?se)\n  ?r rdf:type nmm:TVShow .\n  {\n    SELECT ?series MIN(?s*1000+?e) AS ?se ?seriesTitle\n    WHERE {\n      ?r a nmm:TVShow ; nmm:series ?series ; nmm:episodeNumber ?e ; nmm:season ?s .\n      OPTIONAL { ?r nuao:usageCount ?u . } . FILTER(!BOUND(?u) or (?u < 1)) .\n      OPTIONAL { ?series nie:title ?seriesTitle . } .\n    }\n  }\n}\nORDER BY bif:lower(?seriesTitle)\n', [], [], []]], \
                [_('--notindexed'), ['notindexed', [], [], []]], \
                [_('--performers'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nmm:performer->nco:fullname'], ['nco:Contact']]], \
                [_('--playlist'), ['playlist', [], [], []]], \
                [_('--playmixed'), ['playmixed', [], [], []]], \
                [_('--producers'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nmm:producer->nco:fullname'], ['nco:Contacts']]], \
                #[_('--quit'), ['quit', [], [], []]], \
                [_('--showupdates'), ['SELECT DISTINCT ?r\nWHERE {\n  ?g nao:maintainedBy ?v . ?v nao:identifier "%s"^^xsd:string .\n  GRAPH ?g {\n    ?r nao:lastModified ?lastModified .\n  } .\n}\nORDER BY DESC(?lastModified)\n', [], [], []]], \
                [_('--shownepoogleupdates'), ['SELECT DISTINCT ?r\nWHERE {\n  ?g nao:maintainedBy ?v . ?v nao:identifier "nepoogle"^^xsd:string .\n  GRAPH ?g {\n    ?r nao:lastModified ?lastModified .\n  } .\n}\nORDER BY DESC(?lastModified)\n', [], [], []]], \
                [_('--sort'), ['sort', [], [], []]], \
                [_('--tags'), ['?r', [[0, 'nao:prefLabel', True, True, True], [2, 'nao:altLabel', True, True, True]], ['nao:prefLabel'], ['nao:Tag']]], \
                [_('--topics'), ['?r', [[0, 'pimo:tagLabel', True, True, True]], ['nao:identifier'], ['pimo:Topic']]], \
                [_('--tvseries'), ['?r', [[0, 'nie:title', True, True, True], [1, 'nie:url', True, True, True]], ['nie:title'], ['nmm:TVSeries']]], \
                [_('--tvshows'), ['?r', [[0, 'nie:url', True, True, True], [1, 'nie:title', True, True, True]], ['nie:title'], ['nmm:TVShow']]], \
                [_('--videos'), ['?r', [[0, 'nie:title', True, True, True], [1, 'nie:url', True, True, True]], ['nie:url'], ['nfo:Video']]], \
                [_('--writers'), ['?x1', [[0, 'nco:fullname', True, True, True]], ['nmm:writer->nco:fullname'], ['nco:Contact']]] \
            ]

    enableInference = False

    engine = 1 # 0- Nepomuk.QueryParse(), 1- internal

    externalParameters = []

    # [id, 'ontology', useAsOptional, useToSort, ascending]
    fields = [ \
                [0, 'nie:url', True, True, True], \
                [1, 'nie:title', True, True, True], \
                [2, 'nco:fullname', True, True, True], \
                [3, 'nao:prefLabel', True, True, True] \
            ]

    filters = []
    #filterHard = "  FILTER(REGEX(%s, \"^nepomuk:/res/\"^^xsd:string, \"i\"))\n\n"
    filterHard = ""

    getOptionalFields = True

    indentationLevel = 1

    lastSPARQLQuery = ""

    regExpOntologies = ("nie:url", "rdf:type")

    resultField = "?r"
    resultFieldSubqueries = resultField
    resultFieldOutput = "?id"

    resultsetLimit = 0
    resultsetOffset = 0

    searchForUrlsTooInBasicSearch = True

    sortCaseInsensitive = True
    sortSuffix = '_sort'

    stdoutQuery = False

    shortcuts = [ \
                    ['_nmm:actor->*',_('actor'), _('ac'), _("resources by actor")], \
                    ['_nmm:actor?->*', _('actors'), _('acs'), _("actors")], \
                    ['_nmm:actor<-nie:title', _('actorsmedia'), _('am'), _("actors in media title")], \
                    ['_nmm:actor<-nmm:series->nie:title', _('actorstvseries'), _('at'), _("actors in tv series")], \
                    ['_nmm:albumArtist->nco:fullname', _('albumartist'), _('aa'), _("albums by artist")], \
                    ['albums: nmm:musicAlbum<-contentcreated', _('albumyear'), _('ay'), _("album published year")], \
                    ['nmm:musicAlbum->nie:title', _('album'), _('al'), _("music pieces in album")], \
                    ['rdf:type=nmm:MusicAlbum->nie:title',_('albums'), _('als'), _("albums")], \
                    ['nao:altLabel', _('altlabel'), _('all'), _("alternative label")], \
                    ['_nmm:composer->*',_('composer'), _('co'), _("music pieces by composer")], \
                    ['_nmm:composer?->*', _('composers'), _('cos'), _("composers")], \
                    ['?ont->nco:fullname', _('contact'), _('co'), _("resources by contact")], \
                    ['rdf:type=nco:Contact->nco:fullname', _('contacts'), _('cos'), _("contacts")], \
                    ['nao:created', _('created'), _('cd'), _("created")], \
                    ['nie:contentCreated', _('contentcreated'), _('cc'), _("content created")], \
                    ['_nco:creator->*', _('creator'), _('cr'), _("resources by creator")], \
                    ['_nco:creator?->*', _('creators'), _('crs'), _("creators")], \
                    ['nfo:depiction<-nco:fullname', _('cdepictions'), _('cds'), _("contact depictions")], \
                    ['nao:description', _('description'), _('de'), _("description")], \
                    ['_nmm:director->*', _('director'), _('di'), _("resources by director")], \
                    ['_nmm:director?->*', _('directors'), _('dis'), _("directors")], \
                    ['_nmm:director<-nie:title', _('directorsmedia'), _('dm'), _("directors in media title")], \
                    ['_nmm:director<-nmm:series->nie:title', _('directorstvseries'), _('dt'), _("directors in tv series")], \
                    ['nmm:setNumber', _('discnumber'), _('dn'), _("music album disc number")], \
                    ['nfo:duration', _('duration'), _('du'), _("duration")], \
                    ['nmm:episodeNumber', _('episode'), _('ep'), _("tvshow episode number")], \
                    ['nexif:flash', _('flash'), _('fl'), _("photograph flash")], \
                    ['nco:fullname', _('fullname'), _('fn'), _("contact's fullname")], \
                    ['!nmm:genre', _('genre'), _('ge'), _("genre")], \
                    ['_nao:hasTag->nao:identifier', _('hastag'), _('ht'), _("tag name")], \
                    ['nfo:height', _('height'), _('he'), _("height")], \
                    ['kext:indexingLevel', _('indexinglevel'), _('il'), _("nepomuk indexing level")], \
                    ['rdf:type=nfo:RasterImage->nie:url', _('images'), _('ims'), _("images")], \
                    ['nao:isRelated<-nco:fullname', _('isrelated'), _('ir'), _("contact is related")], \
                    ['nexif:meteringMode', _('meteringmode'), _('mm'), _("photograph metering mode")], \
                    ['nie:mimeType', _('mimetype'), _('mt'), _("file mime type")], \
                    ['rdf:type=nmm:Movie->nie:title', _('movies'), _('mos'), _("movies")], \
                    ['rdf:type=nmm:MusicPiece->nie:title',_('musicpieces'),  _('mps'), _("music pieces")], \
                    ['nie:url', _('name'), _('na'), _("file urls")], \
                    ['nao:numericRating', _('numericrating'), _('nr'), _("rating")], \
                    ['_nmm:performer->*', _('performer'), _('pe'), _("music pieces by performer")], \
                    ['_nmm:performer?->*', _('performers'), _('pes'), _("performers")], \
                    ['nmm:musicAlbum=?vma->nmm:performer->nco:fullname',_('performeralbum'), _('pa'), _("albums by performer")], \
                    ['_nmm:producer->*', _('producer'), _('pr'), _("resources by producer")], \
                    ['_nmm:producer?->*', _('producers'), _('prs'), _("producers")], \
                    ['_nmm:producer<-nie:title', _('producersmedia'), _('pm'), _("producers in media title")], \
                    ['_nmm:producer<-nmm:series->nie:title', _('directorstvseries'), _('pt'), _("producers in tv series")], \
                    ['nco:photo<-nco:fullname', _('photos'), _('ps'), _("photographs")], \
                    ['nuao:usageCount', _('playcount'), _('pc'), _("media file play count")], \
                    ['nao:prefLabel', _('preflabel'), _('pl'), _("preferred label")], \
                    ['nao:numericRating', _('rating'), _('ra'), _("rating")], \
                    ['nie:contentCreated|nmm:releaseDate', _('released'), _('re'), _("released")], \
                    ['nie:contentCreated', _('contentcreated'), _('cc'), _("content created")], \
                    ['nmm:releaseDate', _('releasedate'), _('rd'), _("resource release data")], \
                    ['nexif:saturation', _('saturation'), _('sa'), _("photograph saturation")], \
                    ['nexif:sharpness', _('sharpness'), _('sh'), _("photograph sharpness")], \
                    ['nmm:season', _('season'), _('se'), _("tvshow season")], \
                    ['nmm:setNumber', _('setnumber'), _('sn'), _("music album disc number")], \
                    ['nao:identifier', _('tag'), _('ta'), _("tag name")], \
                    ['nfo:depiction<-nie:title', _('tdepictions'), _('tds'), _("tvseries depictions")], \
                    ['nie:title', _('title'), _('ti'), _("resource title")], \
                    ['nmm:trackNumber', _('tracknumber'), _('tn'), _("song track number")], \
                    ['_nco:topic->*',_('topic'), _('to'), _("resources by topic")], \
                    ['_nco:topic?->*', _('topics'), _('tos'), _("topics")], \
                    ['nmm:series->nie:title', _('tvserie'), _('ts'), _("tvshows by series")], \
                    ['rdf:type=nmm:TVSeries->nie:title', _('tvseries'), _('tvs'), _("tvseries")], \
                    ['_nmm:seriesr<-nmm:actor->nco:fullname', _('tvseriesactors'), _('tva'), _("tv series by actor")], \
                    ['_nmm:seriesr<-nmm:director->nco:fullname', _('tvseriesdirectors'), _('tvd'), _("tv series by director")], \
                    ['_nmm:seriesr<-nmm:producer->nco:fullname', _('tvseriesproducers'), _('tvp'), _("tv series by producer")], \
                    ['_nmm:seriesr<-nmm:writer->nco:fullname', _('tvserieswriters'), _('tvw'), _("tv series by writer")], \
                    ['nmm:series->nie:title', _('tvshow'), _('tv'), _("tvshows by title")], \
                    ['rdf:type=nmm:TVShow->nie:title', _('tvshows'), _('tvw'), _("tvshows")], \
                    ['!rdf:type', _('type'), _('ty'), _("resource type")], \
                    ['%nie:url', _('url'), _('ur'), _("file url")], \
                    ['nuao:usageCount', _('usagecount'), _('uc'), _("media file play count")], \
                    ['rdf:type=nfo:Video->nie:url', _('videos'), _('vis'), _("videos")], \
                    ['nfo:width', _('width'), _('wi'), _("width")], \
                    ['nexif:whiteBalance', _('whitebalance'), _('wb'), _("photograph white balance")], \
                    ['_nmm:writer->*', _('writer'), _('wr'), _("resources by writer")], \
                    ['_nmm:writer?->*', _('writers'), _('wrs'), _("writers")], \
                    ['_nmm:writer<-nie:title', _('writersmedia'), _('wm'), _("writers in media title")], \
                    ['_nmm:writer<-nmm:series->nie:title', _('writerstvseries'), _('wt'), _("writers in tv series")] \
                ]
    #(movies: and actor:"takeuchi") or nmm:series<-nmm:actor->nco:fullname:"takeuchi"

    tempData = ['', [], [], []] # Storage for temporal data.

    typeFilters = [] # To limit the results to only selected resource types.

    visibilityFilter = "" # Was removed since KDE 4.9.

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

            elif (self.tempData[0] in ("musicplayer", "playlist", "playmixed")):
                self.externalParameters = [self.tempData[0]]
                self.tempData = ['', [], [], []]

        if (self.tempData[0] == ''):
            if (self.columns == ""):
                columns = '%s AS %s' % (self.resultField, self.resultFieldOutput)

            else:
                columns = self.columns

        else:
            if (self.tempData[0].lower().find(" as ") < 0):
                columns = '%s AS %s' % (self.tempData[0], self.resultFieldOutput)

            else:
                columns = self.tempData[0]

        filterHard = self.filterHard
        if filterHard:
            filterHard = (self.filterHard % self.resultField)

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

        self.lastSPARQLQuery = header \
                                + subqueries \
                                + optionalFields \
                                + filterHard \
                                + footer \
                                + having \
                                + sort \
                                + limits

        if self.stdoutQuery:
            print toUtf8(self.lastSPARQLQuery)

        self.tempData = ['', [], [], []]

        return self.lastSPARQLQuery


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
        # Workaround for the precision problem.
        if (vartype(val) in ("str", "unicode")):
            val = round(float(val), precision)

        val = round(val, precision)
        adjustmentNumber = "0.%0" + "%sd1" % (precision - 1)
        adjustmentNumber = float(adjustmentNumber % 0)
        valMax = val + adjustmentNumber*9
        valMin = val - adjustmentNumber

        if (op in ("=", "==")):
            return "FILTER((?v >= %(valMin)s) and (?v < %(valMax)s)) ." % {'op': op, 'valMin': valMin, 'valMax': valMax}

        elif (op in (">", ">=")):
            return "FILTER(?v %(op)s %(val)s) ." % {'op': op, 'val': valMax}

        elif (op in ("<", "<=")):
            return "FILTER(?v %(op)s %(val)s) ." % {'op': op, 'val': valMin}

        elif (op == "!="):
            return "FILTER((?v < %(valMin)s) or (?v >= %(valMax)s)) ." % {'op': op, 'valMin': valMin, 'valMax': valMax}

        else:
            return ""


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


    def buildExpressionFilter(self, valType, operator, value, forceRegEx = False):
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

            filterExpression = self.buildFloatFilter(value, operator, 1)

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
                useRegEx = forceRegEx or not (("*" not in value) and (value[0] != "^") and (value[-1] != "$"))
                if useRegEx:
                    if (operator == "="):
                        filterExpression = "FILTER(REGEX(?v, \"%(val)s\"^^xsd:string, 'i')) ." % {'val': value}

                    elif (operator == "!="):
                        filterExpression = "FILTER(!REGEX(?v, \"%(val)s\"^^xsd:string, 'i')) ." % {'val': value}

                    else:
                        filterExpression = "FILTER(?v %(op)s \"%(val)s\"^^xsd:string) ." % {'op': operator, 'val': value}

                else:
                    if (operator == "="):
                        filterExpression = "FILTER(bif:contains(?v, \"'%(val)s'\")) ." % {'val': value}

                    elif (operator == "!="):
                        filterExpression = "FILTER(!bif:contains((?v, \"'%(val)s'\")) ." % {'val': value}

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
                if (ontology[0] not in ("?", "*")): # Especial: variable or all.
                    raise Exception("Unknown ontology <b>%s</b>." % ontology)

        return ontology


    def valuePreprocess(self, value = None, ontology = None):
        if (ontology == "rdf:type"):
            return value.replace("://", "@").replace(":", "#").replace("@", "://")

        return value


    def bsOptionalFields(self):
        if not self.getOptionalFields:
            return ""

        if (self.tempData[1] == []):
            fields = self.fields
            resultFieldSubqueries = self.resultFieldSubqueries

        else:
            fields = self.tempData[1]
            resultFieldSubqueries = self.tempData[0]
            if (self.tempData[0].lower().find(" as ") >= 0):
                resultFieldSubqueries = self.resultFieldSubqueries

        text = ""
        for item in fields:
            if not item[2]:
                continue

            try:
                text += "  optional { %(resultField)s %(ontology)s ?%(field)s . }\n" \
                            % {'resultField': resultFieldSubqueries, 'ontology': item[1], 'field': item[1].split(":")[1]}

            except:
                pass

        if (text != None):
            text += "\n"

        return text


    def bsHaving(self):
        return ''
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
                    if item[4]:
                        sortType = "ASC"

                    else:
                        sortType = "DESC"


                    columnName = "?" + item[1].split(":")[1]
                    if self.sortCaseInsensitive:
                        if (ontologyInfo(item[1])[2].lower() in ("string", "resource", "literal")):
                            sortText += "%s(bif:lower(%s)) " % (sortType, columnName)

                        else:
                            sortText += "%s(%s) " % (sortType, columnName)

                    else:
                        sortText += "%s(%s) " % (sortType, columnName)

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
            value = value.replace("'", "''")
            if (operator == "!="):
                strTerm += indent + "%s a ?v1 . FILTER NOT EXISTS {\n" % (self.resultFieldSubqueries)
                strTerm += indent2 + "{\n"
                strTerm += indent3 + "%s ?p1 ?v2 . FILTER(bif:contains(?v2, \"'%s'\")) .\n" % (self.resultFieldSubqueries, value)
                strTerm += indent2 + "} UNION {\n"
                strTerm += indent3 + "%s ?p2 [ ?p3 ?v2 ] . FILTER(bif:contains(?v2, \"'%s'\")) .\n" % (self.resultFieldSubqueries, value)
                strTerm += indent2 + "} .\n"
                strTerm += indent + "} .\n"

            elif (operator == "=="):
                strTerm += indent + "{\n"
                strTerm += indent2 + "%s ?p ?v . FILTER(?v = \"%s\"^^xsd:string) .\n" % (self.resultFieldSubqueries, value)
                strTerm += indent + "} UNION {\n"
                strTerm += indent2 + "%s ?p1 [ ?p2 ?v ] . FILTER(?v = \"%s\"^^xsd:string) .\n" % (self.resultFieldSubqueries, value)
                if self.searchForUrlsTooInBasicSearch:
                    strTerm += indent + "} UNION {\n"
                    strTerm += indent2 + "%s nie:url ?v . FILTER(?v = \"%s\"^^xsd:string) .\n" % (self.resultFieldSubqueries, value)

                strTerm += indent + "}\n"

            else:
                strTerm += indent + "{\n"
                strTerm += indent2 + "%s ?p ?v . FILTER(bif:contains(?v, \"'%s'\")) .\n" % (self.resultFieldSubqueries, value)
                strTerm += indent + "} UNION {\n"
                strTerm += indent2 + "%s ?p1 [ ?p2 ?v ] . FILTER(bif:contains(?v, \"'%s'\")) .\n" % (self.resultFieldSubqueries, value)
                if self.searchForUrlsTooInBasicSearch:
                    strTerm += indent + "} UNION {\n"
                    strTerm += indent2 + "%s nie:url ?v . FILTER(REGEX(?v, \"%s\"^^xsd:string, 'i')) .\n" % (self.resultFieldSubqueries, value)

                strTerm += indent + "}\n"

        else:
            # There are ontologies.
            ontologies = self.ontologyConversion(ontologies)
            ontologies = ontologies.split(" ")
            for ontologiesItem in ontologies:
                i = numInverseRelations = relationAdjustmentResource = relationAdjustmentValue = 0
                ontologyElements = re.split('->|<-', ontologiesItem)
                ontologyRelations = re.findall('->|<-', ontologiesItem)

                negationWithNotExists = False
                clause = ""
                fieldUsedAsResult = "?x%d " % 0
                firstOntology = None
                lastOntology = None
                filterToUse = None
                for ontology in ontologyElements:
                    ontology = self.ontologyConversion(ontology)
                    valType = ""
                    if (ontology[0] == "%"):
                        ontology = ontology[1:]
                        value = toN3(value)

                    elif (ontology[0] == "_"):
                        ontology = ontology[1:]
                        negationWithNotExists = negationWithNotExists or (operator == "!=")

                    elif (ontology[0] == "!"):
                        ontology = ontology[1:]
                        negationWithNotExists = negationWithNotExists or (operator == "!=")

                    elif ((value == "") and (operator == "!=")):
                        negationWithNotExists = True

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
                        # Inverse sample: { ?x1 ?ont1 ?r . ?x1 ?ont2 ?x2 . FILTER(REGEX(?x2, "text"^^xsd:string, 'i')) }
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

                        # ont1&ont2&ont3 must conveted in several clauses without UNION.
                        # ont1|ont2|ont3 must conveted in several clauses with UNION.
                        addUnion = ""
                        ontologyGroup = ontology.split("&")
                        if (len(ontologyGroup) <= 1):
                            ontologyGroup = ontology.split("|")
                            if (len(ontologyGroup) > 1):
                                addUnion = "UNION"

                        else:
                            if (len(ontology.split("|")) > 1):
                                raise Exception("Bad shortcut definition, shortcuts can't use \"|\" and \"&\" at the same time in \"%s\"." % ontology)

                        if (len(ontologyGroup) > 1):
                            valType = self.ontologyVarType(ontologyGroup[0])
                            filterToUse = self.buildExpressionFilter(valType, operator, self.valuePreprocess(value, ontologyGroup[0]), ontologyGroup[0] in self.regExpOntologies)
                            clause += "{\n"
                            clause += indent2 + "%(r)s %(ont)s %(v)s . %(f)s\n" % {'ont': ontologyGroup[0], 'r': rName, 'v': vName, 'f': filterToUse}
                            clause += indent + "} %s " % addUnion

                            for j in range(1, len(ontologyGroup)-1):
                                valType = self.ontologyVarType(ontologyGroup[j])
                                filterToUse = self.buildExpressionFilter(valType, operator, self.valuePreprocess(value, ontologyGroup[j]), ontologyGroup[j] in self.regExpOntologies)
                                clause += "{\n"
                                clause += indent2 + "%(r)s %(ont)s %(v)s . %(f)s\n" % {'ont': ontologyGroup[j], 'r': rName, 'v': vName, 'f': filterToUse}
                                clause += indent + "} %s " % addUnion

                            valType = self.ontologyVarType(ontologyGroup[-1])
                            filterToUse = self.buildExpressionFilter(valType, operator, self.valuePreprocess(value, ontologyGroup[-1]), ontologyGroup[-1] in self.regExpOntologies)
                            clause += "{\n"
                            clause += indent2 + "%(r)s %(ont)s %(v)s . %(f)s\n" % {'ont': ontologyGroup[-1], 'r': rName, 'v': vName, 'f': filterToUse}
                            clause += indent + "}"

                        else:
                            if (ontology == "*"):
                                # Text search in all resource ontologies.
                                # Sample: ?r nmm:performer [ ?p ?v ] .
                                clause += "%(r)s ?p %(v)s . " % {'ont': ontology, 'r': rName, 'v': vName}
                                
                            else:
                                clause += "%(r)s %(ont)s %(v)s . " % {'ont': ontology, 'r': rName, 'v': vName}

                        i += 1
                        if (firstOntology == None):
                            firstOntology = ontology

                        lastOntology = ontology

                clause = clause.replace(fieldUsedAsResult, self.resultFieldSubqueries + " ").replace("?x%d " % i, "?v ")
                if negationWithNotExists:
                    if (filterToUse == None):
                        strTerm = indent + self.resultFieldSubqueries + " %s ?v1 . FILTER NOT EXISTS {\n" % (firstOntology) \
                                + indent2 + clause + self.buildExpressionFilter(valType, "=", self.valuePreprocess(value, lastOntology), lastOntology in self.regExpOntologies) + "\n" \
                                + indent + "}\n"

                    else:
                        strTerm = indent + self.resultFieldSubqueries + " %s ?v1 . FILTER NOT EXISTS {\n" % (firstOntology) \
                                    + indent2 + clause + "\n" \
                                    + indent + "}\n"

                else:
                    if (filterToUse == None):
                        strTerm = indent + clause + self.buildExpressionFilter(valType, operator, self.valuePreprocess(value, lastOntology), lastOntology in self.regExpOntologies) + "\n"

                    else:
                        strTerm = indent + clause + "\n"

        return strTerm


    def bsSubquery(self, term, buildMethod = "none"):
        if (term[0] == "("):
            indent = "%%%ds" % (self.indentationLevel*2)
            subquery = (indent + "{\n") % ""
            self.indentationLevel += 1

        elif (term[0] == ")"):
            self.indentationLevel -= 1
            indent = "%%%ds" % (self.indentationLevel*2)
            subquery = ("\n" + indent + "}") % ""

        else:
            if (buildMethod in ("product", "union", "subquery")):
                localIndentation = 2

            else:
                localIndentation = 0

            strTerm = self.bsSubqueryTerm(term, self.indentationLevel + localIndentation)
            subquery = ""

            if (strTerm != ""):
                indent = "%%%ds" % (self.indentationLevel*2)
                indent2 = "%%%ds" % ((self.indentationLevel+1)*2)
                if (buildMethod == "union"):
                    subquery += "{\n"

                elif (buildMethod in ("product", "subquery")):
                    subquery += (indent + "{\n") % ("")

                else:
                    pass

                if (buildMethod in ("product", "union", "subquery")):
                    subquery += "\n"
                    subquery += (indent2 + "SELECT DISTINCT %s\n") % ("", self.resultFieldSubqueries)
                    subquery += (indent2 + "WHERE {\n\n") % ("")
                    subquery += strTerm + '\n'
                    subquery += (indent2 + "}\n") % ("")
                    subquery += "\n"
                    subquery += (indent + "}") % ("")

                else:
                    subquery += strTerm

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
        if (len(self.filters) < 2):
            #buildMethod = "none"
            buildMethod = "subquery"

        else:
            buildMethod = "subquery"

        unionClause = ""
        for term in self.filters:
            if (term[0] == "and"):
                buildMethod = "product"
                unionClause = ""

            elif (term[0] == "or"):
                buildMethod = "union"
                unionClause = " UNION "

            else:
                subquery = self.bsSubquery(term, buildMethod)
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

        if string[:3].lower() in ('e0 ', 'e1 '):
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
            commandLower = command.lower()
            if (commandLower not in ("--musicplayer", "--playlist", "--playmixed") and (commandLower[:6] != "--sort")):
                allFilters = []
                raise Exception(_("Syntax error, commands and queries are mutual exclude."))

        # ¿Es un comando?
        if (commandsFound >= 1):
            dummy = command.split(':')
            commandLower = dummy[0].lower()

            # Commands that don't support filters.
            if commandLower in ("--musicplayer", "--playlist", "--playmixed"):
                if (len(dummy) > 1):
                    raise Exception(_("Syntax error, command <b>%s</b> don't support an associated filter.") % commandLower)

                commandsFound -= 1

            # Sort command.
            elif (commandLower == "--sort"):
                if ((len(dummy) <= 1) or (dummy[1] == "")):
                    raise Exception(_("Syntax error, command <b>%s</b> needs at least an ontology as a parameter.") % commandLower)

                dummy = command[7:].split(',')

                self.fields = []
                i = 0
                for item in dummy:
                    item = item.strip()
                    if (item[0] in ("+", "-")):
                        ascending = (item[0] == "+")
                        item = item[1:]

                    else:
                        ascending = True

                    self.fields += [[i, item, True, True, ascending]]

                commandsFound -= 1
                commandLower = ""

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

            if (commandsFound > 1):
                raise Exception(_("Syntax error, only one command per query."))
            
            command = commandLower

        # Commands associated to queries.
        if ((len(allFilters) == 0) and (command in ("--musicplayer", "--playlist", "--playmixed", "--sort"))):
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

                    if value:
                        if bindingName == 'type':
                            value = os.path.basename(toUnicode(value))
                            value = value.split("#")
                            try:
                                value = '[' + value[1] + ']'

                            except:
                                value = value[0]

                        elif (value.split("://")[0] in ("file", "http", "https")):
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
