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

import datetime, md5, os, re, subprocess, sys, tempfile

from PyQt4.QtCore import *
from PyKDE4.kdecore import KUrl
from PyKDE4.kdeui import KMessageBox
from PyKDE4.nepomuk2 import Nepomuk2
from PyKDE4.soprano import Soprano

from lglobals import *

_ = gettext.gettext

#BEGIN lfunctions.py
# Program functions.
gSysEncoding = SYSTEM_ENCODING


class stderrReader():
    tmpFile = None
    old_stderr = None
    stderrValue = ""

    def __init__(self):
        self.tmpFile = tempfile.TemporaryFile()
        self.old_stderr = sys.stderr
        self.old_stderr.flush()
        sys.stderr = self.tmpFile


    def __exit__(self, exc_type, exc_value, traceback):
        if (self.old_stderr != None):
            sys.stderr.flush()
            sys.stderr = self.old_stderr


    def read(self):
        if (self.old_stderr != None):
            sys.stderr.flush()
            sys.stderr = self.old_stderr
            self.old_stderr = None

            self.tmpFile.seek(0)
            self.stderrValue = self.tmpFile.read()
            self.tmpFile.close()

        return self.stderrValue


def addBS(path = '.'):
    path = path.strip()
    if path == '':
        return ''

    else:
        if path[-1] == '/':
            return path
        else:
            return path + '/'


