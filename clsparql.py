#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   cSparqlBuilder - a SPARQL query builder                               *
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

import gettext, time

from PyQt4.QtCore import *
from PyKDE4.nepomuk import *
from PyKDE4.soprano import *

from PyQt4.QtGui import *

from lfunctions import *

gettext.bindtextdomain("nepoogle", '') #'/path/to/my/language/directory')
gettext.textdomain("nepoogle")
_ = gettext.gettext

#BEGIN clsparql.py
#
# cSparqlBuilder class
#
RDF_SCHEMA_RESOURCE = 'http://www.w3.org/2000/01/rdf-schema#Resource'

knownOntologies = [ \
                    ['nao', '2007/08/15'], ['ncal', '2007/04/02'], \
                    ['nco', '2007/03/22'], ['nexif', '2007/05/10'], \
                    ['nfo', '2007/03/22'], ['nid3', '2007/05/10'], \
                    ['nie', '2007/01/19'], ['nmm', '2009/02/19'], \
                    ['nmo', '2007/03/22'], ['nrl', '2007/08/15'], \
                    ['pimo', '2007/11/01'], ['tmo',  '2008/05/20'] \
                ]

ontologiesInfo = []

def NOC(name = '', returnQUrl = False):
    ontology, property = name.strip().split(':')
    date = lvalue(knownOntologies, ontology, 0, 1)
    if date != None:
        value = 'http://www.semanticdesktop.org/ontologies/%s/%s#%s' % (date, ontology, property)

    else:
        value = 'Soprano.Vocabulary.%s.%s().toString()' % (ontology.upper(), property)
        try:
            value = eval(value)

        except:
            value = ''

    if returnQUrl:
        return QUrl(value)

    else:
        return value


def NOCR(ontology = ''):
    if ontology == '':
        return ""
        
    return os.path.basename(toUnicode(ontology)).replace('#', ':').replace('rdf-schema:', 'rdfs:')


def ontologyToHuman(ontology = '', reverse = False):
    #TODO: En la propia base de datos está esta información. Ejemplo:
    #select *
    #where {
        #nao:lastModified rdfs:label ?v
    #}
    #Resultado: "last modified at"
    result = ''
    if ontology == '':
        return result

    try:
        ontology = ontology.split(':')[1]

    except:
        pass

    if ontology == '':
        return result

    result += ontology[0].upper()
    for i in range(1, len(ontology)):
        if ontology[i] == ontology[i].upper():
            result += ' ' + ontology[i].lower()

        else:
            result += ontology[i]

    if reverse:
        if result == 'Creator':
            result = 'Is creator of'

        elif result == 'Has tag':
            result = 'Is tag of'

        elif result == 'Performer':
            result = 'Is performer of'

        elif result == 'Series':
            result = 'Episodes'

    return result


def ontologyInfo(ontology = '', model = None):
    global ontologiesInfo
    
    if (ontology == ""):
        return ["", "", ""]

    if (model == None):
        model = Nepomuk.ResourceManager.instance().mainModel()

    shortOnt = NOCR(ontology)
    i = lindex(ontologiesInfo, shortOnt, column = 0)
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
                    "\t<%(ont)s> rdfs:range ?range\n" \
                    "\tOPTIONAL { <%(ont)s> rdfs:label ?label . }\n" \
                "}" % {"ont": ontology}
        data = model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        if data.isValid():
            while data.next():
                if shortOnt == "nie:contentSize":
                    ontType = "size"

                else:
                    ontType = toUnicode(data["range"].toString()).split("#")[1]

                ontologiesInfo += [[shortOnt, toUnicode(data["label"].toString()), ontType]]

        i = -1

    return [ontologiesInfo[i][0], ontologiesInfo[i][1], ontologiesInfo[i][2]]




def toN3(url = ''):
    if url[0] == '^':
        result = '^' + QUrl(url[1:]).toEncoded()

    else:
        result = QUrl(url).toEncoded()

    return result


