#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, os, re

from PyQt4.QtCore import *
from PyKDE4.soprano import *

#BEGIN lfunctions.py
# Program functions.

RDF_SCHEMA_RESOURCE = 'http://www.w3.org/2000/01/rdf-schema#Resource'

knownOntologies = [ \
                    ['nao', '2007/08/15'], ['ncal', '2007/04/02'], \
                    ['nco', '2007/03/22'], ['nexif', '2007/05/10'], \
                    ['nfo', '2007/03/22'], ['nid3', '2007/05/10'], \
                    ['nie', '2007/01/19'], ['nmm', '2009/02/19'], \
                    ['nmo', '2007/03/22'], ['nrl', '2007/08/15'], \
                    ['pimo', '2007/11/01'], ['tmo',  '2008/05/20'] \
                ]

gSysEncoding = 'utf-8' # Change this for a detection system.


def addLinksToText(text = ''):
    patter1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
    patter2 = re.compile(r"#(^|[\n ])(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

    text = patter1.sub(r'\1<a title="\2" href="\2" target="_blank">\3</a>', text)
    text = patter2.sub(r'\1<a title="http:/\2" href="http:/\2" target="_blank">\3</a>', text)

    return text


def fileExists(fileName = ''):
    if fileName == '':
        return False

    fileName = toUnicode(fileName)
    if fileName[:7] == 'file://':
        return os.path.exists(fileName[7:])

    else:
        return os.path.exists(fileName)


def formatDate(string = '', pack = False):
    result = datetime.datetime.strptime(string[:19], "%Y-%m-%dT%H:%M:%S")
    result = datetime.datetime.strftime(result, '%x')
    return result


def formatDateTime(string = '', pack = False):
    result = datetime.datetime.strptime(string[:19], "%Y-%m-%dT%H:%M:%S")
    if pack and result.day == 1 and result.month == 1 and (result.hour + result.minute + result.second) == 0:
        result = datetime.datetime.strftime(result, '%Y')

    else:
        result = datetime.datetime.strftime(result, '%x %X')

    return result


def fromPercentEncoding(url = ''):
    qurl = QUrl()
    qurl.setEncodedUrl(toUtf8(url))
    qurl.setEncodedUrl(toUtf8(qurl.toString()))
    qurl.setEncodedUrl(toUtf8(qurl.toString()))
    return toUnicode(qurl.toString())


def iif(condition = True, value = '', optionalValue = ''):
    return value if condition else optionalValue


def lindex(items, value, column = None):
    try:
        if vartype(items[0]) != 'list':
            column = None

        if column == None:
            result = next((i for i, element in enumerate(items) if value in element), None)

        else:
            result = next((i for i, element in enumerate(items) if value == element[column]), None)

    except:
        result = None

    return result


def lvalue(items, value, searchColumn = 0, valueColumn = 0):
    try:
        value = items[lindex(items, value, searchColumn)][valueColumn]

    except:
        value = None

    return value


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
    result = ''
    if ontology == '':
        return result

    return os.path.basename(toUnicode(ontology)).replace('#', ':').replace('rdf-schema:', 'rdfs:')



def ontologyToHuman(ontology = '', reverse = False):
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


def QStringListToString(stringList = []):
    result = ''
    for item in stringList:
        if result != '':
            result += ', '

        result += toUnicode(item)

    return result


def toN3(url = ''):
    if url[0] == '^':
        result = '^' + QUrl(url[1:]).toEncoded()

    else:
        result = QUrl(url).toEncoded()

    return result


def toPercentEncoding(url = ''):
    return QUrl.toPercentEncoding(url)


def toUtf8(string):
    try:
        if vartype(string) == 'QString':
            return string.toUtf8() # REVISAR: Esto no es coherente con el resto.

        else:
            return string.encode(gSysEncoding)

    except:
        return string


def toUnicode(string):
    try:

        if vartype(string) == 'QString':
            return unicode(str(string.toUtf8()), gSysEncoding)

        if vartype(string) == 'unicode':
            return string

        return unicode(string, gSysEncoding)

    except:
        return string


def vartype(var):
    return type(var).__name__

#END lfunctions.py