def addLinksToText(text = ''):
    patter1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
    patter2 = re.compile(r"#(^|[\n ])(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

    text = patter1.sub(r'\1<a title="\2" href="\2" target="_blank">\3</a>', text)
    text = patter2.sub(r'\1<a title="http:/\2" href="http:/\2" target="_blank">\3</a>', text)

    return text


def dialogInputBox(message = _("Text"), ontType = "string"):
    if (ontType == "date"):
        parameters = ["zenity", "--calendar", "--title=" + PROGRAM_NAME, "--text=" + message, "--date-format=%Y-%m-%d"]

    else:
        parameters = ["kdialog", "--title", PROGRAM_NAME, "--inputbox", message]

    try:
        dialogProcess = subprocess.Popen(parameters, stdout=subprocess.PIPE)
        dialogProcess.wait()
        value = u""
        for line in iter(dialogProcess.stdout.readline, ''):
            value += toUnicode(line)

        # Cleaning last "\n".
        if (value[-1] == "\n"):
            value = value[:-1]

        print(toUtf8("dialogInputBox:%s" % value))

    except:
        value = None
        KMessageBox.error(None, "Zenity and KDialog are required to edit resources.")

    return value


def dialogList(parameters = [], message = _("Select")):
    value = label = None

    try:
        if parameters:
            parameters = ["kdialog", "--title", PROGRAM_NAME, "--radiolist", message] \
                            + parameters
            dialogProcess = subprocess.Popen(parameters, stdout=subprocess.PIPE)
            dialogProcess.wait()
            value = u""
            for line in iter(dialogProcess.stdout.readline, ''):
                value += toUnicode(line)

            # Cleaning last "\n".
            if (value[-1] == "\n"):
                value = value[:-1]

            try:
                label = toUnicode(parameters[parameters.index(value) + 1])

            except:
                label = toUnicode(value)

        print(toUtf8("dialogList:%s" % value))

    except:
        KMessageBox.error(None, "Zenity and KDialog are required to edit resources.")

    return value, label


def dialogTextInputBox(message = _("Text"), value = "", ontType = "string"):
    try:
        if (ontType == "date"):
            oldYear = ""
            oldMonth = ""
            oldDay = ""
            if value:
                oldYear = "--year=%s" % value[:4]
                oldMonth = "--month=%s" % value[5:7]
                oldDay = "--day=%s" % value[8:10]

            parameters = ["zenity", "--calendar", "--title=" + PROGRAM_NAME, "--text=" + message, oldYear, oldMonth, oldDay, "--date-format=%Y-%m-%d"]

        else:
            parameters = ["kdialog", "--title", PROGRAM_NAME, "--textinputbox", message, value]

        dialogProcess = subprocess.Popen(parameters, stdout=subprocess.PIPE)
        dialogProcess.wait()
        value = u""
        for line in iter(dialogProcess.stdout.readline, ''):
            value += toUnicode(line)

        # Cleaning last "\n".
        if (value[-1] == "\n"):
            value = value[:-1]

        print(toUtf8("dialogTextInputBox:%s" % value))

    except:
        value = None
        KMessageBox.error(None, "Zenity and KDialog are required to edit resources.")

    return value


def downloadFile(remoteUrl, localUrl):
    remoteUrl = str(QUrl(toUnicode(remoteUrl)).toEncoded())

    result = False
    #NEPOOGLE_DOWNLOAD_METHOD = "curl"

    #if (NEPOOGLE_DOWNLOAD_METHOD == None):
        #try:
            #if (remoteUrl.find(".imgur.com/") < 0):
                #import pycurl, StringIO
                #NEPOOGLE_DOWNLOAD_METHOD = "libcurl"

            ##elif (remoteUrl.find(".wikimedia.org/") < 0):
            ##    NEPOOGLE_DOWNLOAD_METHOD = "curl"

            #else:
                #import urllib
                #NEPOOGLE_DOWNLOAD_METHOD = "urllib"

        #except:
            #pass

    #if (NEPOOGLE_DOWNLOAD_METHOD == "urllib"):
        #try:
            #urllib.urlretrieve(remoteUrl, localUrl)
            #result = True

        #except:
            #pass

    #elif (NEPOOGLE_DOWNLOAD_METHOD == "libcurl"):
        #cUrl = pycurl.Curl()
        #cUrl.setopt(pycurl.URL, remoteUrl)
        #strIO = StringIO.StringIO()
        #cUrl.setopt(pycurl.WRITEFUNCTION, strIO.write)
        ##cUrl.setopt(pycurl.FOLLOWLOCATION, 1)
        ##cUrl.setopt(pycurl.MAXREDIRS, 5)
        #cUrl.setopt(pycurl.POST, 1)
        #cUrl.perform()

        ## Data must be written to file.
        #try:
            #buffer = strIO.getvalue()
            #if buffer.find("<HTML>") < 0:
                #f = open(localUrl, "w")

                #try:
                    #f.write(strIO.getvalue())
                    #result = True

                #finally:
                    #f.close()

            #else:
                #NEPOOGLE_DOWNLOAD_METHOD = "curl"

        #except:
            #NEPOOGLE_DOWNLOAD_METHOD = "curl"
            #result = False

    #if (NEPOOGLE_DOWNLOAD_METHOD == "curl"):
    if True:
        try:
            subprocess.check_call(["curl", "-q", "--raw", "--fail", "-o", localUrl, remoteUrl])

        except:
            pass

        result = os.path.exists(localUrl)

    return result


def fileExists(fileName = ''):
    if fileName == '':
        return False

    fileName = toUnicode(fileName)
    if fileName[:7] == 'file://':
        return os.path.exists(fileName[7:])

    else:
        return os.path.exists(fileName)


def findRecurseFiles(rootPath = './', hidden = False):
    resources = []
    rootPath = os.path.normpath(rootPath)
    for dirPath, dirName, fileNames in os.walk(unicode(rootPath)):
        if not hidden and os.path.basename(dirPath)[0] == '.':
            continue

        resources += [addBS(dirPath)]
        for item in fileNames:
            if not hidden and item[0] == '.':
                continue

            resources += [addBS(dirPath) + item]

    return len(resources), sorted(resources)


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
    return str(QUrl.toPercentEncoding(url))


def toUtf8(string):
    try:
        if vartype(string) == 'QString':
            return string.toUtf8() # REVISAR: Esto no es coherente con el resto.

        else:
            #return string.encode(gSysEncoding)
            return string.encode("UTF-8")

    except:
        return string


def toUnicode(string):
    try:
        if (vartype(string) == 'QString'):
            return unicode(str(string.toUtf8()), gSysEncoding)

        elif (vartype(string) == 'QUrl'):
            return unicode(str(string.toString()), gSysEncoding)

        if (vartype(string) == 'unicode'):
            return string

        return unicode(string, gSysEncoding)

    except:
        return string


def toVariant(value):
    if (vartype(value) == "QUrl"):
        pass

    elif (vartype(value) == "QString"):
        if ((toUnicode(value).find("://") > 0) or (value[:13] == "nepomuk:/res/")):
            value = QUrl(value)

    elif (vartype(value) in ("unicode", "str")):
        if ((value.find("://") > 0) or (value[:13] == "nepomuk:/res/")):
            value = QUrl(value)

    return Nepomuk2.Variant(value)


def urlDecode(url, retryIfThereArePercentCharacters = True):
    url = toUtf8(url)
    qUrl = QUrl()
    try:
        #print(toUtf8(url))
        qUrl.setEncodedUrl(url)

    except:
        qUrl.setUrl(url)

    if (retryIfThereArePercentCharacters and (qUrl.toString().indexOf("%") >= 0)):
        result = urlDecode(qUrl.toString(), False)

    else:
        result = toUnicode(qUrl.toString())

    #print(toUtf8(result))
    return result


def urlHtmlEncode(url):
    if not url:
        return url

    if ((url[0] == "/") or (url[:7] == "file://")):
        return url.replace("\"", "&quot;").replace("#", "%23").replace("'", "&#39;").replace("?", "%3F")

    else:
        return url.replace("\"", "&quot;").replace("#", "%23").replace("'", "&#39;")


def vartype(var):
    return type(var).__name__

#END lfunctions.py
