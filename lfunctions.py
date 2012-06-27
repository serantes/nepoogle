#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - functions library                                          *
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

import datetime, md5, os, re, subprocess, sys
from PyKDE4.kdecore import *

from PyQt4.QtCore import *
from PyKDE4.soprano import *
from PyKDE4.nepomuk import *

from lglobals import *

_ = gettext.gettext

#BEGIN lfunctions.py
# Program functions.
try:
    gSysEncoding = os.environ["LANG"].split(".")[1]

except:
    gSysEncoding = 'utf-8' # Forcing UTF-8.


def addLinksToText(text = ''):
    patter1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
    patter2 = re.compile(r"#(^|[\n ])(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

    text = patter1.sub(r'\1<a title="\2" href="\2" target="_blank">\3</a>', text)
    text = patter2.sub(r'\1<a title="http:/\2" href="http:/\2" target="_blank">\3</a>', text)

    return text


def dialogList(parameters = [], message = _("Select")):
    value = label = None

    if parameters != []:
        parameters = ["kdialog", "--title", PROGRAM_NAME, "--radiolist", message] \
                        + parameters
        dialogProcess = subprocess.Popen(parameters, stdout=subprocess.PIPE)
        dialogProcess.wait()
        value = toUnicode(dialogProcess.stdout.readline().strip())
        try:
            label = toUnicode(parameters[parameters.index(value) + 1])

        except:
            label = toUnicode(value)

    return value, label


def dialogInputBox(message = _("Text")):
    parameters = ["kdialog", "--title", PROGRAM_NAME, "--inputbox", message]
    dialogProcess = subprocess.Popen(parameters, stdout=subprocess.PIPE)
    dialogProcess.wait()
    return toUnicode(dialogProcess.stdout.readline().strip())


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


def getThumbnailUrl(url = ''):
    thumbName = md5.new(QFile.encodeName(KUrl(url).url())).hexdigest() + ".png"
    thumbPath = QDir.homePath() + "/.thumbnails/"
    result = thumbPath + "large/" + thumbName
    if not os.path.exists(result):
        result = thumbPath + "normal/" + thumbName
        if not os.path.exists(result):
            return None

    return "file://" + result


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


def QStringListToString(stringList = []):
    result = ''
    for item in stringList:
        if result != '':
            result += ', '

        result += toUnicode(item)

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


def toVariant(value):
    if ((vartype(value) != "QUrl") and (toUnicode(value).find("://") > 0)):
        value = QUrl(value)

    return Nepomuk.Variant(value)


def vartype(var):
    return type(var).__name__

#END lfunctions.py
