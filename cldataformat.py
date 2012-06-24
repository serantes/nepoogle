#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - data format library.                                       *
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

import datetime, fractions, os, re

from PyQt4.QtCore import *
from PyKDE4.kdeui import *
from PyKDE4.nepomuk import *
from PyKDE4.soprano import *

from clsparql import *
from lfunctions import *
from lglobals import *

_ = gettext.gettext

#BEGIN cldataformat.py
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
    columnsCount = 3
    coverFileNames = ['cover.png', 'Cover.png', 'cover.jpg', 'Cover.jpg']
    data = []
    enableImageViewer = True
    hiddenOntologies = ["kext:unixFileGroup", "kext:unixFileMode", "kext:unixFileOwner", "nao:userVisible"]
    model = None
    ontologyMusicAlbumCover = NOC(ONTOLOGY_MUSIC_ALBUM_COVER)
    outFormat = 1  # 1- Text, 2- Html
    playlistShowWithOneElement = True
    playlistDescendingOrderInAlbumYear = True
    queryString = ""
    renderSize = 50
    renderedDataRows = 0
    renderedDataText = ""
    skippedOntologiesInResourceIsA = [NOC("nao:hasSubResource")]
    structure = []
    videojsEnabled = False

    supportedAudioFormats = ("flac", "mp3", "ogg", "wav")
    supportedImageFormats = QImageReader.supportedImageFormats() + ["nef"]
    supportedVideoFormats = ("avi", "divx", "flv", "mkv", "mp4", "mpeg", "mpg", "tp", "ts", "vob", "webm", "wmv")

    iconDelete = KIconLoader().iconPath('edit-delete', KIconLoader.Small)
    iconDocumentInfo = KIconLoader().iconPath('documentinfo', KIconLoader.Small)
    iconDocumentProp = KIconLoader().iconPath('document-properties', KIconLoader.Small)
    iconEmblemLink = KIconLoader().iconPath('emblem-link', KIconLoader.Small)
    iconFileManager = KIconLoader().iconPath('system-file-manager', KIconLoader.Small)
    iconKIO = KIconLoader().iconPath('kde', KIconLoader.Small)
    iconKonqueror = KIconLoader().iconPath('konqueror', KIconLoader.Small)
    iconListRemove = KIconLoader().iconPath('list-remove', KIconLoader.Small)
    iconNavigateFirst = KIconLoader().iconPath('go-first', KIconLoader.Small)
    iconNavigateLast = KIconLoader().iconPath('go-last', KIconLoader.Small)
    iconNavigateNext = KIconLoader().iconPath('go-next', KIconLoader.Small)
    iconNavigatePrevious = KIconLoader().iconPath('go-previous', KIconLoader.Small)
    iconNoCover = KIconLoader().iconPath('audio-x-generic', KIconLoader.Desktop)
    iconNoVideoThumbnail = KIconLoader().iconPath('video-x-generic', KIconLoader.Desktop)
    iconPlaylistFirst = KIconLoader().iconPath('go-first-view', KIconLoader.Small)
    iconPlaylistPrevious = KIconLoader().iconPath('go-previous-view', KIconLoader.Small)
    iconPlaylistNext = KIconLoader().iconPath('go-next-view', KIconLoader.Small)
    iconPlaylistLast = KIconLoader().iconPath('go-last-view', KIconLoader.Small)
    iconProcessIdle = KIconLoader().iconPath('process-idle', KIconLoader.Small)
    iconReindex = KIconLoader().iconPath('nepomuk', KIconLoader.Small)
    iconSystemRun = KIconLoader().iconPath('system-run', KIconLoader.Small)
    iconSystemSearch = KIconLoader().iconPath('system-search', KIconLoader.Small)
    iconSystemSearchWeb = KIconLoader().iconPath('edit-web-search', KIconLoader.Small)

    htmlHeader = "<html>\n" \
                        "<head>\n" \
                        "<title>%(title)s</title>\n" \
                        "<style type=\"text/css\">" \
                        "    body {%(body_style)s}\n" \
                        "    tr {%(tr_style)s}\n" \
                        "    p {%(p_style)s}\n" \
                        "</style>\n" \
                        "<meta charset=\"UTF-8\" />" \
                        "%(scripts)s\n" \
                        "</head>\n" \
                        "<body>\n" \
                        % {"title": "%s", \
                            "scripts": "%s", \
                            "body_style": "font-size:small;", \
                            "p_style": "font-size:small;", \
                            "tr_style": "font-size:small;" \
                            }
    htmlFooter = "</body>\n" \
                        "</html>"

    htmlProgramInfo = PROGRAM_HTML_POWERED

    htmlTableHeader = "<table style=\"text-align:left; width: 100%;\" " \
                            "border=\"1\" cellpadding=\"1\" cellspacing=\"0\">" \
                        "<tbody>\n"
    htmlTableFooter = "</tbody></table>\n"

    #TODO: This must be automatic.
    # This is not automatically generated and is linked to self.columnsCount.
    # To add a column self.columnsCount must be changed and this properties too.
    # Search for columnsformat for more changes.
    htmlTableColumn1 = "<td>%s</td>"
    htmlTableColumn2 = "<td>%s</td>"
    htmlTableColumn3 = "<td width=\"65px\">%s</td>"
    htmlTableRow = "<tr>" + htmlTableColumn1 + htmlTableColumn2 + htmlTableColumn3 + "</tr>"

    htmlViewerTableHeader = "<table style=\"text-align:left; width: 100%%;\" " \
                                "border=\"0\" cellpadding=\"3\" cellspacing=\"0\">" \
                                "<tbody>\n"
    htmlViewerTableFooter = "</tbody></table>\n"

    htmlStyleIcon = "align=\"center\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 14px; height: 14px;\""
    htmlStyleNavigate  = "align=\"center\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 20px; height: 20px;\""

    htmlStadistics = "%(records)s records found in %(seconds).4f seconds." \
                        "&nbsp;HTML visualization built in %(sechtml).2f seconds." \

    htmlLinkDelete = "<a title=\"Delete\" href=\"delete:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDelete) \
                            + "</a>"
    htmlLinkDolphin = "<a title=\"Open with Dolphin\" href=\"dolp:/%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconFileManager) \
                        + "</a>"
    htmlLinkInfo = "<a title=\"%(uri)s\" href=\"%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDocumentInfo) \
                        + "</a>"
    htmlLinkKonqueror = "<a title=\"Open with Konqueror\" href=\"konq:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconKonqueror) \
                            + "</a>"
    htmlLinkNavigateFirst = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "first", "hotkey": "Ctrl+PgUp", "style": htmlStyleNavigate, "icon": iconNavigateFirst}
    htmlLinkNavigateLast = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "last", "hotkey": "Ctrl+PgDown", "style": htmlStyleNavigate, "icon": iconNavigateLast}
    htmlLinkNavigatePrevious = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "previous", "hotkey": "Ctrl+Left", "style": htmlStyleNavigate, "icon": iconNavigatePrevious}
    htmlLinkNavigateNext = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "next", "hotkey": "Ctrl+Right", "style": htmlStyleNavigate, "icon": iconNavigateNext}
    htmlLinkOpenKIO = "<a title=\"Open location %(uri)s\" href=\"%(uri)s\">" \
                                + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconKIO) \
                                + "</a>"
    htmlLinkOpenLocation = "<a title=\"Open location %(uri)s\" href=\"%(uri)s\">" \
                                + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconFileManager) \
                                + "</a>"
    htmlLinkProperties = "<a title=\"Properties\" href=\"prop:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDocumentInfo) \
                            + "</a>"
    htmlLinkRemove = "<a title=\"Remove resource%(hotkey)s\" href=\"remove:/%(uri)s\">" \
                            + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconDelete) \
                            + "</a>"
    htmlLinkSearch = "<a title=\"%(uri)s\" href=\"query:/%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconSystemSearch) \
                        + "</a>"
    htmlLinkSearchRender = "<img align=\"bottom\" border=\"0\" hspace=\"0\" vspace=\"0\" " \
                                "style=\"width: 14px; height: 14px;\" " \
                                " src=\"file://%s\">" % (iconSystemSearch)
    htmlLinkSearchWebRender = "<img align=\"bottom\" border=\"0\" hspace=\"0\" vspace=\"0\" " \
                                "style=\"width: 14px; height: 14px;\" " \
                                " src=\"file://%s\">" % (iconSystemSearchWeb)
    htmlLinkSystemRun = "<a title=\"Open file %(uri)s\" href=\"run:/%(uri)s\">" \
                        + "<img %s src=\"file://%s\">" % (htmlStyleIcon, iconSystemRun) \
                        + "</a>"

    htmlVideoSize = "height=\"360\" width=\"640\""

    #TODO: columnsformat. This is linked to self.columnsCount.
    ontologyFormat = [ \
                        [None, \
                            "{uri|l|of}%[<br /><b>Full name</b>: {nco:fullname}%]%[<br /><b>Label</b>: {nao:prefLabel}%]%[<br /><b>Title</b>: {nie:title}%]" \
                                "%[<br /><b>Url</b>: {nie:url|of|ol}%]" \
                                "%[<br /><b>Rating</b>: {nao:numericRating}%]" \
                                "%[<br /><b>Description</b>: {nie:description}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["pimo:Topic", \
                            "{pimo:tagLabel|l}%[<br />Other labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nao:Agent", \
                            "{uri|l|of}%[<br /><b>Identifier</b>: {nao:identifier}%] %[<b>Label</b>: {nao:prefLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nmm:Movie", \
                            "<b>Title</b>: {nie:title|l|of|ol}" \
                                "%[<br /><b>Rating</b>: {nao:numericRating}%]" \
                                "<br /><b>Actors</b>: {SPARQL}SELECT DISTINCT ?uri ?value WHERE { <%(uri)s> nmm:actor ?uri . ?uri nco:fullname ?value . } ORDER BY ?value|l|s:actor{/SPARQL}" \
                                "%[<br /><b>Description</b>: {nie:description}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nmm:MusicAlbum", \
                            "{nie:title|l|s:album}" \
                                "%[ <b>by</b> {SPARQL}SELECT DISTINCT ?uri ?value WHERE { <%(uri)s> nmm:albumArtist ?uri . ?uri nco:fullname ?value . } ORDER BY ?value|l|s:albumartist{/SPARQL}%]<br />" \
                                "<b>Performers</b>: {SPARQL}SELECT DISTINCT ?uri ?value WHERE { ?r nmm:musicAlbum <%(uri)s> . ?r nmm:performer ?uri . ?uri nco:fullname ?value . } ORDER BY ?value|l|s:performer{/SPARQL}", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nmm:MusicPiece", \
                            "{nfo:fileName|l|of|ol}<br />" \
                                "<b>Title</b>: <em>%[{nmm:setNumber}x%]{nmm:trackNumber|f%02d} - {nie:title}</em><br />" \
                                "<b>Album</b>: {nmm:musicAlbum->nie:title|l|s:album}<br \>" \
                                "%[<b>Performers</b>: {SPARQL}SELECT DISTINCT ?uri ?value WHERE { <%(uri)s> nmm:performer ?uri . ?uri nco:fullname ?value . } ORDER BY ?value|l|s:performer{/SPARQL}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nmm:TVSeason", \
                            "<b>Title</b>: {nmm:seasonOf->nie:title|l} <br /><b>Season</b>: {nmm:seasonNumber|l}", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nmm:TVSeries", \
                                "{SPARQL}SELECT ?banner AS ?uri ?url AS ?value WHERE { <%(uri)s> nfo:depiction ?banner . ?banner nfo:height 140 . ?banner nie:url ?url . } LIMIT 1|i{/SPARQL}" \
                                "{nie:title|l|s:tvserie|ok:tvshow}" \
                                "%[<br /><b>Last watched episode</b>: S{SPARQL}SELECT DISTINCT ?uri ?season AS ?value WHERE { ?x1 nmm:series <%(uri)s> ; nmm:episodeNumber ?episode ; nmm:season ?season ; nuao:usageCount ?v2 . FILTER(?v2 > 0) . } ORDER BY DESC(1000*?season + ?episode) LIMIT 1|f%02d{/SPARQL}" \
                                "E{SPARQL}SELECT DISTINCT ?uri ?episode AS ?value ?season WHERE { ?x1 nmm:series <%(uri)s> ; nmm:episodeNumber ?episode ; nmm:season ?season ; nuao:usageCount ?v2 . FILTER(?v2 > 0) . } ORDER BY DESC(1000*?season + ?episode) LIMIT 1|f%02d{/SPARQL}" \
                                " - {SPARQL}SELECT DISTINCT ?x1 AS ?uri ?value WHERE { ?x1 nmm:series <%(uri)s> . ?x1 nmm:episodeNumber ?episode ; nmm:season ?season ; nie:title ?value ; nuao:usageCount ?v2 . FILTER(?v2 > 0) . } ORDER BY DESC(1000*?season + ?episode) LIMIT 1|l|s:tvshows{/SPARQL}%]"
                                "%[<br /><b>Last downloaded episode</b>: S{SPARQL}SELECT DISTINCT ?uri ?season AS ?value WHERE { ?x1 nmm:series <%(uri)s> ; nmm:episodeNumber ?episode ; nmm:season ?season . } ORDER BY DESC(1000*?season + ?episode) LIMIT 1|f%02d{/SPARQL}" \
                                "E{SPARQL}SELECT DISTINCT ?uri ?episode AS ?value ?season WHERE { ?x1 nmm:series <%(uri)s> ; nmm:episodeNumber ?episode ; nmm:season ?season . } ORDER BY DESC(1000*?season + ?episode) LIMIT 1|f%02d{/SPARQL}" \
                                " - {SPARQL}SELECT DISTINCT ?x1 AS ?uri ?value WHERE { ?x1 nmm:series <%(uri)s> . ?x1 nmm:episodeNumber ?episode ; nmm:season ?season ; nie:title ?value . } ORDER BY DESC(1000*?season + ?episode) LIMIT 1|l|s:tvshows{/SPARQL}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nmm:TVShow", \
                            "{SPARQL}SELECT ?banner AS ?uri ?url AS ?value WHERE { <%(uri)s> nmm:series ?series . ?series nfo:depiction ?banner . ?banner nfo:height 140 . ?banner nie:url ?url . } LIMIT 1|i{/SPARQL}" \
                            "%[<b>Episode:</b> S{nmm:season|f%02d}E{nmm:episodeNumber|f%02d} - %]{nie:title|l|of|ol}" \
                                "%[<br \><b>Series</b>: {nmm:series->nie:title|l|ol|ok:tvshow}%]"\
                                "%[ <b>Watched</b>: {nuao:usageCount} times%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nfo:Audio", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]%[<br />url: {nie:url}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:FileDataObject", \
                            "{nie:url|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:FileHash", \
                            "<b>File hash</b>: {nie:url|l|of|ol}" \
                                "<br /><b>Associated files</b>:<br />{SPARQL}SELECT DISTINCT ?uri ?value WHERE { ?uri nfo:hasHash <%(uri)s> . optional { ?uri nie:url ?value } . } ORDER BY ?value|lfld|n{/SPARQL}", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Folder", \
                            "{nie:url|l|of|ol}%[<br />Filename: {nfo:fileName}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nfo:Image", \
                            "{nie:url|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:PaginatedTextDocument", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:RasterImage", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Spreadsheet", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:TextDocument", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]" \
                                "%[<br /><b>Lines</b>: {nfo:lineCount} <b>Words</b>: {nfo:wordCount} <b>Characters</b>: {nfo:characterCount}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Video", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_SYSTEM_RUN], \
                        ["nfo:Website", \
                            "{nie:url|l|of}%[<br /><b>Title</b>: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_SYSTEM_RUN], \
                        ["nfo:WebDataObject", \
                            "{nie:url|l|of}%[<br /><b>Title</b>: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_SYSTEM_RUN], \
                        ["nao:Tag", \
                            "{nao:prefLabel|l|of|ol|s:hasTag}%[<br />Other labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nco:Contact", \
                            "{nco:fullname|l|s:contact}%[<br />Other labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nco:PersonContact", \
                            "{nco:fullname|l|s:contact}%[<br />Other labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nexif:Photo", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nie:InformationElement", \
                            "{nfo:fileName|l|of|ol}%[<br />Other labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["rdfs:Resource", \
                            "{nie:url|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE] \
                    ]


    def __init__(self, searchString = "", model = None):
        self.searchString = searchString
        if model == None:
            if DO_NOT_USE_NEPOMUK:
                self.model = Soprano.Client.DBusModel('org.kde.NepomukStorage', '/org/soprano/Server/models/main')

            else:
                self.model = Nepomuk.ResourceManager.instance().mainModel()

        else:
            self.model = model


    def getCoverUrl(self, res = None, url = ""):
        if res in (None, ""):
            return None

        if vartype(res) in ("str", "QString", "QVariant"):
            if INTERNAL_RESOURCE:
                res = cResource(res)

            else:
                res = Nepomuk.Resource(res)

        # Setting default cover.
        coverUrl = self.iconNoCover

        # First try to extract this information from the resource.
        if res.hasProperty(self.ontologyMusicAlbumCover):
            if INTERNAL_RESOURCE:
                resUris = res.property(self.ontologyMusicAlbumCover)
                if vartype(resUris) != "list":
                    resUris = [resUris]

            else:
                resUris = res.property(self.ontologyMusicAlbumCover).toStringList()

            for uri in resUris:
                if INTERNAL_RESOURCE:
                    resTmp = cResource(uri)

                else:
                    resTmp = Nepomuk.Resource(uri)

                tmpCoverUrl = self.readProperty(resTmp, 'nie:url', 'str')
                if tmpCoverUrl[:7] == "file://":
                    tmpCoverUrl = tmpCoverUrl[7:]

                if ((tmpCoverUrl != "") and fileExists(tmpCoverUrl)):
                    coverUrl = tmpCoverUrl.replace("\"", "&quot;").replace("#", "%23").replace("'", "&#39;").replace("?", "%3F")
                    break

        # If there is no property then let's try to locate using tracks location.
        if coverUrl == self.iconNoCover:
            if url[:7] == "file://":
                url = url[7:]

            url = os.path.dirname(url)
            for coverName in ('cover.png', 'Cover.png', 'cover.jpg', 'Cover.jpg'):
                tmpCoverUrl = url + '/' + coverName
                if fileExists(tmpCoverUrl):
                    coverUrl = tmpCoverUrl.replace("\"", "&quot;").replace("#", "%23").replace("'", "&#39;").replace("?", "%3F")
                    break

        return "file://" + coverUrl


    def resourceIsA(self, uri = None):
        if (vartype(uri) != "str"):
            uri = toUnicode(uri.uri())

        result = []

        if (uri == None) or (uri == ""):
            return ", ".join(result)

        query = "SELECT DISTINCT ?p\n" \
                "WHERE {\n" \
                "  [] ?p <%s> .\n" \
                "}\n" % uri

        ontologies = []
        queryResultSet = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        if queryResultSet.isValid():
            while queryResultSet.next():
                ontologies += [toUnicode(queryResultSet["p"].toString())]

        for ontology in ontologies:
            if not ontology in self.skippedOntologiesInResourceIsA:
                result += [ontologyInfo(ontology)[1]]

        result.sort()

        return  ", ".join(result)


    def buildPlaylist(self, data = [], listType = "audio"):
        listType = listType.lower()
        #TODO: Añadir soporte para imágenes..., algún tipo de slideshow.
        #TODO: Mantener volumen entre preproducciones.
        #TODO: from PyKDE4.kio import *
        #TODO:     oKPJ = KIO.PreviewJob()
        if not listType in ('audio', 'video'):
            return ""

        if len(data) < 1:
            return ""

        data = sorted(data, key=lambda item: item[0])
        i = 0
        playList = []
        output = ""
        oldTitle = ["", "", 0]
        oldPerformers = []
        albumYear = None

        for item in data:
            sortColumn = ""
            url = item[0]
            if url[:7] != "file://":
                url = "file://" + url

            if INTERNAL_RESOURCE_IN_PLAYLIST:
                res = cResource(item[1])

            else:
                res = Nepomuk.Resource(item[1])

            if listType == 'audio':
                trackNumber = self.readProperty(res, 'nmm:trackNumber', 'int')
                discNumber = self.readProperty(res, 'nmm:setNumber', 'int')
                trackName = self.readProperty(res, 'nie:title', 'str')
                if trackName == "":
                    trackName = os.path.basename(url)

                trackName = "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                % {"uri": item[1], "title": trackName}
                if trackNumber != None:
                    trackName = "%02d - " % trackNumber + trackName

                if discNumber != None:
                    trackName = "%02d/" % discNumber + trackName

                albumYear = self.readProperty(res, 'nie:contentCreated', 'year')
                if albumYear == None:
                    albumYear = 0

                sortColumn = trackName
                coverUrl = None

                # Performers.
                performers = []
                if res.hasProperty(NOC('nmm:performer')):
                    if INTERNAL_RESOURCE_IN_PLAYLIST:
                        resUris = res.property(NOC('nmm:performer'))
                        if vartype(resUris) != "list":
                            resUris = [resUris]

                    else:
                        resUris = res.property(NOC('nmm:performer')).toStringList()

                    for itemUri in resUris:
                        if INTERNAL_RESOURCE_IN_PLAYLIST:
                            resTmp = cResource(itemUri)

                        else:
                            resTmp = Nepomuk.Resource(itemUri)

                        fullname = self.readProperty(resTmp, 'nco:fullname', 'str')
                        if fullname != None:
                            performers += [[itemUri, fullname]]

                performers = sorted(performers, key=lambda item: toUtf8(item[1]))
                if performers == oldPerformers:
                    performers = []

                else:
                    oldPerformers = list(performers)

                # Album title.
                albumTitle = [None, "", 0, ""]
                if res.hasProperty(NOC('nmm:musicAlbum')):
                    if INTERNAL_RESOURCE_IN_PLAYLIST:
                        resUri = res.property(NOC('nmm:musicAlbum'))
                        resTmp = cResource(resUri)

                    else:
                        resUri = res.property(NOC('nmm:musicAlbum')).toStringList()[0]
                        resTmp = Nepomuk.Resource(resUri)

                    albumTitle = self.readProperty(resTmp, 'nie:title', 'str')

                    if albumTitle == None:
                        oldTitle = [None, "", 0, ""]

                    elif not (oldTitle[1] == albumTitle):
                        # Obtain album artists.
                        albumArtists = []
                        if resTmp.hasProperty(NOC('nmm:albumArtist')):
                            if INTERNAL_RESOURCE_IN_PLAYLIST:
                                resUris = resTmp.property(NOC('nmm:albumArtist'))
                                if vartype(resUris) != "list":
                                    resUris = [resUris]

                            else:
                                resUris = resTmp.property(NOC('nmm:albumArtist')).toStringList()

                            for itemUri in resUris:
                                if INTERNAL_RESOURCE_IN_PLAYLIST:
                                    resTmp2 = cResource(itemUri)

                                else:
                                    resTmp2 = Nepomuk.Resource(itemUri)

                                fullname = self.readProperty(resTmp2, 'nco:fullname', 'str')
                                if fullname != None:
                                    albumArtists += [[itemUri, fullname]]

                        albumArtists = sorted(albumArtists, key=lambda item: toUtf8(item[1]))
                        linkAlbumArtists = ""
                        for artist in albumArtists:
                            if linkAlbumArtists != "":
                                linkAlbumArtists += ",&nbsp;"

                            linkAlbumArtists += "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                            % {"uri": artist[0], "title": artist[1]}

                        oldTitle = [resUri, albumTitle, albumYear, linkAlbumArtists]
                        albumTitle = [resUri, albumTitle, albumYear, linkAlbumArtists]
                        performers = list(oldPerformers)

                    else:
                        albumTitle = ["", "", 0, ""]

                # Final track name building.
                if albumTitle[1] != "":
                    linkTitle = "<a title='%(uri)s' href='%(uri)s'>%(title)s (%(year)s)</a>" \
                                    % {"uri": albumTitle[0], "title": albumTitle[1], "year": albumTitle[2]}
                    if albumTitle[3] != "":
                        linkTitle += " by " + albumTitle[3]

                    linkPerformers = ""
                    for performer in performers:
                        if linkPerformers != "":
                            linkPerformers += ",&nbsp;"

                        linkPerformers += "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                        % {"uri": performer[0], "title": performer[1]}

                    trackName = "<em>%s</em><br /><em>%s</em><br />%s" \
                                    % (linkTitle, linkPerformers, trackName)

                    # Cover.
                    coverUrl = self.getCoverUrl(albumTitle[0], toUnicode(self.readProperty(res, 'nie:url', 'str')))
                    trackName = "<img width=48 style='float:left; " \
                                    "vertical-align:text-bottom; margin:2px' " \
                                    "src='%s'>" % (coverUrl) \
                                + trackName

                elif performers != []:
                    linkPerformers = ""
                    for performer in performers:
                        if linkPerformers != "":
                            linkPerformers += ",&nbsp;"

                        linkPerformers += "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                        % {"uri": performer[0], "title": performer[1]}

                    trackName = "<em>%s</em><br />%s" % (linkPerformers, trackName)

                elif (albumTitle[0] == None) or (oldPerformers == []):
                    # Probably a video or a music file without tags. Use a thumbnail is exists.
                    if coverUrl == None:
                        tmpCoverUrl = getThumbnailUrl(toUnicode(self.readProperty(res, 'nie:url', 'str')))
                        if tmpCoverUrl != None:
                            coverUrl = tmpCoverUrl

                    # If there is no thumbnail then default image is displayed.
                    if coverUrl == None:
                        coverUrl = "file://" + self.iconNoCover

                    trackName = "<img width=48 style='float:left; " \
                                    "vertical-align:text-bottom; margin:2px' " \
                                    "src='%s'>" % (coverUrl) \
                                + trackName

                trackName = trackName.replace('"', '&quot;')
                if self.playlistDescendingOrderInAlbumYear:
                    sortAdjustment = 9999

                else:
                    sortAdjustment = 0

                sortColumn = "%s_%s_%s" % (oldTitle[2] - sortAdjustment, oldTitle[1], sortColumn)

            elif listType == 'video':
                # Thumbnail.
                thumbnailUrl = None
                if res.hasProperty(NOC('nie:url')):
                    thumbnailUrl = getThumbnailUrl(toUnicode(self.readProperty(res, 'nie:url', 'str')))

                    if thumbnailUrl == None:
                        thumbnailUrl = "file://" + self.iconNoVideoThumbnail

                # Title.
                trackName = self.readProperty(res, 'nie:title', 'str')
                if ((trackName == None) or (trackName == "")):
                    dummyVal = os.path.basename(url)
                    sortColumn = dummyVal
                    trackName = "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                    % {"uri": res.uri(), "title": dummyVal}

                else:
                    sortColumn = trackName
                    trackName = "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                    % {"uri": res.uri(), "title": trackName}

                    # Episode number.
                    episodeNumber = self.readProperty(res, 'nmm:episodeNumber', 'int')
                    seasonNumber = self.readProperty(res, 'nmm:season', 'int')
                    if episodeNumber != None:
                        dummyVal = "E%02d - " % episodeNumber
                        sortColumn = dummyVal + sortColumn
                        trackName = dummyVal + trackName

                    # Season.
                    if seasonNumber != None:
                        dummyVal = "S%02d" % seasonNumber
                        sortColumn = dummyVal + sortColumn
                        trackName = dummyVal + trackName

                    # Watched?.
                    if res.hasProperty(NOC('nuao:usageCount')):
                        if res.property(NOC('nuao:usageCount')).toString() == '1':
                            trackName += ' <b><em>(watched)</em></b>'

                    # Series title.
                    if res.hasProperty(NOC('nmm:series')):
                        if INTERNAL_RESOURCE:
                            resUri = res.property(NOC('nmm:series'))
                            resTmp = cResource(resUri)

                        else:
                            resUri = res.property(NOC('nmm:series')).toStringList()[0]
                            resTmp = Nepomuk.Resource(resUri)

                        if resTmp.hasProperty(NOC('nie:title')):
                            dummyVal = resTmp.property(NOC('nie:title')).toString()
                            sortColumn = dummyVal + sortColumn
                            trackName = "<em><a title='%(uri)s' href='%(uri)s'>%(title)s</a></em>: %(trackName)s" \
                                            % {"uri": resTmp.uri(), "title": dummyVal, "trackName": trackName}

                if thumbnailUrl != None:
                    trackName = "<img width=48 style='float:left; " \
                                    "vertical-align:text-bottom; margin:2px' " \
                                    "src='%s'>" % (thumbnailUrl) \
                                + trackName

                trackName = trackName.replace('"', '&quot;')

            playList += [[item[1], i, url, trackName, sortColumn]]
            i += 1

        playList = sorted(playList, key=lambda item: toUtf8(item[4]))
        url = playList[0][2]
        if url[:7] == "file://":
            url = url[7:]

        if listType == 'audio':
            output += "<b>Audio player</b><br />\n" \
                        "<audio id=\"%splayer\" " \
                            "src=\"file://%s\" controls preload>No audio support</audio><br />\n" \
                            % (listType, url.replace("\"", "&quot;").replace("#", "%23").replace("?", "%3F"))

        elif listType == 'video':
            output += "<b>Video player</b><br />\n" \
                        "<video id=\"%splayer\" " \
                            "src=\"file://%s\" %s controls preload>No video support</video><br />\n" \
                            % (listType, url.replace("\"", "&quot;").replace("#", "%23").replace("?", "%3F"), self.htmlVideoSize)

        if self.playlistShowWithOneElement or len(data) > 1:
            output += "<img onclick='%(type)splayTrack(-1)' style='margin:2px' src='file://%(f)s'>" \
                        "<img onclick='%(type)splayTrack(-2)' style='margin:2px' src='file://%(p)s'>" \
                        "<img onclick='%(type)splayTrack(-3)' style='margin:2px' src='file://%(n)s'>" \
                        "<img onclick='%(type)splayTrack(-4)' style='margin:2px' src='file://%(l)s'>" \
                        "<br />" \
                         % {"type": listType, "f": self.iconPlaylistFirst, "p": self.iconPlaylistPrevious, "n": self.iconPlaylistNext, "l": self.iconPlaylistLast}
            output += "<b>Playlist</b>:<br />\n" \
                        "<script>\n" \
                        "var %(type)scurrItem = 0;\n" \
                        "var %(type)splayerVolume = 0;\n" \
                        "var %(type)stotalItems = %(i)s;\n" \
                        "var %(type)splayList = new Array();\n" % {"type": listType, "i": i}

            output += "document.write(\"<div id='%(type)splaylist' style='overflow: auto; height: 250px; width: 100%%;'>\")\n" % {"type": listType}
            output += "document.write(\"<table style='width:100%;'>\")\n"
            i = 0
            for item in playList:
                output += "%splayList[%s] = [\"%s\", \"%s\"]\n" % (listType, i, item[2].replace("\"", "\\\"").replace("#", "%23").replace("?", "%3F"), item[3])
                iconRun = self.htmlLinkSystemRun % {"uri": item[2].replace("\"", "&quot;").replace("#", "%23").replace("'", "&#39;").replace("?", "%3F")}
                iconRun = iconRun.replace('"', "'")
                iconDir = self.htmlLinkOpenLocation % {"uri": os.path.dirname(item[2]).replace("\"", "&quot;").replace("#", "%23").replace("'", "&#39;").replace("?", "%3F")}
                iconDir = iconDir.replace('"', "'")
                row = "<tr>"
                row += "<td width='30px'><button onclick='%(type)splayTrack(%(i)s)' type='%(type)sbtnTrack%(i)s'>" \
                            "%(trackNumber)02d</button></td>" % {"type": listType, "i": i, "trackNumber": i + 1 }
                row += "<td id='%(type)strack%(i)s' style='background-color:%(color)s;padding:0 0 0 5;' onclick='%(type)splayTrack(%(i)s)'>" \
                            "%(title)s</td>" % {"type": listType, "color": "LightBlue", "i": i, "title": item[3]}
                row += "<td width='15px' style='background-color:%(color)s;' >%(iconRun)s%(iconDir)s</td>" \
                            % {"color": "LightGray", "iconRun": iconRun, "iconDir": iconDir}
                row += "</tr>"
                output += "document.write(\"%s\");\n" % (row)
                i += 1

            output += "document.write(\"</table>\")\n"
            output += "document.write(\"</div>\")\n"

            output += "var %(type)splayer = document.getElementById('%(type)splayer');\n" % {"type": listType}

            output += "%(type)splayerVolume = 0.7;\n" % {"type": listType}
            output += "%(type)splayer.volume = %(type)splayerVolume;\n" % {"type": listType}

            output += \
                "%(type)splayer.addEventListener('play', function () {\n" \
                "    oldTrackOffsetTop = 0;\n" \
                "    for ( var i = 0; i < %(type)stotalItems; i++ ) {\n" \
                "        %(type)splayer.volume = %(type)splayerVolume;\n" \
                "        var %(type)strack = document.getElementById('%(type)strack' + i);\n" \
                "        if (i == %(type)scurrItem) {\n" \
                "            %(type)strack.style.fontWeight = 'bold';\n" \
                "            scrollTop = document.getElementById('%(type)splaylist').scrollTop;\n" \
                "            if (%(type)strack.offsetTop >  scrollTop + 200 || %(type)strack.offsetTop < scrollTop + 50) {\n" \
                "                document.getElementById('%(type)splaylist').scrollTop = oldTrackOffsetTop;\n" \
                "            }\n" \
                "        } else {\n" \
                "            %(type)strack.style.fontWeight = 'normal';\n" \
                "        }\n" \
                "        oldTrackOffsetTop = %(type)strack.offsetTop\n" \
                "    }\n" \
                "    %(type)splayer.volume = %(type)splayerVolume;\n" \
                "    //window.alert(%(type)splayer.volume);\n" \
                "} );\n" % {"type": listType}

            output += \
                "%(type)splayer.addEventListener('ended', function () {\n" \
                "    %(type)scurrItem += 1;\n" \
                "    if (%(type)scurrItem < %(type)stotalItems) {\n" \
                "        %(type)splayer.setAttribute('src', %(type)splayList[%(type)scurrItem][0]);\n" \
                "        %(type)splayer.play();\n" \
                "    } else {\n" \
                "        %(type)scurrItem = %(type)scurrItem - 1;\n" \
                "        var %(type)strack = document.getElementById('%(type)strack' + %(type)scurrItem);\n" \
                "        %(type)strack.style.fontWeight = 'normal';\n" \
                "        %(type)scurrItem = 0;\n" \
                "        %(type)splayer.setAttribute('src', %(type)splayList[%(type)scurrItem][0]);\n" \
                "    }\n" \
                "} );\n" % {"type": listType}

            output += \
                "%(type)splayer.addEventListener('volumechange', function() {\n" \
                "    %(type)splayerVolume = %(type)splayer.volume;\n" \
                "} );\n" % {"type": listType}

            output += \
                "function %(type)splayTrack(track) {\n" \
                "    if (track == -1) { track = 0 };\n" \
                "    if (track == -2) { track = %(type)scurrItem - 1 };\n" \
                "    if (track == -3) { track = %(type)scurrItem + 1 };\n" \
                "    if (track == -4) { track = %(type)splayList.length - 1 };\n" \
                "    if (track <= 0) { track = 0 };\n" \
                "    if (track >= %(type)splayList.length) { track = %(type)splayList.length - 1 };\n" \
                "    <!--if (%(type)scurrItem != track) {-->\n" \
                "        %(type)scurrItem = track;\n" \
                "        %(type)splayer.setAttribute('src', %(type)splayList[%(type)scurrItem][0]);\n" \
                "        %(type)splayer.play();\n" \
                "    <!--}-->;\n" \
                "}\n" % {"type": listType}

            output += "</script>\n"

            #print '<html>\n<body>\n' + toUtf8(output) + '\n</body>\n</html>'

        return output


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
                # There is a segmentation fault using Nepomuk.Resource() in ssh.
                if INTERNAL_RESOURCE_FORCED_IN_CONSOLE or INTERNAL_RESOURCE:
                    resource = cResource(uri)

                else:
                    resource = Nepomuk.Resource(uri)

                altLabel = resource.property(NOC('nao:altLabel')).toString()
                fullname = resource.property(NOC('nco:fullname')).toString()
                identifier = resource.property(NOC('nao:identifier')).toString()
                itemType = toUnicode(resource.type().split('#')[1])
                prefLabel = resource.property(NOC('nao:prefLabel')).toString()
                title = resource.property(NOC('nie:title')).toString()
                url = resource.property(NOC('nie:url')).toString()

                fullTitle = "%s  %s  %s  %s" % (fullname, title, prefLabel, altLabel)
                fullTitle = fullTitle.strip().replace("  ", " - ")
                line = "%s, %s, %s" % (url, fullTitle, itemType)
                line = line.replace(", , ", ", ")
                if line[:2] == ", ":
                    line = line[2:]

            else:
                for i in range(0, numColumns):
                    if line != "":
                        line += ", "

                    line += "%s" % row[i]

                line += ", Unknown"

            if line != '':
                print(toUtf8(line))
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

        elif id == 'googlesearch':
            title = "title=\"Search for &quot;%s&quot; using Google\"" % par1
            href = "href=\"googlesearch:/%%22%s%%22\"" % par1.replace(' ', '+')
            value = self.htmlLinkSearchWebRender

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
            htmlLinkInfo = "<img align=\"bottom\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 14px; height: 14px;\" src=\"file://%s\">" % (self.iconDocumentInfo)
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


    def fmtValue(self, value, valueType):
        valueType = valueType.lower()
        try:
            if valueType == 'boolean':
                result = value

            elif valueType == 'datep':
                result = formatDate(value[:19], True)

            elif valueType == 'date':
                result = formatDate(value[:19])

            elif valueType == 'datetimep':
                result = formatDateTime(value[:19], True)

            elif valueType == 'datetime':
                result = formatDateTime(value[:19])

            elif valueType == 'unixfilemode':
                result = "%o" % int(value)
                result = "%s %s" % (result[:3], result[3:])

            elif valueType in ('int', 'integer', 'number', 'nonnegativeinteger'):
                result = "%d" % int(float(value))

            elif valueType == 'float':
                result = "%.4f" % float(value)

            elif valueType == 'duration':
                result = "%s" % datetime.timedelta(0, int(value), 0)

            elif valueType == 'size':
                result = "%s" % "%0.2f MiB" % (int(value)/1024.00/1024.00)

            elif valueType == 'string':
                result = value

            elif valueType == 'aperturevalue':
                result = "%.1f" % float(value)

            elif valueType == 'exposurebiasvalue':
                try:
                    value = fractions.Fraction(value).limit_denominator(max_denominator=3)
                    result = "%s/%s" % (value.numerator, value.denominator)

                except:
                    result = "%s" % value

            elif valueType == 'exposuretime':
                try:
                    value = fractions.Fraction(value).limit_denominator(max_denominator=16000)
                    result = "%s/%s" % (value.numerator, value.denominator)

                except:
                    result = "%s" % value

            elif valueType == 'focallength':
                try:
                    value = fractions.Fraction(value).limit_denominator()
                    result = "%s/%s" % (value.numerator, value.denominator)

                except:
                    result = "%s" % value

            else:
                result = value

        except:
            result = value

        return result


    def readProperty(self, resource, propertyOntology, propertyType = "str"):
        try:
            if vartype(resource) in ("str", "QString"):
                if INTERNAL_RESOURCE:
                    resource = cResource(resource)

                else:
                    resource = Nepomuk.Resource(resource)

            result = resource.property(NOC(propertyOntology))
            if result != None:
                if (propertyType == "int"):
                    result = int(result.toString())

                elif (propertyType == "year"):
                    result = int(result.toString()[:4])

                else:
                    result = toUnicode(result.toString())

        except:
            result = None

        return result


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

                elif elements[0] == "type":
                    values += [[toUnicode(resource.uri()), NOCR(resource.type())]]

                else:
                    propertyValue = toUnicode(resource.property(NOC(elements[0])).toString())
                    if elements[0] == "nie:url":
                        #propertyValue = fromPercentEncoding(propertyValue)
                        if propertyValue[:8] == "filex://":
                            uuid = propertyValue[8:].split('/')[0]
                            htmlLinkInfo = "<img align=\"bottom\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 14px; height: 14px;\" src=\"file://%s\">" % (self.iconDocumentInfo)
                            unpluggedLink = "[<b>Unplugged</b><a title=\"uuid:%s\" href=\"prop:/%s\">%s</a>]/" \
                                                % (uuid, uuid, htmlLinkInfo)
                            propertyValue = unpluggedLink + '/'.join(propertyValue[8:].split('/')[1:])

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

        optionals = re.findall('%\[(.*?)%\]', pattern)
        optionalsEmpty = list(optionals)

        return data, variables, optionals, optionalsEmpty


    def formatResource(self, resource, pattern):
        # Variables substitution.
        data, variables, optionals, optionalsEmpty = self.processFormatPattern(pattern)
        listSeparation = ", "
        for variable in variables:
            variable = toUnicode(variable)
            elements = variable.split("|")
            addImage = addLink = addLinkOpenFile = addLinkOpenLocation = addOpenFile = addOpenLocation = addOpenKIO = addSearch = False
            KIOName = ""
            for item in elements:
                if item == "l" or item[:1] == "l":
                    addLink = True
                    addLinkOpenFile = (item[1:].find("f") >= 0)
                    addLinkOpenLocation = (item[1:].find("l") >= 0)
                    addLinkDelete = (item[1:].find("d") >= 0)

                elif item == "i":
                    addImage = True

                elif item == "of":
                    addOpenFile = True

                elif item == "ol":
                    addOpenLocation = True

                elif item[:2] == "ok":
                    addOpenKIO = True
                    KIOName = item[3:]

                elif item == "s" or item[:2] == "s:":
                    addSearch = True
                    searchTerm = item.split(":")
                    if len(searchTerm) > 1:
                        searchTerm = searchTerm[1]

                    else:
                        searchTerm = elements[0]

                elif item == "n":
                    listSeparation = "<br />"

                elif item[:1] == "f" and len(item) > 1:
                    fmtValue = item[1:]
                    #TODO: this must be improved.
                    if (fmtValue[-1].lower() == 'd'):
                        fmtValueToNumber = True

                    for value in values:
                        if value[1] != "":
                            if fmtValueToNumber:
                                try:
                                    value[1] = fmtValue % int(value[1])

                                except:
                                    value[1] = "0"

                            else:
                                try:
                                    value[1] = fmtValue % value[1]

                                except:
                                    value[1] = "0"

                else:
                    values = self.readValues(resource, item)

            formatValue = ""
            for value in values:
                if formatValue != "":
                    formatValue += listSeparation

                if len(value) == 1:
                    displayValue += [""]

                if addLink:
                    if value[1] == "":
                        displayValue = value[0]

                    else:
                        if value[1][:17] == "[<b>Unplugged</b>":
                            tmpSplit = value[1].split("]")
                            formatValue += tmpSplit[0] + "]"
                            displayValue = ""
                            for i in range(1, len(tmpSplit)):
                                displayValue += ']' + tmpSplit[i]

                        else:
                            displayValue = value[1]
                            if addLinkOpenFile:
                                displayValue += " " + self.htmlLinkSystemRun % {"uri": value[1]}

                            if addLinkOpenLocation:
                                displayValue += " " + self.htmlLinkOpenLocation % {"uri": os.path.dirname(value[1])}

                            if addLinkDelete:
                                displayValue += " " + self.htmlLinkDelete % {"uri": value[1]}

                    formatValue += "<a title=\"%s\" href=\"%s\">%s</a>" % (value[0], value[0], displayValue)

                elif addImage:
                    formatValue += "<img title=\"%s\" src=\"%s\" border=\"0\" hspace=\"0\" vspace=\"0\" style=\"width: 100%%;\"><br />" % (value[1], value[1])

                else:
                    formatValue += value[1]

                if addOpenKIO:
                    formatValue += " " + self.htmlLinkOpenKIO % {"uri": KIOName + ":/" + value[1]}

                if addSearch:
                    formatValue += " " + self.htmlLinkSearch % {"uri": "%s:+'%s'" % (searchTerm, value[1])}

                if addOpenFile:
                    valuesTmp = self.readValues(resource, 'nie:url')
                    if valuesTmp != [] and valuesTmp[0] != [] and valuesTmp[0][1] != "":
                        if valuesTmp[0][1][:17] != "[<b>Unplugged</b>":
                            formatValue += " " + self.htmlLinkSystemRun % {"uri": valuesTmp[0][1]}

                if addOpenLocation:
                    valuesTmp = self.readValues(resource, 'nie:url')
                    if valuesTmp != [] and valuesTmp[0] != [] and valuesTmp[0][1] != "":
                        if valuesTmp[0][1][:17] != "[<b>Unplugged</b>":
                            url = os.path.dirname(valuesTmp[0][1])
                            formatValue += " " + self.htmlLinkOpenLocation % {"uri": url}

            if variable[:7].lower() == "sparql:":
                data = data.replace("{SPARQL}" + variable[7:] + "{/SPARQL}", formatValue)
                variable = variable[7:]

            else:
                data = data.replace("{" + variable + "}", formatValue)

            for i in range(0, len(optionalsEmpty)):
                optionals[i] = optionals[i].replace("{SPARQL}" + variable + "{/SPARQL}", formatValue)
                optionals[i] = optionals[i].replace("{" + variable + "}", formatValue)
                optionalsEmpty[i] = optionalsEmpty[i].replace("{SPARQL}" + variable + "{/SPARQL}", "")
                optionalsEmpty[i] = optionalsEmpty[i].replace("{" + variable + "}", "")

        # Empty optionals are eliminated.
        for i in range(0, len(optionalsEmpty)):
            data = data.replace("%[" + optionalsEmpty[i] + "%]", "")

        # Remove brackets from not empty optionals.
        for i in range(0, len(optionals)):
            data = data.replace("%[" + optionals[i] + "%]", optionals[i])

        return data.strip()


    def getResourceIcons(self, uri, iconsAssociated):
        icons = ""
        for i in _CONST_ICONS_LIST:
            if (i & iconsAssociated):
                if (i == _CONST_ICON_DOLPHIN):
                    icons += self.htmlLinkDolphin % {"uri": uri}

                elif (i == _CONST_ICON_KONQUEROR):
                    icons += self.htmlLinkKonqueror % {"uri": uri}

                elif (i == _CONST_ICON_PROPERTIES):
                    icons += self.htmlLinkProperties % {"uri": uri}

                elif (i == _CONST_ICON_REMOVE):
                    icons += self.htmlLinkRemove % {"uri": uri, "hotkey": ""}

                elif (i == _CONST_ICON_SYSTEM_RUN):
                    icons += self.htmlLinkSystemRun % {"uri": uri}

            #else:
                #pass

        return icons


    def formatHtmlLine(self, uri):
        if INTERNAL_RESOURCE_IN_RESULTS_LIST:
            resource = cResource(uri)

        else:
            resource = Nepomuk.Resource(uri)

        if USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE and not INTERNAL_RESOURCE_IN_RESULTS_LIST:
            itemType = NOCR(cResource(uri).type())

        else:
            itemType = NOCR(resource.type())

        idx = lindex(self.ontologyFormat, itemType, column = 0)
        if (idx == None):
            idx = 0

        isValid = False
        for i in range(1, self.columnsCount + 1):
            exec "pattern = self.ontologyFormat[%s][%s]" % (idx, i)
            if vartype(pattern) == "int":
                exec "column%s = self.getResourceIcons(toUnicode(uri), pattern)" % i

            else:
                if pattern == "{type}":
                    exec "column%s = \"<b title='%s'>\" + ontologyToHuman(itemType) + \"</b>\"" % (i, itemType)

                else:
                    exec "column%s = self.formatResource(resource, pattern)" % i
                    isValid = True

        if isValid:
            #TODO: columnsformat, this must be automatic.
            line = self.htmlTableRow % (column1, column2, column3)

        else:
            line = ""

        resource = None

        return line


    def formatAsHtml(self, param1 = None, structure = [], queryTime = 0, stdout = False):
        if self.searchString[:9] == "nepomuk:/":
            return self.formatResourceInfo()

        if ((self.searchString.find('--playlist') >= 0) or (self.searchString.find('--playmixed') >= 0)):
            return self.formatAsHtmlPlaylist()

        htmlQueryTime = time.time()

        text = self.htmlHeader % ("Query results", "")
        text += self.htmlTableHeader

        if vartype(param1) == "list":
            if self.data == []:
                self.data = list(param1)
                self.structure = list(structure)

            rowsToRender = self.renderSize

        else:
            if param1 == "all":
                rowsToRender = len(self.data) # No calculations, a number that always work.

            elif param1 == "more":
                rowsToRender = self.renderSize

            else:
                rowsToRender = 0

        # If remains less than self.renderSize half then renders all.
        if ((len(self.data) - self.renderedDataRows - rowsToRender) < (self.renderSize / 2)):
            rowsToRender = len(self.data) # No calculations, a number that always work.

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
                    try:
                        line = self.formatHtmlLine(uri)

                    except:
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

        rowNavigation = ""
        if self.renderedDataRows < len(self.data):
            rowNavigation = '<tr><td><a href="render:/more">%s more</a>, <a href="render:/all">all records</a></td>' \
                    '<td>%s of %s records</td><td></td><tr>' \
                        % (min(self.renderSize, len(self.data) - self.renderedDataRows), self.renderedDataRows, len(self.data))


        text += rowNavigation +  self.renderedDataText + rowNavigation

        text += self.htmlTableFooter
        text += "<br />\n" + self.htmlStadistics \
                    % {'records': len(self.data), \
                        'seconds': queryTime, \
                        'sechtml': time.time() - htmlQueryTime}

        text += "<div class=\"bottom\" style=\"clear: both;\">\n" \
                    + self.htmlProgramInfo \
                    + "</div>\n" \
                    + self.htmlFooter

        return text


    def formatAsHtmlPlaylist(self, mode = 'playlist', param1 = None, structure = [], queryTime = 0, stdout = False):
        if self.searchString[:9] == "nepomuk:/":
            return self.formatResourceInfo()

        if param1 == None:
            return self.renderedDataText

        htmlQueryTime = time.time()

        if vartype(param1) != "list":
            raise Exception('error')

        if self.data == []:
            self.data = list(param1)
            self.structure = list(structure)

        rowsToRender = self.renderSize

        script = ""
        output = self.htmlHeader % ('Playlist viewer', script) \
                    + '<b title=\"Título\"><h2>Playlist viewer</b>&nbsp;</h2>\n<hr>\n'

        output = toUnicode(output)

        # Build playlist here.
        nfoVideo = NOC('nfo:Video')
        nieUrl = NOC('nie:url')
        nieTitle = NOC('nie:title')
        nmmMusicPiece = NOC('nmm:MusicPiece')

        audios = []
        images = []
        videos = []
        count = 0
        if len(self.data) > 0:
            lines = u""
            for item in self.data:
                url = title = ""
                if INTERNAL_RESOURCE:
                    resource = cResource(item[0])

                else:
                    resource = Nepomuk.Resource(QUrl(item[0]))

                if resource.hasProperty(nieUrl):
                    url = fromPercentEncoding(toUnicode(resource.property(nieUrl).toString().toUtf8()))
                    ext = os.path.splitext(url)[1][1:].lower()
                    if ((ext != '') and fileExists(url)):
                        if ext in self.supportedImageFormats:
                            if not url in images:
                                images += [[url, item[0]]]

                        elif ext in self.supportedAudioFormats:
                            if lindex(audios, url) == None:
                                audios += [[url, item[0]]]

                        elif ext in self.supportedVideoFormats:
                            if lindex(videos, url) == None:
                                videos += [[url, item[0]]]

                    count += 1

                resource = None

        if count == 0:
            output += "<b>There is no multimedia data to display.</b>\n"

        else:
            if (mode == 'playmixed'):
                mode = 'playlist'
                audios += videos
                videos = []

            if len(audios) > 0:
                output += self.buildPlaylist(audios, 'audio')

            for item in images:
                lines += u"Image: %s<br />\n" % item[0]

            if len(videos) > 0:
                output += self.buildPlaylist(videos, 'video')

        output += self.htmlTableFooter
        output += "<br />\n" + self.htmlStadistics \
                    % {'records': len(self.data), \
                        'seconds': queryTime, \
                        'sechtml': time.time() - htmlQueryTime}
        output += "<div class=\"bottom\" style=\"clear: both;\">\n" \
                    + self.htmlProgramInfo \
                    + "</div>\n" \
                    + self.htmlFooter

        if stdout:
            print toUtf8(output)

        self.renderedDataText = output

        return output


    def formatResourceInfo(self, uri = "", knownShortcuts = [], ontologyValueTypes = [], stdout = False):
        if uri == "":
            return self.renderedDataText

        query = "SELECT DISTINCT ?ont ?val\n" \
                "WHERE {\n" \
                    "\t<" + uri + "> ?ont ?val ; nao:userVisible 1 .\n"\
                "}\n"
        if stdout:
            print toUtf8(query)

        script = ""
        if self.enableImageViewer:
            script += SCRIPT_IMAGE_VIEWER
            imageViewer = "<img title=\"%(url)s\" src=\"%(url)s\" style=\"width:600px;\" "\
                            "onLoad=\"new viewer({image: this, frame: ['600px','400px']});\"/>"

        if self.videojsEnabled:
            script += "<link href=\"http://vjs.zencdn.net/c/video-js.css\" rel=\"stylesheet\" type=\"text/css\">\n" \
                        "<script src=\"http://vjs.zencdn.net/c/video.js\"></script>\n"

        output = self.htmlHeader % ('Resource viewer', script)
        output += "<div class=\"top\" style=\"static: top;\">\n"
        output += '<b title=\"%(uri)s\"><h2><a title)=\"%(uri)s\" href=\"%(uri)s\">Resource viewer</a></b>&nbsp;%(remove)s<reindex />&nbsp;&nbsp;%(navigator)s<cached /></h2>\n' \
                        % {'uri': uri, "remove": self.htmlLinkRemove % {"uri": uri, "hotkey": " (Ctrl+Del)"}, "navigator": self.htmlRenderLink("navigator")}
        output += "</div>\n"
        output += "<div class=\"data\" style=\"float: left; width: 500px;\">\n<hr>"
        output += self.htmlViewerTableHeader

        data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        if data.isValid():
            processedData = []
            images = []
            audios = []
            videos = []
            if INTERNAL_RESOURCE or USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE:
                mainResource = cResource(uri, False, False) # prefechData = useCache = False
                defaultType = NOCR(mainResource.type())

            else:
                if nepoogle.clearResourceManagerCache:
                    Nepomuk.ResourceManager.instance().clearCache()

                mainResource = Nepomuk.Resource(uri)
                defaultType = NOCR(mainResource.type())

            while data.next():
                currOnt = NOCR(data["ont"].toString())
                if currOnt in self.hiddenOntologies:
                    continue

                ontInfo = ontologyInfo(data["ont"].toString(), self.model)
                value = self.fmtValue(toUnicode(data["val"].toString()), ontInfo[2])
                if value[:9] == 'nepomuk:/':
                    if INTERNAL_RESOURCE:
                        resource = cResource(value)

                    else:
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

                    elif resource.type() == NOC('nmm:TVSeason'):
                        ontLabel = currOnt + '->nmm:seasonNumber'
                        seasonNumber = "%d" % self.readProperty(resource, 'nmm:seasonNumber', 'int')
                        value = '<!--' + toUnicode(seasonNumber) + '-->' \
                                    + self.htmlRenderLink('uri', resource.uri(), seasonNumber)

                    elif resource.hasType(NOC('rdfs:Resource', True)):
                        ontLabel = ''
                        ext = os.path.splitext(toUnicode(resource.genericLabel()))[1][1:].lower()
                        if ext != '' and ext in self.supportedImageFormats:
                            if resource.hasProperty(NOC('nie:url')):
                                url = toUnicode(resource.property(NOC('nie:url')).toString())
                                if not url in images:
                                    images += [url]

                    else:
                        value = toUnicode(resource.type())

                    if value == '':
                        shorcut = lvalue(knownShortcuts, ontLabel, 0, 1)
                        if shorcut == None:
                            shorcut = ontLabel

                        genericLabel = toUnicode(resource.genericLabel())
                        value = '<!--' + genericLabel + '-->' \
                                + self.htmlRenderLink('uri', resource.uri(), genericLabel)
                        if ((genericLabel[:7] == "http://") or (genericLabel[:8] == "https://")) \
                                and (genericLabel.find(" ") < 0):
                                # Seems a url so a link to the url could be great.
                                value += " <a title=\"%s\" href=\"%s\"><img src=\"file://%s\"></a>" \
                                            % (genericLabel, genericLabel, self.iconEmblemLink)

                        if ontLabel != '':
                            value += ' ' + self.htmlRenderLink('ontology', shorcut, resource.genericLabel())

                elif currOnt == 'rdf:type':
                    value = NOCR(value)
                    if value == defaultType:
                        value = '<em>' + value + '</em>'

                elif currOnt == 'nie:url':
                    url = fromPercentEncoding(value)
                    ext = os.path.splitext(url)[1][1:].lower()
                    if ((ext != '') and fileExists(url)):
                        if ext in self.supportedImageFormats:
                            if not url in images:
                                images += [url]

                        elif ext in self.supportedAudioFormats:
                            if lindex(audios, url) == None:
                                audios += [[url, uri]]

                        elif ext in self.supportedVideoFormats:
                            if lindex(videos, url) == None:
                                videos += [[url, uri]]

                    value = ''
                    if url[:7] == 'file://':
                        value += "<a title=\"%(url)s\" href=\"%(url)s\">%(url)s</a>" % {"url": url}
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

                    else:
                        value += self.htmlRenderLink('url', url, url)

                    # Adding reindex button to navigator bar.
                    output = output.replace("<reindex />", \
                                            "&nbsp;<a title=\"Reindex file\" href=\"reindex:/%(url)s\"><img %(style)s title=\"Reindex file\" src=\"file://%(icon)s\"></a>" \
                                            % {"style": self.htmlStyleNavigate, "url": url, "icon": self.iconReindex}
                                        )

                elif currOnt == 'nmm:genre':
                    value = value + ' ' + self.htmlRenderLink('ontology', 'genre', value)

                elif (currOnt in ("nco:fullname", "nie:title")):
                    value = value + ' ' + self.htmlRenderLink('googlesearch', value)

                else:
                    try:
                        # Must check for full paths to avoid file detection in execution path.
                        if (((value[0] == "/") or (value[:7] == "file://")) and fileExists(value)):
                            ext = os.path.splitext(value)[1][1:].lower()
                            if ext != '' and ext in self.supportedImageFormats:
                                if not value in images:
                                    images += [value]

                            if value[:7] != 'file://':
                                value = 'file://' + value

                            value = '<a title=\"%(url)s\" href=\"%(url)s\">%(name)s</a>' \
                                        % {'url': value, 'name': os.path.basename(value)}

                        else:
                            # No es un fichero así que añadimos los linksitem[3] si hay urls.
                            value = value.replace("\n", "<br />")
                            value = value.replace("\r", "<br />")
                            value = addLinksToText(value)

                    except:
                        value = ""

                if value != '':
                    #processedData += [[currOnt, ontologyToHuman(currOnt), value]]
                    processedData += [[currOnt, ontologyToHuman(ontInfo[1]), value]]

        text = ''
        if len(processedData) > 0:
            processedData = sorted(processedData, key=lambda row: row[1] + row[2])
            oldOnt = ''
            for row in processedData:
                if (oldOnt != row[1]):
                    if text != '':
                        text += '</td></tr>\n'

                    text += '<tr><td valign=\"top\" width=\"120px\">' \
                            '<a href="delprop:/%s&%s"><img %s src=\"file://%s\"></a><b title=\"%s\">%s</b>:</td><td>%s' \
                                % (uri, row[0], self.htmlStyleIcon, self.iconListRemove, row[0], row[1], row[2])
                    oldOnt = row[1]

                else:
                    text += ', ' + row[2]

        if text == '':
            output += '<p>No data found for the uri %s.</p>\n' % uri

        else:
            # Hacks for resources.
            if defaultType == "nco:Contact":
                # Adding the header.
                ontologySymbol = NOC(ONTOLOGY_SYMBOL)
                if mainResource.hasProperty(ontologySymbol):
                    symbols = mainResource.property(ontologySymbol).toStringList()
                    symbol = self.readProperty(symbols[0], "nie:url", "str")
                    #symbol = symbols[0]
                    try:
                        if (((symbol[0] == "/") or (symbol[:7] == "file://")) and fileExists(symbol)):
                            ext = os.path.splitext(symbol)[1][1:].lower()
                            if ext != '' and ext in self.supportedImageFormats:
                                if symbol[:7] != 'file://':
                                    symbol = 'file://' + symbol

                                fullname = toUnicode(mainResource.property(NOC("nco:fullname")).toString())
                                resourceIsA = self.resourceIsA(mainResource)
                                output += '<img %(fmt)s title=\"%(title)s\" src=\"%(url)s\"><h2>%(fullname)s</h2><b>%(resourceIsA)s</b>' \
                                            % {"fmt": "style=\"float:left; vertical-align:text-top; width: 100px\" border=\"2px\" hspace=\"10px\" vspace=\"0\"", \
                                                'url': symbol, 'title': os.path.basename(symbol), "fullname": fullname, "resourceIsA": resourceIsA}

                                print "hay symbol"

                            else:
                                print "no hay symbol"
                                symbol = ""

                    except:
                        symbol = self.iconDelete

            output += text

        # Reverse resources.
        query = "select ?uri ?ont\n" \
                "   where { " \
                "       ?uri ?ont <%s> ; nao:userVisible 1 . " \
                "}" \
                "order by ?ont" % uri
        data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
        reverseResourcesItems = []
        reverseResourcesList = []
        if data.isValid():
            while data.next():
                resUri = toUnicode(data["uri"].toString())
                if INTERNAL_RESOURCE:
                    res = cResource(resUri)

                else:
                    res = Nepomuk.Resource(resUri)

                #val = fromPercentEncoding(toUnicode(res.genericLabel()))
                url = None
                if res.type() == NOC('nmm:TVSeason'):
                    val = "%d" % self.readProperty(res, 'nmm:seasonNumber', 'int')

                else:
                    val = toUnicode(res.genericLabel())
                    if res.hasProperty(NOC('nie:url')):
                        url = toUnicode(res.property(NOC('nie:url')).toString())

                    else:
                        url = None

                reverseResourcesItems += [[resUri, NOCR(data["ont"].toString()), val, url]]

            tmpOutput = ''
            if len(reverseResourcesItems) > 0:
                reverseResourcesItems = sorted(reverseResourcesItems, key=lambda revRes: revRes[1] + revRes[2])
                oldOnt = ''
                for item in reverseResourcesItems:
                    if oldOnt != item[1]:
                        if tmpOutput != "":
                            tmpOutput = tmpOutput.replace('</a><', '</a>, <')
                            reverseResourcesList[-1][1] = reverseResourcesList[-1][1] + tmpOutput
                            tmpOutput = ""

                        reverseResourcesList += [[item[1], '\n<hr>\n<tr><td valign=\"top\" width=\"100px\"><b title=\"%s\">%s</b>:</td><td>' \
                                    % (item[1], ontologyToHuman(item[1], True))]]
                        oldOnt = item[1]

                    tmpOutput += '<!-- ' + item[2] + '-->' \
                                    + self.htmlRenderLink('uri', item[0], item[2])

                    url = item[3]
                    if ((url != None) and fileExists(url)):
                        ext = os.path.splitext(url)[1][1:].lower()
                        if ext in self.supportedImageFormats:
                            if not url in images:
                                images += [url]

                        elif ext in self.supportedAudioFormats:
                            if lindex(audios, url) == None:
                                audios += [[url, item[0]]]

                        elif ext in self.supportedVideoFormats:
                            if lindex(videos, url) == None:
                                videos += [[url, item[0]]]

                tmpOutput = tmpOutput.replace('</a><', '</a>, <')
                reverseResourcesList[-1][1] = reverseResourcesList[-1][1] + tmpOutput + '</td></tr>\n'

        for item in reverseResourcesList:
            if defaultType == "nmm:MusicAlbum" and item[0] in ("nmm:musicAlbum", "_no_nao:hasSubResource"):
                # Don't print for music albums this reverse resources.
                pass

            else:
                output += item[1]

        output += self.htmlViewerTableFooter
        output += "</div>\n"

        if len(audios) + len(images) + len(videos) > 0:
            output += "<div class=\"preview\" style=\"float: left;\">"
            output += "<hr><h3><b>Preview</b></h3>\n"

        # Resource audios.
        if len(audios) > 0:
            #output += "<div class=\"preview\" style=\"float: left;\">"
            # Dirty hack for support covers and playlist in nmm:MusicAlbum.
            if defaultType == "nmm:MusicAlbum":
                output += "<b>Album cover</b><br />"
                output += '<img title=\"%(url)s\" style=\"height:auto;width:250px;scalefit=1\" src=\"%(url)s\"><br />\n' \
                                % {'url': self.getCoverUrl(mainResource, audios[0][0])}
                output += "<br />\n"

            output += self.buildPlaylist(audios, 'audio')
            #output += "\n</div>\n"

        # Resource videos.
        if len(videos) > 0:
            #output += "<div class=\"preview\" style=\"float: left;\">"
            output += self.buildPlaylist(videos, 'video')
            #output += "\n</div>\n"

        # Resource images.
        if len(images) > 0:
            if len(audios) + len(videos) > 0:
                output += "<br />"

            for url in sorted(images):
                if url[:7] != 'file://':
                    url = 'file://' + url

                if self.enableImageViewer:
                    output += imageViewer % {'url': url}

                else:
                    output += '<img title=\"%(url)s\" style=\"height:auto;width:400px;scalefit=1\" src=\"%(url)s\"><br />\n' \
                                % {'url': url}
                output += "<b>File name</b>:<title>%s</title><em>%s</em><br />" % (url, os.path.basename(url))
                #output += "\n</div>\n"

        if len(audios) + len(images) + len(videos) > 0:
            output += "\n</div>\n"

        output += "<div class=\"bottom\" style=\"clear: both;\">\n" \
                    + self.htmlProgramInfo \
                    + "</div>\n" \
                    + self.htmlFooter

        if stdout:
            print toUtf8(output)

        self.renderedDataText = output

        return output


    def formatData(self, data = [], structure = [], queryTime = 0, stdout = False):
        if self.outFormat == 1:
            return self.formatAsText(data = [], structure = [], queryTime = 0, stdout = False)

        elif self.outFormat == 2:
            return self.formatAsHtml(data = [], structure = [], queryTime = 0, stdout = False)

        else:
            return ""

#END cldataformat.py