class cSparqlBuilder():

    _private_main_header = \
                            "SELECT DISTINCT %s\n" \
                            "WHERE {\n\n"
    _private_main_footer = "}\n"

    caseInsensitiveSort = True
    #columns = '*'
    # ?x0+>prefLabel ?x0*>url + si * opcional
    #columns = '?url ?title AS ?label ?prefLabel ?fullname ?altlabel min(?type) AS ?type'
    columns = '?url ?title ?prefLabel ?fullname ?altLabel'
    command = ''
    # [id, ['columns', [[id, 'ontology', optional, sort]...], [bsTypeFilter], [bsIndividualFilter]]]
    commands = [ \
                [_('--actors'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nmm:actor->nco:fullname'], ['nmm:actor->nco:fullname']]], \
                [_('--albums'), ['?x0 AS ?id ?url ?title', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['rdf:type=nmm:MusicAlbum'], ['nie:title']]], \
                [_('--audios'), ['?x0 AS ?id ?url ?title', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['rdf:type=nfo:Audio'], ['nie:title']]], \
                #[_('--connect'), ['', [], [], []]], \
                [_('--composers'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nco:composer->nco:fullname'], ['nco:composer->nco:fullname']]], \
                [_('--contacts'), ['?x0 AS ?id ?fullname', [[0, 'nco:fullname', True, True]], ['rdf:type=nco:Contact'], ['nco:fullname']]], \
                [_('--creators'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nco:creator->nco:fullname'], ['nco:creator->nco:fullname']]], \
                #[_('--daemonize'), ['', [], [], []]], \
                [_('--directors'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nmm:director->nco:fullname'], ['nmm:director->nco:fullname']]], \
                #[_('--disconnect'), ['', [], [], []]], \
                [_('--genres'), ['\'ont://nmm:genre\' AS ?id ?x1 AS ?genre', [[0, 'nco:genre', True, False]], ['nmm:genre'], ['nmm:genre']]], \
                [_('--help'), ['help', [], [], []]], \
                [_('--images'), ['?x0 AS ?id ?url ?title', [[0, 'nie:url', True, True], [1, 'nie:title', True, True]], ['rdf:type=nfo:RasterImage'], ['nie:url']]], \
                [_('--movies'), ['?x0 AS ?id ?url ?title', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['rdf:type=nmm:Movie'], ['nie:title']]], \
                [_('--musicpieces'), ['?x0 AS ?id ?url ?title', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['rdf:type=nmm:MusicPiece'], ['nie:title']]], \
                [_('--performers'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nmm:performer->nco:fullname'], ['nmm:performer->nco:fullname']]], \
                [_('--producers'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nmm:producer->nco:fullname'], ['nmm:producer->nco:fullname']]], \
                [_('--quit'), ['quit', [], [], []]], \
                [_('--tags'), ['?x0 AS ?id ?prefLabel ?altLabel', [[0, 'nao:prefLabel', True, True], [2, 'nao:altLabel', True, True]], ['rdf:type=nao:Tag'], ['rdf:type=nao:Tag->nao:identifier']]], \
                [_('--tvseries'), ['?x0 AS ?id ?url ?title', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['rdf:type=nmm:TVSeries'], ['nie:title']]], \
                [_('--tvshows'), ['?x0 AS ?id ?url ?title', [[0, 'nie:url', True, True], [1, 'nie:title', True, True]], ['rdf:type=nmm:TVShow'], ['nie:title']]], \
                [_('--videos'), ['?x0 AS ?id ?url ?title', [[0, 'nie:title', True, True], [1, 'nie:url', True, True]], ['rdf:type=nfo:Video'], ['nie:title']]], \
                [_('--writers'), ['?x1 AS ?id ?fullname', [[0, 'nco:fullname', True, False]], ['nmm:writer->nco:fullname'], ['nmm:writer->nco:fullname']]] \
            ]

    engine = 0 # 0- Nepomuk.QueryParse(), 1- v1, 2- v2
    
    #fields = [[0, 'rdf:type', True], [1, 'nao:identifier', True], [2, 'nie:url', True], [3, 'nie:title', False], [4, 'nao:prefLabel', False],
    #            [5, 'nao:description', False], [6, 'nao:numericRating', False]]
    # 'nmm:genre', 'nmm:releaseDate', ''
    fields = [ \
                [0, 'nie:url', True, True], \
                [1, 'nie:title', True, True], \
                [2, 'nao:prefLabel', True, True], \
                [3, 'nco:fullname', True, True], \
                [4, 'nao:altLabel', True, True] \
            ]
    filters = []

    getAllFields = True
    #ontologyFilters = ['_nao:description', '_nao:identifier', '/nie:url', 'nao:hasTag->$nao:identifier', '%nie:plainTextContent']
    #ontologyFilters = ['_nao:description', '_nao:identifier', '_nie:url', 'nao:hasTag->$nao:identifier']
    ontologyFilters = ['nao:description', '%nao:identifier', '%nie:url', 'nao:hasTag->%nao:identifier', 'nco:fullname', 'nie:title']
    # All in lowercase so search in lowercase.
    #TODO: esta información, en forma básica, está en la base de datos. Ejemplo:
    #select *
    #where {
    #    nao:lastModified rdfs:range ?v
    #}
    #resultado: <http://www.w3.org/2001/XMLSchema#dateTime>
    ontologyTypes = [ \
                        ['nao:created', 'datetime'], \
                        ['nao:lastmodified', 'datetime'], \
                        ['nao:numericrating', 'number'], \
                        ['nfo:averagebitrate', 'number'], \
                        ['nfo:duration', 'seconds'], \
                        ['nfo:height', 'number'], \
                        ['nfo:samplerate', 'number'], \
                        ['nfo:width', 'number'], \
                        ['nie:contentcreated', 'datetimep'], \
                        ['nie:contentsize', 'size'], \
                        ['nie:lastmodified', 'datetime'], \
                        ['nmm:episodenumber', 'number'], \
                        ['nmm:releasedate', 'datep'], \
                        ['nmm:season', 'number'], \
                        ['nmm:setnumber', 'number'], \
                        ['nmm:tracknumber', 'number'], \
                        ['nuao:usagecount', 'number'] \
                    ]
    shortcuts = [ \
                    #TODO: singulares y plurales para todo
                    ['_nmm:actor->nco:fullname',_('actor'),  _('ac')], \
                    #TODO: fix actors shortcut
                    #['nmm:actor->nco:fullname', _('actors', _('acs'], \
                    #  optional { ?x0 nmm:actor ?x00 . ?x00 nco:fullname ?fullname . }
                    #  HAVING (REGEX(?fullname, '', 'i'))
                    ['nmm:musicAlbum->nie:title', _('album'), _('al')], \
                    ['rdf:type=nmm:MusicAlbum->nie:title',_('albums'), _('als')], \
                    ['nao:altLabel', _('altlabel'), _('all')], \
                    ['_nmm:composer->nco:fullname', _('composer'), _('cm')], \
                    ['?ont->nco:fullname', _('contact'), _('co')], \
                    ['rdf:type=nco:Contact->nco:fullname', _('contacts'), _('cos')], \
                    ['_nco:creator->nco:fullname', _('creator'), _('cr')], \
                    ['nao:description', _('description'), _('de')], \
                    ['_nmm:director->nco:fullname', _('director'), _('di')], \
                    ['nmm:setNumber', _('discnumber'), _('dn')], \
                    ['nmm:episodeNumber', _('episode'), _('ep')], \
                    ['nco:fullname', _('fullname'), _('fn')], \
                    ['nmm:genre', _('genre'), _('ge')], \
                    ['_nao:hasTag->%nao:identifier', _('hastag'), _('ht')], \
                    ['nfo:height', _('height'), _('height')], \
                    ['nie:mimeType', _('mimetype'), _('mt')], \
                    ['rdf:type=nmm:MusicPiece->nie:title',_('musicpieces'),  _('mps')], \
                    ['rdf:type=nmm:Movie->nie:title', _('movies'), _('mos')], \
                    ['nie:url', _('name'), _('na')], \
                    ['nao:numericRating', _('numericrating'), _('nr')], \
                    ['_nmm:performer->nco:fullname', _('performer'), _('pe')], \
                    ['_nmm:producer->nco:fullname', _('producer'), _('pr')], \
                    ['nuao:usageCount', _('playcount'), _('pc')], \
                    ['nao:prefLabel', _('preflabel'), _('pl')], \
                    ['nao:numericRating', _('rating'), _('ra')], \
                    ['nmm:season', _('season'), _('se')], \
                    ['nmm:setNumber', _('setnumber'), _('sn')], \
                    ['nao:identifier', _('tag'), _('ta')], \
                    ['nie:title', _('title'), _('ti')], \
                    ['nmm:trackNumber', _('tracknumber'), _('tn')], \
                    ['nmm:series->nie:title', _('tvserie'), _('ts')], \
                    ['rdf:type=nmm:TVSeries->nie:title', _('tvseries'), _('tvs')], \
                    ['nmm:series->nie:title', _('tvshow'), _('tv')], \
                    ['rdf:type', _('type'), _('ty')], \
                    ['%nie:url', _('url'), _('ur')], \
                    ['nuao:usageCount', _('usagecount'), _('uc')], \
                    ['nfo:width', _('width'), _('wi')], \
                    ['_nmm:writer->nco:fullname', _('writer'), _('wr')] \
                ]

    tempData = ['', [], [], []]

    #typeFilters = ['nao#Tag', 'nfo#FileDataObject']
    typeFilters = []

    resultsetLimit = 0
    resultsetOffset = 0

    sortSuffix = '_sort'
    stdoutQuery = False

    visibilityFilter = "nao:userVisible 1 ."

    warningsList = []
    

    def __init__(self):
        pass


    def __del__(self):
        pass


    def buildQuery(self, searchString = ''):
        if ((self.command == '') and (self.filters == []) and (searchString != '')):
            self.filters = self.stringQueryConversion(searchString.strip())

        command = self.command.strip().lower()
        if command == '':
            pass

        else:
            idx = lindex(self.commands, command, 0)
            if idx >= 0:
                if self.commands[idx][1][0] == '':
                    raise Exception("Sorry, command \"%s\" not implemented yet." % self.command)

                else:
                    self.tempData = self.commands[idx][1]

            else:
                raise Exception("Unknown command \"%s\", try \"--help\" command." % self.command)

            # La ayuda tiene tratamiento especial
            if self.tempData[0] == 'help':
                raise Exception(self.tempData[0])

        if self.tempData[0] == '':
            columns = self.columns

        else:
            columns = self.tempData[0]

        footer = self._private_main_footer
        having = self.bsHaving()
        sort, sortColumns = self.bsSort()
        limits = self.bsResulsetLimits()

        columns += sortColumns
        header = self._private_main_header % columns

        mainFilter = self.bsMainFilter() + '\n'
        if self.getAllFields:
            fields = self.bsFields() + '\n'

        else:
            fields = ''

        searchFilter = self.bsFilter() + '\n'

        query = header \
                + mainFilter \
                + fields \
                + searchFilter \
                + footer \
                + having \
                + sort \
                + limits

        if self.stdoutQuery:
            print toUtf8(query)

        self.tempData = ['', [], [], []]

        return query


    def bsFields(self):
        if self.tempData[1] == []:
            fields = self.fields

        else:
            fields = self.tempData[1]

        text = ""
        for item in fields:
            if not item[3]:
                continue

            try:
                text += "  optional { ?x0 %(ontology)s ?%(field)s . }\n" \
                            % {'ontology': item[1], 'field': item[1].split(":")[1]}

            except:
                pass

        return text


    def ontologyConversion(self, ontology = ''):
        ont = ontology.strip().lower()

        if ont == '':
            ontology = ''

        elif ont.find(':') > 0:
            pass

        else:
            idx = lindex(self.shortcuts, ont, 1)
            if idx == None:
                # Miramos en las abreviaturas.
                idx = lindex(self.shortcuts, ont, 2)

            if idx >= 0:
                ontology = self.shortcuts[idx][0]

            else:
                raise Exception("Unknown ontology \"%s\"." % ontology)

        return ontology


    def bsIndividualFilter(self, value = ''):
        ontologies = [self.ontologyConversion(value[2])]
        if ontologies == ['']:
            if self.tempData[3] == []:
                ontologies = self.ontologyFilters

            else:
                ontologies = self.tempData[3]

        text = ""
        for item in ontologies:
            textAux = ""
            ontologyElements = item.split("->")
            i = 0
            optionalUsage = False
            for ontology in ontologyElements:
                ontology = ontology.strip()

                try:
                    val = value[0]

                except:
                    val = ""

                try:
                    operator = value[1]
                    if operator == '':
                        operator = '='

                except:
                    operator = '='

                valType = ""
                if ontology[0] == '%':
                    ontology = ontology[1:]
                    val = toN3(val)

                elif ontology[0] == '_':
                    ontology = ontology[1:]
                    optionalUsage = optionalUsage or (operator == '!=')

                valType = self.ontologyVarType(ontology)
                #optionalUsage = (optionalUsage and (operator == '!='))
                if not optionalUsage:
                    if ontology.find('=') >= 0:
                        textAux += "?x%(v1)s %(ont)s %(v2)s . " % {'ont': ontology.split('=')[0], 'v1': i, 'v2': ontology.split('=')[1]}

                    else:
                        textAux += "?x%(v1)s %(ont)s ?x%(v2)s . " % {'ont': ontology, 'v1': i, 'v2': i + 1}
                        i += 1

            if val == '':
                filterExpression = '}\n'

            else:
                # Sometimes " character must be removed.
                if val[0] == val[-1] == '"':
                    val = val[1:-1]

                if valType == 'number':
                    filterExpression = "FILTER(?x%(v2)s %(op)s %(val)s) }\n" % {'v2': i, 'op': operator, 'val': val}

                else:
                    if operator == '==':
                        filterExpression = "FILTER(?x%(v2)s %(op)s \"%(val)s\"^^xsd:string) }\n" % {'v2': i, 'op': "=", 'val': val}

                    elif operator == '=':
                        filterExpression = "FILTER(REGEX(?x%(v2)s, \"%(val)s\"^^xsd:string, 'i')) }\n" % {'v2': i, 'val': val.replace('(', '\\\(').replace(')', '\\\)')}

                    elif operator == '!=':
                        if optionalUsage:
                            filterExpression = "?x%(v1)s %(ontbase)s ?x%(v2)s . optional { ?x%(v2)s %(ont)s ?x%(v3)s . FILTER(!REGEX(?x%(v3)s, \"%(val)s\"^^xsd:string, 'i')) } FILTER(!BOUND(?x%(v3)s)) }\n" \
                                                    % {'v1': i, 'v2': i+1, 'v3': i+2, 'val': val.replace('(', '\\\(').replace(')', '\\\)'), 'ontbase': ontologyElements[0][1:], 'ont': ontology}

                        else:
                            filterExpression = "FILTER(!REGEX(?x%(v2)s, \"%(val)s\"^^xsd:string, 'i')) }\n" % {'v2': i, 'val': val.replace('(', '\\\(').replace(')', '\\\)')}

                    else:
                        filterExpression = "FILTER(?x%(v2)s %(op)s \"%(val)s\"^^xsd:string) }\n" % {'v2': i, 'op': operator, 'val': val}

            if optionalUsage:
                        #"      }\n" \
                        #"    ))\n" \
                        #"    &&\n" \
                textAux = \
                        "    (!bif:exists ((\n" \
                        "      SELECT *\n" \
                        "      WHERE {\n" \
                        "        { " + textAux + filterExpression

            else:
                if text != "":
                    text += "      UNION\n"
                    textAux = "        { " + textAux + filterExpression

                else:
                    textAux = "    (bif:exists ((\n" \
                                "      SELECT *\n" \
                                "      WHERE {\n" \
                                "        { " + textAux + filterExpression

            text += textAux

        if text != "":
            if text[0] == '!':
                text += \
                            "      }\n" \
                        "    )))\n" \

            else:
                text = \
                                    "%(text)s" \
                            "      }\n" \
                        "    )))\n" \
                        % {'text': text}

        return text


    def bsFilter(self):
        filters = self.filters
        text = ""
        for item in filters:
            if item == []:
                continue

            if item[0].lower() == 'or':
                text += '    ||\n'

            elif item[0].lower() == 'and':
                text += '    &&\n'

            else:
                if text != "" and text[-2] == ')':
                    text += '    &&\n'
                text += self.bsIndividualFilter(item)

        if text != "":
            text = \
                    "  FILTER(\n" \
                        "%s" \
                    "  )\n" \
                    % text

        return text


    def bsHaving(self):
        return '\n'
        #return "HAVING !(?type = <http://www.w3.org/2000/01/rdf-schema#Resource>)\n"
        #return "HAVING (?type = <http://www.w3.org/2000/01/rdf-schema#Resource>)\n"
        #return "GROUP BY (?x0)\n"


    def bsSort(self):
        if self.tempData[1] == []:
            fields = self.fields

        else:
            fields = self.tempData[1]

        sortText = ""
        sortColumns = ""
        for item in fields:
            if item[2]:
                try:
                    columnName = "?" + item[1].split(":")[1]
                    sortText += columnName
                    if self.caseInsensitiveSort:
                        sortColumns += " bif:lower(%s) AS %s%s " % (columnName, columnName, self.sortSuffix)
                        sortText += self.sortSuffix + ' '

                    else:
                        sortText += ' '

                except:
                    pass

        if sortText != "":
            sortText = "ORDER BY " + sortText + "\n"

        return sortText, sortColumns


    def bsMainFilter(self):
        text = ""
        if self.tempData[2] == []:
            typeFilters = self.typeFilters

        else:
            typeFilters = self.tempData[2]

        if len(typeFilters) == 1:
            items = typeFilters[0].split("->")
            if len(items) > 1:
                i = 0
                text = ''
                #oldVarName = 'x0'
                for item in items:
                    if item != '':
                        if self.visibilityFilter != '':
                            text += "  ?x%s %s\n" % (i, self.visibilityFilter)

                        if item == items[-1]:
                            varName = '%s' % (item.split(':')[-1])

                        else:
                            varName = 'x%s' % (i+1)

                        text += "  ?x%(oldVarName)s %(ontology)s ?%(varName)s .\n" \
                                % {'oldVarName': i, 'varName': varName, 'ontology': item}
                        #oldVarName = varName
                        i += 1

            else:
                if self.visibilityFilter != '':
                    text += "  ?x0 %s\n" % (self.visibilityFilter)
                                    
                items = typeFilters[0].split("=")
                if len(items) > 1:
                    text += "  ?x0 %(ontology1)s %(ontology2)s .\n" \
                            % {'ontology1': items[0], 'ontology2': items[1]}

                else:
                    text += "  ?x0 %(ontology)s ?x1 .\n" \
                            % {'ontology': items[0]}

        else:
            #TODO: cambiar el rdf:type igual que arriba.
            for item in typeFilters:
                if text != '':
                    text += '        UNION\n'
                text += '        { ?x0 rdf:type %s . }\n' % item

            if text != "":
                if self.visibilityFilter != '':
                    text += "  ?x0 %s\n" % (self.visibilityFilter)
                    
                else:
                    text = ""

                text += \
                        "  ?x0 rdf:type ?type .\n" \
                        "  FILTER(\n" \
                            "    bif:exists ((\n" \
                                "      SELECT *\n" \
                                "      WHERE {\n" \
                                "%s" \
                                "      }\n" \
                            "    ))\n" \
                        "  )\n" \
                        % text

            else:
                if self.visibilityFilter != '':
                    text = "  ?x0 %s\n" % (self.visibilityFilter)

                else:
                    text = ""

                text += \
                        "  ?x0 rdf:type ?type .\n" \

        return text


    def bsResulsetLimits(self):
        text = ''
        if self.resultsetLimit > 0:
            text += "LIMIT %s\n" % self.resultsetLimit

        if self.resultsetOffset > 0:
            text += "OFFSET %s" % self.resultsetOffset

        return text


    def addField(self, name = ''):
        pass


    def removeField(self, name = '', logop = ''):
        pass


    def addFilter(self, name = ''):
        pass


    def removeFilter(self, name = ''):
        pass


    def addOntologyFilter(self, name = ''):
        pass


    def removeOntologyFilter(self, name = ''):
        pass


    def addTypeFilter(self, name = ''):
        pass


    def removeTypeFilter(self, name = ''):
        pass


    def setOrder(self, orderList = []):
        pass


    def ontologyVarType(self, ontology = ''):
        return lvalue(self.ontologyTypes, ontology.lower().strip(), 0, 1)


    def split(self, string = ''):
        #print string
        specialChars = [":", "+", "-", ">", "<", "="]
        results = []
        if string != '':
            breakChar = ' '
            newItem = True
            for i in range(0, len(string)):
                #print breakChar, string[i], results
                if string[i] == breakChar:
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

                if newItem and ((results == []) or (results[-1] != '')):
                    results += ['']
                    newItem = False

                results[-1] += string[i]

        for result in results:
            if result != "" and result[0] == "-" and result[1] != "-":
                i = lindex(self.warningsList, "BUG001", 0)

                if i != None:
                    self.warningsList[i] += [result]

                else:
                    self.warningsList = [["BUG001", result]]

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

        commandFound = False
        addAnd = False
        for item in items:
            if item[:2] == '--':
                commandFound = True
                oneFilter = [item, '', '']

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

                if operator == '-':
                    operator = '!='
                    data = data[1:]

                elif operator == '+':
                    operator = '=='
                    data = data[1:]

                elif operator == '>':
                    operator = data[1]
                    if operator == '=':
                        operator = '>='
                        data = data[2:]

                    else:
                        operator = '>'
                        data = data[1:]

                elif operator == '<':
                    operator = data[1]
                    if operator == '=':
                        operator = '<='
                        data = data[2:]

                    else:
                        operator = '<'
                        data = data[1:]

                else:
                    operator = '='

                if (data[0] == data[-1] == '"') or (data[0] == data[-1] == "'"):
                    data = data[1:-1]

                oneFilter = [data, operator, ontology]
                addAnd = True

            allFilters += [oneFilter]

        # Check basic errors.
        if allFilters[len(allFilters)-1][0] == 'and' or allFilters[len(allFilters)-1][0] == 'or':
            allFilters = []
            raise Exception(_("Syntax error, please check your search text."))

        if (commandFound and (len(allFilters) > 1)):
            allFilters = []
            raise Exception(_("Syntax error, commands and queries are mutual exclude."))

        # ¿Es un comando?
        if ((len(allFilters) == 1) and (allFilters[0][0][:2] == "--")):
            dummy = allFilters[0][0].split(':')
            self.command = dummy[0]
            if ((len(dummy) > 1) and (dummy[1] != "")):
                if dummy[1][0] == '-':
                    allFilters = [[dummy[1][1:], '!=', '']]

                elif dummy[1][0] == '+':
                    allFilters = [[dummy[1][1:], '==', '']]

                else:
                    allFilters = [[dummy[1], '=', '']]

            else:
                allFilters = []

        return allFilters


    def executeQuery(self, query = []):
        model = Nepomuk.ResourceManager.instance().mainModel()

        queryTime = time.time()
        result = model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        queryTime = time.time() - queryTime

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
