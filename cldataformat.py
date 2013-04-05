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

import __builtin__
import datetime, fractions, os, re

from PyKDE4.kdeui import KIconLoader
from PyKDE4.nepomuk2 import Nepomuk2
from PyKDE4.soprano import Soprano

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
    #hiddenOntologies = ["kext:unixFileGroup", "kext:unixFileMode", "kext:unixFileOwner", "nao:userVisible", "nao:annotation", "rdfs:comment", "nie:relatedTo"]
    hiddenOntologies = ["kext:unixFileGroup", "kext:unixFileMode", "kext:unixFileOwner", "nao:userVisible"]
    #hiddenOntologiesInverse = [NOC("nao:hasSubResource", False), NOC("dces:contributor", False), NOC("nco:contributor", False)]
    hiddenOntologiesInverse = [NOC("nao:hasSubResource", False)]
    model = None
    navegable = False
    ontologyMusicAlbumCover = NOC(ONTOLOGY_MUSIC_ALBUM_COVER, True)
    outFormat = 1  # 1- Text, 2- Html
    playlistShowWithOneElement = True
    playlistDescendingOrderInAlbumYear = True
    queryString = ""
    renderSize = 50
    renderedDataRows = 0
    renderedDataText = ""
    skippedOntologiesInResourceIsA = [NOC("nao:hasSubResource", False)]
    structure = []
    uri = None
    videojsEnabled = False

    # Sizes
    screenWidth = 800
    viewerColumnsWidth = (screenWidth - 100) / 2
    playlistHeight = 200
    playlistScrollHeight = 50
    playlistWidth = viewerColumnsWidth
    videoWidth = viewerColumnsWidth
    videoHeight = int(0.5625*viewerColumnsWidth)

    supportedAudioFormats = ("flac", "mp3", "ogg", "wav")
    supportedImageFormats = QImageReader.supportedImageFormats() + ["nef"]
    supportedVideoFormats = ("avi", "divx", "flv", "mkv", "mp4", "mpeg", "mpg", "tp", "ts", "vob", "webm", "wmv")

    iconDelete = toUnicode(KIconLoader().iconPath('edit-delete', KIconLoader.Small))
    iconDocumentInfo = toUnicode(KIconLoader().iconPath('documentinfo', KIconLoader.Small))
    iconDocumentProp = toUnicode(KIconLoader().iconPath('document-properties', KIconLoader.Small))
    iconEmblemLink = toUnicode(KIconLoader().iconPath('emblem-link', KIconLoader.Small))
    iconFileManager = toUnicode(KIconLoader().iconPath('system-file-manager', KIconLoader.Small))
    iconKIO = toUnicode(KIconLoader().iconPath('kde', KIconLoader.Small))
    iconKonqueror = toUnicode(KIconLoader().iconPath('konqueror', KIconLoader.Small))
    iconListAdd = toUnicode(KIconLoader().iconPath('list-add', KIconLoader.Small))
    #iconListRemove = toUnicode(KIconLoader().iconPath('list-remove', KIconLoader.Small))
    iconNavigateFirst = toUnicode(KIconLoader().iconPath('go-first', KIconLoader.Small))
    iconNavigateLast = toUnicode(KIconLoader().iconPath('go-last', KIconLoader.Small))
    iconNavigateNext = toUnicode(KIconLoader().iconPath('go-next', KIconLoader.Small))
    iconNavigatePrevious = toUnicode(KIconLoader().iconPath('go-previous', KIconLoader.Small))
    iconNoCover = toUnicode(KIconLoader().iconPath('no_cover', KIconLoader.Desktop))
    iconNoPhoto = toUnicode(KIconLoader().iconPath('no_photo', KIconLoader.Desktop))
    iconNoSymbol = toUnicode(KIconLoader().iconPath('no_symbol', KIconLoader.Desktop))
    iconNoVideoThumbnail = toUnicode(KIconLoader().iconPath('no_video_thumbnail', KIconLoader.Desktop))
    iconPlaylistFirst = toUnicode(KIconLoader().iconPath('go-first-view', KIconLoader.Small))
    iconPlaylistPrevious = toUnicode(KIconLoader().iconPath('go-previous-view', KIconLoader.Small))
    iconPlaylistNext = toUnicode(KIconLoader().iconPath('go-next-view', KIconLoader.Small))
    iconPlaylistLast = toUnicode(KIconLoader().iconPath('go-last-view', KIconLoader.Small))
    iconProcessIdle = toUnicode(KIconLoader().iconPath('process-idle', KIconLoader.Small))
    iconRatingEmpty = toUnicode(KIconLoader().iconPath('rating_empty', KIconLoader.Small))
    iconRatingFull = toUnicode(KIconLoader().iconPath('rating_full', KIconLoader.Small))
    iconRatingHalf = toUnicode(KIconLoader().iconPath('rating_half', KIconLoader.Small))
    iconReindex = toUnicode(KIconLoader().iconPath('nepomuk', KIconLoader.Small))
    iconSystemRun = toUnicode(KIconLoader().iconPath('system-run', KIconLoader.Small))
    iconSystemSearch = toUnicode(KIconLoader().iconPath('system-search', KIconLoader.Small))
    iconSystemSearchWeb = toUnicode(KIconLoader().iconPath('edit-web-search', KIconLoader.Small))
    iconUnknown = toUnicode(KIconLoader().iconPath('unknown', KIconLoader.Small))

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
    htmlLinkNavigateFirst = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s/navbutton\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "first", "hotkey": "Ctrl+PgUp", "style": htmlStyleNavigate, "icon": iconNavigateFirst}
    htmlLinkNavigateLast = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s/navbutton\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "last", "hotkey": "Ctrl+PgDown", "style": htmlStyleNavigate, "icon": iconNavigateLast}
    htmlLinkNavigatePrevious = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s/navbutton\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
                            % {"to": "previous", "hotkey": "Ctrl+Left", "style": htmlStyleNavigate, "icon": iconNavigatePrevious}
    htmlLinkNavigateNext = "<a title=\"Go %(to)s (%(hotkey)s)\" href=\"navigate:/%(to)s/navbutton\"><img %(style)s title=\"Go %(to)s (%(hotkey)s)\" src=\"file://%(icon)s\"></a>" \
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
    htmlLinkRemoveAll = "<a title=\"Remove all listed resources\" href=\"remove:/all\">" \
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
                            "{pimo:tagLabel|l}%[<br />Alternative labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nao:Agent", \
                            "{uri|l|of}%[<br /><b>Identifier</b>: {nao:identifier}%] %[<b>Label</b>: {nao:prefLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nao:Tag", \
                            "%[<img width=48 style='float:left; vertical-align:text-bottom;' src=\"{nao:hasSymbol->nie:url|1}\"'>%]" \
                            "{nao:prefLabel|l|of|ol|s:hasTag}%[<br />Alternative labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nco:Contact", \
                            "%[<img width=48 style='float:left; vertical-align:text-bottom;' src=\"{nco:photo->nie:url|1}\"'>%]" \
                                "{nco:fullname|l|s:contact}%[<br />Preferred label: {nao:prefLabel}%]%[<br />Alternative labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nco:IMAccount", \
                            "%[<img width=48 style='float:left; vertical-align:text-bottom;' src=\"{nco:photo->nie:url|1}\"'>%]" \
                                "{nco:imNickname|l}%[ ({nco:imID})%]%[<br />Type: {nco:imAccountType}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nco:PersonContact", \
                            "%[<img width=48 style='float:left; vertical-align:text-bottom;' src=\"{nco:photo->nie:url|1}\"'>%]" \
                                #"{nco:fullname|l|s:contact}%[<br />Preferred label: {nao:prefLabel}%]%[<br />Alternative labels: {nao:altLabel}%]" \
                                "{nco:hasIMAccount->nco:imNickname|l}%[ ({nco:hasIMAccount->nco:imID})%]%[<br />Account type: {nco:hasIMAccount->nco:imAccountType}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nexif:Photo", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Audio", \
                            "{nfo:fileName|l|of|ol}%[<br />Title: {nie:title}%]%[<br />url: {nie:url}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:Archive", \
                            "{nie:url|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE], \
                        ["nfo:ArchiveItem", \
                            "{nie:url|l|of|ol}%[<br />Title: {nie:title}%]", \
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
                        ["nfo:RemoteDataObject", \
                            "{nie:url|l|of}%[<br /><b>Title</b>: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_SYSTEM_RUN], \
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
                        ["nie:InformationElement", \
                            "{nfo:fileName|l|of|ol}%[<br />Alternative labels: {nao:altLabel}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nmm:Movie", \
                            "%[<img width=48 style='float:left; vertical-align:text-bottom;' src=\"{nfo:depiction->nie:url|1}\"'>%]" \
                            "<b>Title</b>: {nie:title|l|of|ol}" \
                                "%[<br /><b>Alternative titles</b>: {nao:altLabel}%]" \
                                "%[<br /><b>Rating</b>: {nao:numericRating}%]" \
                                "<br /><b>Actors</b>: {SPARQL}SELECT DISTINCT ?uri ?value WHERE { <%(uri)s> nmm:actor ?uri . ?uri nco:fullname ?value . } ORDER BY ?value|l|s:actor{/SPARQL}" \
                                "%[<br /><b>Description</b>: {nie:description}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE + _CONST_ICON_DOLPHIN + _CONST_ICON_KONQUEROR], \
                        ["nmm:MusicAlbum", \
                            "%[<img width=48 style='float:left; vertical-align:text-bottom;' src=\"{nmm:artwork->nie:url|1}\"'>%]" \
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
                            "<b>Title</b>: {nao:prefLabel}<br /><b>Season</b>: {nmm:seasonNumber|l} of {nmm:seasonOf->nie:title|l} ", \
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
                        ["rdfs:Resource", \
                            "{nie:url|l|of|ol}%[<br />Title: {nie:title}%]", \
                            "{type}", \
                            _CONST_ICON_PROPERTIES + _CONST_ICON_REMOVE] \
                    ]


    def __init__(self, searchString = "", model = None, screenWidth = 1024, renderedDataText = None):
        self.searchString = searchString
        if model == None:
            if DO_NOT_USE_NEPOMUK:
                self.model = Soprano.Client.DBusModel('org.kde.NepomukStorage', '/org/soprano/Server/models/main')

            else:
                self.model = Nepomuk2.ResourceManager.instance().mainModel()

        else:
            self.model = model

        self.screenWidth = screenWidth
        self.viewerColumnsWidth = (self.screenWidth - 100) / 2
        self.playlistWidth = self.viewerColumnsWidth
        self.videoWidth = self.viewerColumnsWidth
        self.videoHeight = int(0.5625*self.viewerColumnsWidth)

        if (renderedDataText != None):
            self.renderedDataText = renderedDataText


    def getCoverUrl(self, res = None, url = "", useHtmlEncoding = True):
        if res in (None, ""):
            return ""

        if vartype(res) in ("str", "unicode", "QString", "QVariant"):
            if INTERNAL_RESOURCE:
                res = cResource(res)

            else:
                res = Nepomuk2.Resource(res)

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
                    resTmp = Nepomuk2.Resource(uri)

                tmpCoverUrl = self.readProperty(resTmp, 'nie:url', 'str')
                if tmpCoverUrl[:7] == "file://":
                    tmpCoverUrl = tmpCoverUrl[7:]

                if ((tmpCoverUrl != "") and fileExists(tmpCoverUrl)):
                    if useHtmlEncoding:
                        coverUrl = urlHtmlEncode(tmpCoverUrl)

                    else:
                        coverUrl = tmpCoverUrl

                    break

        # If there is no property then let's try to locate using tracks location.
        if coverUrl == self.iconNoCover:
            if url == "":
                # We must obtain the url from one of the album tracks.
                #query = "select ?uri\n" \
                #        "   where {\n" \
                #        "       ?uri nao:hasSubResource <%s> ; nao:userVisible 1 .\n" \
                #        "}\n" % toUnicode(res.uri())
                query = "select ?uri\n" \
                        "   where {\n" \
                        "       ?uri nie:isLogicalPartOf <%s> .\n" \
                        "}\n" % toUnicode(res.uri())
                data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparql)
                if data.isValid():
                    while data.next():
                        resUri = toUnicode(data["uri"].toString())
                        if INTERNAL_RESOURCE:
                            resTrack = cResource(resUri)
                            resType = NOCR(resTrack.type())

                        else:
                            resTrack = Nepomuk2.Resource(resUri)
                            if USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE:
                                resType = NOCR(cResource(resUri).type())

                            else:
                                resType = NOCR(resTrack.type())

                        if (resType == "nmm:MusicPiece"):
                            url = toUnicode(self.readProperty(resTrack, 'nie:url', 'str'))
                            break

            if (url != ""):
                if url[:7] == "file://":
                    url = url[7:]

                url = os.path.dirname(url)
                for coverName in ('cover.png', 'Cover.png', 'cover.jpg', 'Cover.jpg'):
                    tmpCoverUrl = url + '/' + coverName
                    if fileExists(tmpCoverUrl):
                        if useHtmlEncoding:
                            coverUrl = urlHtmlEncode(tmpCoverUrl)

                        else:
                            coverUrl = tmpCoverUrl

                        break

        return "file://" + coverUrl


    def getOrientationHtml(self, orientation = 1, size = 48):
        if (vartype(orientation) == "Resource"):
            orientation = rating.property(NOC("nexif:orientation", True))

        if not (vartype(orientation) in ("int", "long")):
            try:
                orientation = int(orientation)

            except:
                orientation = 1

        if ((orientation < 1) or (orientation > 8)):
            orientation = 1

        propertyName = 'iconOrientation%s' % orientation
        if hasattr(self, propertyName):
            icon = getattr(self, propertyName)

        else:
            icon = toUnicode(KIconLoader().iconPath('orientation_%s' % orientation, KIconLoader.Small))
            setattr(self, propertyName, icon)

        html = ""
        html += "<div class=\"orientation\">"
        html += "<img style=\"width:%spx\" src=\"file://%s\">" % (size, icon)
        html += "</div>"

        return html


    def getRatingHtml(self, rating = None, size = 32):
        #if (self.iconRatingEmpty == self.iconUnknown) \
        #        or (self.iconRatingFull == self.iconUnknown) \
        #        or (self.iconRatingHalf == self.iconUnknown):

        #    if (vartype(rating) == "Resource"):
        #        rating = rating.rating()

        #    return "<div class=\"rating\">%s%s</div>" % (rating, _(" (can't locate rating icons)"))
        #
        num_stars = 5
        full_count = half_count = 0
        empty_count = num_stars

        if (vartype(rating) == "Resource"):
            rating = rating.rating()

        if (vartype(rating) in ("int", "long")):
            full_count = min(rating/2, 5)
            half_count = min(rating - full_count*2, num_stars - full_count)
            empty_count = max(empty_count - full_count - half_count, 0)

        #starHtml = "<a href=\"setrating:/%s\"><img style=\"-webkit-filter: blur(2px) grayscale(1);\" src=\"file://%s\"></a>"
        starHtml = "<a href=\"setrating:/%%s\"><img style=\"width:%spx\" src=\"file://%%s\"></a>" % size
        html = ""
        html += "<div class=\"rating\">"
        i = 1
        for j in range(0, full_count):
            html += starHtml % (i*2-1, self.iconRatingFull)
            i += 1

        for j in range(0, half_count):
            html += starHtml % (i*2-2, self.iconRatingHalf)
            i += 1

        for j in range(0, empty_count):
            html += starHtml % (i*2, self.iconRatingEmpty)
            i += 1

        html += "</div>"

        return html


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
        queryResultSet = self.model.executeQuery(query, SOPRANO_QUERY_LANGUAGE)
        if queryResultSet.isValid():
            while queryResultSet.next():
                ontologies += [toUnicode(queryResultSet["p"].toString())]

        for ontology in ontologies:
            if not ontology in self.skippedOntologiesInResourceIsA:
                result += [ontologyInfo(ontology)[1]]

        # list -> to set (duplicates are removed) -> to list again.
        result = list(set(result))

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
            songSearch = ""
            url = item[0]
            if url[:7] != "file://":
                url = "file://" + url

            if INTERNAL_RESOURCE_IN_PLAYLIST:
                res = cResource(item[1])

            else:
                res = Nepomuk2.Resource(item[1])

            if listType == 'audio':
                trackNumber = self.readProperty(res, 'nmm:trackNumber', 'int')
                discNumber = self.readProperty(res, 'nmm:setNumber', 'int')
                trackName = self.readProperty(res, 'nie:title', 'str')
                if trackName == "":
                    trackName = os.path.basename(url)

                else:
                    songSearch = "&quot;%s&quot;" % urlHtmlEncode(trackName)

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
                if res.hasProperty(NOC('nmm:performer', True)):
                    if INTERNAL_RESOURCE_IN_PLAYLIST:
                        resUris = res.property(NOC('nmm:performer', True))
                        if vartype(resUris) != "list":
                            resUris = [resUris]

                    else:
                        resUris = res.property(NOC('nmm:performer', True)).toStringList()

                    for itemUri in resUris:
                        if INTERNAL_RESOURCE_IN_PLAYLIST:
                            resTmp = cResource(itemUri)

                        else:
                            resTmp = Nepomuk2.Resource(itemUri)

                        fullname = self.readProperty(resTmp, 'nco:fullname', 'str')
                        if fullname != None:
                            performers += [[itemUri, fullname]]
                            songSearch += " &quot;%s&quot;" % urlHtmlEncode(fullname)

                if (len(performers) > 0):
                    performers = sorted(performers, key=lambda item: toUtf8(item[1]))

                else:
                    performers = [[None, _("No performers")]]

                if performers == oldPerformers:
                    performers = []

                else:
                    oldPerformers = list(performers)

                # Album title.
                albumTitle = [None, "", 0, ""]
                if res.hasProperty(NOC('nmm:musicAlbum', True)):
                    if INTERNAL_RESOURCE_IN_PLAYLIST:
                        resUri = res.property(NOC('nmm:musicAlbum', True))
                        resTmp = cResource(resUri)

                    else:
                        resUri = res.property(NOC('nmm:musicAlbum', True)).toStringList()[0]
                        resTmp = Nepomuk2.Resource(resUri)

                    albumTitle = self.readProperty(resTmp, 'nie:title', 'str')

                    if albumTitle == None:
                        oldTitle = [None, "", 0, ""]

                    elif not (oldTitle[1] == albumTitle):
                        # Obtain album artists.
                        albumArtists = []
                        if resTmp.hasProperty(NOC('nmm:albumArtist', True)):
                            if INTERNAL_RESOURCE_IN_PLAYLIST:
                                resUris = resTmp.property(NOC('nmm:albumArtist', True))
                                if vartype(resUris) != "list":
                                    resUris = [resUris]

                            else:
                                resUris = resTmp.property(NOC('nmm:albumArtist', True)).toStringList()

                            for itemUri in resUris:
                                if INTERNAL_RESOURCE_IN_PLAYLIST:
                                    resTmp2 = cResource(itemUri)

                                else:
                                    resTmp2 = Nepomuk2.Resource(itemUri)

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
                    if (albumTitle[2] > 0):
                        linkTitle = "<a title='%(uri)s' href='%(uri)s'>%(title)s (%(year)s)</a>" \
                                        % {"uri": albumTitle[0], "title": albumTitle[1], "year": albumTitle[2]}

                    else:
                        linkTitle = "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                        % {"uri": albumTitle[0], "title": albumTitle[1]}

                    if albumTitle[3] != "":
                        linkTitle += " by " + albumTitle[3]

                    linkPerformers = ""
                    for performer in performers:
                        if linkPerformers != "":
                            linkPerformers += ",&nbsp;"

                        if (performer[0] == None):
                            linkPerformers += "%(title)s" % {"title": performer[1]}

                        else:
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

                        if (performer[0] == None):
                            linkPerformers += "%(title)s" % {"title": performer[1]}

                        else:
                            linkPerformers += "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                            % {"uri": performer[0], "title": performer[1]}

                    trackName = "<em>%s</em><br />%s" % (linkPerformers, trackName)

                if (coverUrl == None):
                    # Probably a video or a music file without tags. Use a thumbnail is exists.
                    if (os.path.splitext(url)[1][1:].lower() in self.supportedVideoFormats):
                        if coverUrl == None:
                            tmpCoverUrl = getThumbnailUrl(url)
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
                if res.hasProperty(NOC('nie:url', True)):
                    thumbnailUrl = getThumbnailUrl(toUnicode(self.readProperty(res, 'nie:url', 'str')))

                    if thumbnailUrl == None:
                        thumbnailUrl = "file://" + self.iconNoVideoThumbnail

                # Title.
                trackName = self.readProperty(res, 'nie:title', 'str')
                if ((trackName == None) or (trackName == "")):
                    dummyVal = os.path.basename(url)
                    sortColumn = dummyVal
                    trackName = "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                    % {"uri": toUnicode(res.uri()), "title": dummyVal}

                else:
                    sortColumn = trackName
                    trackName = "<a title='%(uri)s' href='%(uri)s'>%(title)s</a>" \
                                    % {"uri": toUnicode(res.uri()), "title": trackName}

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
                    if res.hasProperty(NOC('nuao:usageCount', True)):
                        if res.property(NOC('nuao:usageCount', True)).toString() == '1':
                            trackName += ' <b><em>(watched)</em></b>'

                    # Series title.
                    if res.hasProperty(NOC('nmm:series', True)):
                        if INTERNAL_RESOURCE:
                            resUri = res.property(NOC('nmm:series', True))
                            resTmp = cResource(resUri)

                        else:
                            resUri = res.property(NOC('nmm:series', True)).toStringList()[0]
                            resTmp = Nepomuk2.Resource(resUri)

                        if resTmp.hasProperty(NOC('nie:title', True)):
                            dummyVal = resTmp.property(NOC('nie:title', True)).toString()
                            sortColumn = dummyVal + sortColumn
                            trackName = "<em><a title='%(uri)s' href='%(uri)s'>%(title)s</a></em>: %(trackName)s" \
                                            % {"uri": toUnicode(resTmp.uri()), "title": dummyVal, "trackName": trackName}

                if thumbnailUrl != None:
                    trackName = "<img width=48 style='float:left; " \
                                    "vertical-align:text-bottom; margin:2px' " \
                                    "src='%s'>" % (thumbnailUrl) \
                                + trackName

                trackName = trackName.replace('"', '&quot;')

            playList += [[item[1], i, url, trackName, sortColumn, songSearch]]
            i += 1

        playList = sorted(playList, key=lambda item: toUtf8(item[4]))
        url = playList[0][2]
        if url[:7] == "file://":
            url = url[7:]

        if listType == 'audio':
            output += "<div class=\"audioplayer\">\n"
            output += "<b>Audio player</b><br />\n" \
                        "<audio id=\"%splayer\" " \
                            "src=\"file://%s\" controls preload>No audio support</audio><br />\n" \
                            % (listType, urlHtmlEncode(url))

        elif listType == 'video':
            output += "<div class=\"videoplayer\">\n"
            output += "<b>Video player</b><br />\n" \
                        "<video id=\"%splayer\" " \
                            "src=\"file://%s\" height=\"%s\" width=\"%s\" controls preload>No video support</video><br />\n" \
                            % (listType, urlHtmlEncode(url), self.videoHeight, self.videoWidth)

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

            output += "document.write(\"<div id='%(type)splaylist' style='overflow: auto; height: %(height)s; max-width: %(width)s;'>\")\n" % {"type": listType, "height": self.playlistHeight, "width": self.playlistWidth}
            output += "document.write(\"<table style='width:100%;'>\")\n"
            i = 0
            for item in playList:
                output += "%splayList[%s] = [\"%s\", \"%s\"]\n" % (listType, i, item[2].replace("\"", "\\\"").replace("#", "%23").replace("?", "%3F"), item[3])
                iconRun = self.htmlLinkSystemRun % {"uri": urlHtmlEncode(item[2])}
                iconRun = iconRun.replace('"', "'")
                iconDir = self.htmlLinkOpenLocation % {"uri": urlHtmlEncode(os.path.dirname(item[2]))}
                iconDir = iconDir.replace('"', "'")
                if item[5] != "":
                    iconGoogleLyrics = self.htmlRenderLink('googlemultisearch', "lyrics " + item[5])
                    iconGoogleLyrics = iconGoogleLyrics.replace('"', "'")

                else:
                    iconGoogleLyrics = ""

                row = "<tr>"
                row += "<td width='30px'><button onclick='%(type)splayTrack(%(i)s)' type='%(type)sbtnTrack%(i)s'>" \
                            "%(trackNumber)02d</button></td>" % {"type": listType, "i": i, "trackNumber": i + 1 }
                row += "<td id='%(type)strack%(i)s' style='background-color:%(color)s;padding:0 0 0 5;' onclick='%(type)splayTrack(%(i)s)'>" \
                            "%(title)s</td>" % {"type": listType, "color": "LightBlue", "i": i, "title": item[3]}
                row += "<td width='15px' style='background-color:%(color)s;' >%(iconRun)s%(iconDir)s%(iconGoogleLyrics)s</td>" \
                            % {"color": "LightGray", "iconRun": iconRun, "iconDir": iconDir, "iconGoogleLyrics": iconGoogleLyrics}
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
                "            if (%(type)strack.offsetTop >  scrollTop + %(scrollTop)s || %(type)strack.offsetTop < scrollTop + %(scrollBottom)s) {\n" \
                "                document.getElementById('%(type)splaylist').scrollTop = oldTrackOffsetTop;\n" \
                "            }\n" \
                "        } else {\n" \
                "            %(type)strack.style.fontWeight = 'normal';\n" \
                "        }\n" \
                "        oldTrackOffsetTop = %(type)strack.offsetTop\n" \
                "    }\n" \
                "    %(type)splayer.volume = %(type)splayerVolume;\n" \
                "    //window.alert(%(type)splayer.volume);\n" \
                "} );\n" % {"type": listType, "scrollTop": self.playlistHeight - self.playlistScrollHeight, "scrollBottom": self.playlistScrollHeight}

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

            output += "<br /></div>\n"

        return output


    def formatAsText(self, data = [], structure = [], queryTime = 0, pipeMode = False):
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
                    resource = Nepomuk2.Resource(uri)

                if pipeMode:
                    line = toUnicode(resource.property(NOC('nie:url', True)).toString().toUtf8())
                    if (line == "") or (line == None):
                        line = uri

                    #else:
                        #line = "\"" + line.replace('"', '\\\\"') + "\""

                else:
                    altLabel = resource.property(NOC('nao:altLabel', True)).toString()
                    fullname = resource.property(NOC('nco:fullname', True)).toString()
                    identifier = resource.property(NOC('nao:identifier', True)).toString()
                    itemType = toUnicode(str(resource.type()).split('#')[1])
                    prefLabel = resource.property(NOC('nao:prefLabel', True)).toString()
                    title = resource.property(NOC('nie:title', True)).toString()
                    url = resource.property(NOC('nie:url', True)).toString()

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
        if (vartype(par1) == "QUrl"):
            par1 = par1.toString()

        if (vartype(par2) == "QUrl"):
            par2 = par2.toString()

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

        elif id == 'googlemultisearch':
            title = "title=\"Search for &quot;%s&quot; using Google\"" % par1
            href = "href=\"googlesearch:/%s\"" % par1.replace(' ', '+')
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
        #if True:
        try:
            if (valueType == 'boolean'):
                result = value

            elif (valueType == 'datep'):
                result = formatDate(value[:19], True)

            elif (valueType == 'date'):
                result = formatDate(value[:19])

            elif (valueType == 'datetimep'):
                result = formatDateTime(value[:19], True)

            elif (valueType == 'datetime'):
                result = formatDateTime(value[:19])

            elif (valueType == 'indexinglevel'):
                try:
                    result = int(value)
                    if not (result in (0, 1, 2)):
                        result = 0

                    result = KEXT_INDEXING_LEVEL[result]

                except:
                    result = "%s" % value

            elif (valueType == 'unixfilemode'):
                result = "%o" % int(value)
                result = "%s %s" % (result[:3], result[3:])

            elif (valueType in ('int', 'integer', 'number', 'nonnegativeinteger')):
                result = "%d" % int(float(value))

            elif (valueType == 'float'):
                result = "%.4f" % float(value)

            elif (valueType == 'duration'):
                result = "%s" % datetime.timedelta(0, int(value), 0)

            elif (valueType == 'size'):
                result = "%0.2f" % (int(value)/1024.00/1024.00)
                if (result == "0.00"):
                    result = "%0.2f" % (int(value)/1024.00)
                    if (result == "0.00"):
                        result = "%0.2f Bytes" % (int(value))

                    else:
                        result += " KiB"

                else:
                    result += " MiB"


            elif (valueType == 'string'):
                result = value

            elif (valueType == 'aperturevalue'):
                result = "F%.1f" % float(value)

            elif (valueType == 'exposurebiasvalue'):
                try:
                    value = fractions.Fraction(value).limit_denominator(max_denominator=30)
                    if (value.denominator == 1):
                        result = "%.0f EV" % (value.numerator)

                    else:
                        result = "%s/%s EV" % (value.numerator, value.denominator)

                    if (result[0] != "-"):
                        result = "+" + result

                except:
                    result = "%s EV" % value

            elif (valueType == 'exposuretime'):
                try:
                    fracValue = fractions.Fraction(value).limit_denominator(max_denominator=16000)
                    result = "%s/%s s" % (fracValue.numerator, fracValue.denominator)
                    if (fracValue.numerator > 1):
                        print fracValue.numerator
                        fracValue = fractions.Fraction(value).limit_denominator(max_denominator=(fracValue.denominator/fracValue.numerator)+1)
                        result += " (%s/%s s)" % (fracValue.numerator, fracValue.denominator)

                except:
                    result = "%s s" % value

            elif (valueType == 'flash'):
                try:
                    # bit value
                    # 0   -- flash fired: did not fire, fired
                    # 1,2 -- flash return: No strobe return detection function, reserved, Strobe return light not detected, Strobe return light detected
                    # 3,4 -- flash mode: Unknown, Compulsore flash firing, Compulsory flash suppression, Auto mode
                    # 5   -- flash function: Present, No flash function
                    # 6   -- red-eye: no or unknown, yes
                    # 7   -- unused
                    flashValues = []
                    if (__builtin__.bin(int(value)&1) == __builtin__.bin(0)):
                        flashValues += [NEXIF_FLASH[0]]

                    else:
                        flashValues += [NEXIF_FLASH[1]]

                    # Flash return:
                    if (__builtin__.bin(int(value)&6) == __builtin__.bin(2)):
                        flashValues += [_("reserved")]

                    elif (__builtin__.bin(int(value)&6) == __builtin__.bin(4)):
                        flashValues += [_("return light not detected")]

                    elif (__builtin__.bin(int(value)&6) == __builtin__.bin(6)):
                        flashValues += [_("return light detected")]

                    #else:
                    #    pass

                    # Flash mode:
                    if (__builtin__.bin(int(value)&24) == __builtin__.bin(8)):
                        flashValues += [_("compulsory firing")]

                    elif (__builtin__.bin(int(value)&24) == __builtin__.bin(16)):
                        flashValues += [_("compulsory suppression")]

                    elif (__builtin__.bin(int(value)&24) == __builtin__.bin(24)):
                        flashValues += [_("auto")]

                    #else:
                    #    pass

                    #Flash function:
                    if (__builtin__.bin(int(value)&32) == __builtin__.bin(32)):
                        flashValues += [_("no flash function")]

                    #Flash function:
                    if (__builtin__.bin(int(value)&64) == __builtin__.bin(64)):
                        flashValues += [_("red-eye reduction")]

                    result = ", ".join(flashValues)

                except:
                    result = "%s" % value

            elif (valueType == 'focallength'):
                try:
                    value = fractions.Fraction(value).limit_denominator()
                    result = "%.1f mm" % (float(value.numerator)/float(value.denominator))

                except:
                    result = "%s mm" % value

            elif (valueType == 'isospeedratings'):
                result = "%s ISO" % value

            elif (valueType == 'meteringmode'):
                try:
                    result = int(value)
                    if (result == 255):
                        result = 7

                    elif ((result < 0) and (result > 6)):
                        result = 0

                    result = NEXIF_METERING_MODE[result]

                except:
                    result = "%s" % value

            elif (valueType == 'orientation'):
                result = "%s" % value

            elif (valueType == 'saturation'):
                try:
                    result = int(value)
                    if not (result in (1, 2)):
                        result = 0

                    result = NEXIF_SATURATION[result]

                except:
                    result = "%s" % value

            elif (valueType == 'sharpness'):
                try:
                    result = int(value)
                    if not (result in (1, 2)):
                        result = 0

                    result = NEXIF_SHARPNESS[result]

                except:
                    result = "%s" % value

            elif (valueType == 'whitebalance'):
                try:
                    result = int(value)
                    if not (result in (1, 2)):
                        result = 0

                    result = NEXIF_WHITE_BALANCE[result]

                except:
                    result = "%s" % value

            else:
                result = value

        except:
            result = value

        return result


    def readProperty(self, resource, propertyOntology, propertyType = "str"):
        #if True:
        try:
            if vartype(resource) in ("str", "QString"):
                if INTERNAL_RESOURCE:
                    resource = cResource(resource)

                else:
                    resource = Nepomuk2.Resource(resource)

            result = resource.property(NOC(propertyOntology, True))
            if result != None:
                if (propertyType == "int"):
                    result = int(result.toString())

                elif (propertyType == "year"):
                    try:
                        result = int(result.toString()[:4])

                    except:
                        result = 0

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
                    query = query.replace("%(" + var + ")s", toUnicode(resource.property(NOC(var, True)).toString()))

            queryResultSet = self.model.executeQuery(query, SOPRANO_QUERY_LANGUAGE)
            if queryResultSet.isValid():
                while queryResultSet.next():
                    values += [[toUnicode(queryResultSet["uri"].toString()), \
                                toUnicode(queryResultSet["value"].toString())]]

        else:
            elements = valuesName.split("->")
            if len(elements) > 1:
                # A simple relation.
                uris = toUnicode(resource.property(NOC(elements[0], True)).toStringList())
                for uri in uris:
                    # Handling cases where there is no uri and value is stored directly.
                    if uri[:13] == "nepomuk:/res/":
                        query = 'SELECT DISTINCT ?value\n' \
                                'WHERE {\n' \
                                    '\t<%s> %s ?value .\n' \
                                '}\n' \
                                % (uri, elements[1])
                        queryResultSet = self.model.executeQuery(query, SOPRANO_QUERY_LANGUAGE)
                        if queryResultSet.isValid():
                            value = ""
                            while queryResultSet.next():
                                if value != "":
                                    value += ", "

                                if (vartype(uri) == "QUrl"):
                                    uri = uri.toString()

                                values += [[uri, toUnicode(queryResultSet["value"].toString())]]

                    else:
                        # If value is a "/" then assuming it's a file.
                        if uri[0] == "/":
                            uri = "file://" + uri

                        values += [[toUnicode(resource.uri()), uri]]

            elif len(elements) == 1:
                # A property.
                if elements[0] == "uri":
                    values += [[toUnicode(resource.uri()), toUnicode(resource.uri())]]

                elif elements[0] == "type":
                    values += [[toUnicode(resource.uri()), NOCR(resource.type())]]

                else:
                    propertyValue = toUnicode(resource.property(NOC(elements[0], True)).toString())
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
            addImage = addLink = addLinkOpenFile = addLinkOpenLocation = addOpenFile = addOpenLocation = addOpenKIO = addSearch = limitToOne = False
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

                elif item == "1":
                    limitToOne = True

                else:
                    values = self.readValues(resource, item)

            if limitToOne and (len(values) > 1):
                values = [values[0]]

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

                    # Uris must be decoded for better user display.
                    if displayValue.find("://") > 0: # A bad assumption :?
                        displayValue = urlDecode(displayValue)

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
            resource = Nepomuk2.Resource(uri)

        if USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE and not INTERNAL_RESOURCE_IN_RESULTS_LIST:
            itemType = NOCR(cResource(uri).type())

        else:
            itemType = NOCR(resource.type())

        idx = lindex(self.ontologyFormat, itemType, column = 0)
        if (idx == None):
            idx = 0

        isValid = False
        columns = []
        for i in range(1, self.columnsCount + 1):
            pattern = self.ontologyFormat[idx][i]
            if (vartype(pattern) == "int"):
                columns += [self.getResourceIcons(toUnicode(uri), pattern)]

            elif (pattern == "{type}"):
                columns += ["<b title='%s'>" % itemType + ontologyToHuman(itemType) + "</b>"]

            else:
                columns += [self.formatResource(resource, pattern)]
                isValid = True

        if isValid:
            #TODO: columnsformat, this must be automatic.
            line = self.htmlTableRow % (columns[0], columns[1], columns[2])

        else:
            line = ""

        resource = None

        return line


    def formatAsHtml(self, param1 = None, structure = [], queryTime = 0, stdout = False):
        if (self.searchString[:9] == "nepomuk:/"):
            self.navegable = False
            return self.formatResourceInfo()

        if ((self.searchString.find('--playlist') >= 0) or (self.searchString.find('--playmixed') >= 0)):
            self.navegable = False
            return self.formatAsHtmlPlaylist()

        self.navegable = True
        htmlQueryTime = time.time()

        text = self.htmlHeader % ("Query results", "")
        #if (self.searchString[:3] != "e0 "):
        #    text += "WARNING! this kind of query is slow with Nepomuk2, don't use prefix or use e0 prefix."

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
                    #if True:
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
                    '<td>%s of %s records</td><td>%s</td><tr>' \
                        % (min(self.renderSize, len(self.data) - self.renderedDataRows), self.renderedDataRows, len(self.data), self.htmlLinkRemoveAll)

        else:
            rowNavigation = '<tr><td></td><td>%s records</td><td>%s</td><tr>' % (len(self.data), self.htmlLinkRemoveAll)

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
        nfoArchiveItem = NOC('nfo:ArchiveItem', True)
        nfoVideo = NOC('nfo:Video', True)
        nieUrl = NOC('nie:url', True)
        nieTitle = NOC('nie:title', True)
        nmmMusicPiece = NOC('nmm:MusicPiece', True)

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
                    resource = Nepomuk2.Resource(QUrl(item[0]))

                if ((resource.type() != nfoArchiveItem) and resource.hasProperty(nieUrl)):
                    url = fromPercentEncoding(toUnicode(resource.property(nieUrl).toString().toUtf8()))
                    ext = os.path.splitext(url)[1][1:].lower()
                    if ((ext != '') and fileExists(url)):
                        if ext in self.supportedImageFormats:
                            if (lindex(images, url) == None):
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

            #TODO: it's this loop used?
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

        #query = "SELECT DISTINCT ?ont ?val\n" \
        #        "WHERE {\n" \
        #            "\t<" + uri + "> ?ont ?val ; nao:userVisible 1 .\n"\
        #        "}\n"
        query = "SELECT DISTINCT ?ont ?val\n" \
                "WHERE {\n" \
                    "\t<" + uri + "> ?ont ?val .\n"\
                "}\n"
        if stdout:
            print toUtf8(query)

        script = ""
        if self.enableImageViewer:
            script += SCRIPT_IMAGE_VIEWER
            imageViewer = "<img title=\"%%(title)s\" src=\"%%(url)s\" style=\"width: %s;\" "\
                            "onLoad=\"new viewer({image: this, frame: ['%s','400px']});\"/>" % (self.viewerColumnsWidth, self.viewerColumnsWidth)

        if self.videojsEnabled:
            script += "<link href=\"http://vjs.zencdn.net/c/video-js.css\" rel=\"stylesheet\" type=\"text/css\">\n" \
                        "<script src=\"http://vjs.zencdn.net/c/video.js\"></script>\n"

        output = self.htmlHeader % (_('Resource viewer'), script)
        output += "<div class=\"top\" style=\"static: top;\">\n"
        output += '<b title=\"%(uri)s\"><h2><a title)=\"%(uri)s\" href=\"%(uri)s\">%(title)s</a></b>&nbsp;%(remove)s<reindex />&nbsp;&nbsp;%(navigator)s<cached /></h2>\n' \
                        % {"title": _('Resource viewer'), 'uri': uri, "remove": self.htmlLinkRemove % {"uri": uri, "hotkey": " (Ctrl+Del)"}, "navigator": self.htmlRenderLink("navigator")}
        output += "</div>\n"
        output += "<div class=\"data\" style=\"float: left; width: %s;\">\n<hr>" % self.viewerColumnsWidth
        output += self.htmlViewerTableHeader

        if INTERNAL_RESOURCE:
            mainResource = cResource(uri, False, False) # prefechData = useCache = False
            defaultType = NOCR(mainResource.type())

        else:
            mainResource = Nepomuk2.Resource(uri)
            if USE_INTERNAL_RESOURCE_FOR_MAIN_TYPE:
                defaultType = NOCR(cResource(uri).type())

            else:
                defaultType = NOCR(mainResource.type())

        if defaultType != "":
            data = self.model.executeQuery(query, SOPRANO_QUERY_LANGUAGE)

        noc_nfoArchiveItem = NOC("nfo:ArchiveItem", True)
        noc_nieUrl = NOC("nie:url", True)
        noc_nieTitle = NOC("nie:title", True)

        isAnEmptyResource = True
        if ((defaultType != "") and data.isValid()):
            processedData = []
            images = []
            audios = []
            videos = []
            while data.next():
                isAnEmptyResource = False
                currOnt = NOCR(data["ont"].toString())
                if ((currOnt in self.hiddenOntologies) or (currOnt.find(":") < 0)):
                    continue

                ontInfo = ontologyInfo(data["ont"].toString(), self.model)
                value = self.fmtValue(toUnicode(data["val"].toString()), ontInfo[2])
                if value[:9] == 'nepomuk:/':
                    if INTERNAL_RESOURCE:
                        resource = cResource(value)

                    else:
                        resource = Nepomuk2.Resource(value)

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

                    elif resource.type() == NOC('nmm:TVSeason', True):
                        ontLabel = currOnt + '->nmm:seasonNumber'
                        seasonNumber = "%d" % self.readProperty(resource, 'nmm:seasonNumber', 'int')
                        value = '<!--' + toUnicode(seasonNumber) + '-->' \
                                    + self.htmlRenderLink('uri', resource.uri(), seasonNumber)

                    else:
                    #elif resource.hasType(NOC('rdfs:Resource', True)):
                        ontLabel = ''
                        # Better don't add remote resources.
                        if not (resource.hasType(NOC('nfo:RemoteDataObject', True))):
                            if resource.hasProperty(noc_nieUrl):
                                url = toUnicode(resource.property(noc_nieUrl).toString())
                                ext = os.path.splitext(url)[1][1:].lower()
                                if ext != '' and ext in self.supportedImageFormats:
                                    if (lindex(images, url) == None):
                                        if resource.hasProperty(noc_nieTitle):
                                            images += [[url, toUnicode(resource.property(noc_nieTitle).toString())]]

                                        else:
                                            images += [[url, os.path.basename(url)]]

                    #else:
                    #    value = toUnicode(resource.type())

                    if value == '':
                        shorcut = lvalue(knownShortcuts, ontLabel, 0, 1)
                        if shorcut == None:
                            shorcut = ontLabel

                        # Trying to avoid the two titles bug.
                        #genericLabel = toUnicode(resource.genericLabel())
                        genericLabel = resource.property(NOC("nie:title", True))
                        if genericLabel.isStringList():
                            genericLabel = toUnicode(genericLabel.toStringList()[0])

                        else:
                            genericLabel = toUnicode(genericLabel.toString())

                        if (genericLabel == ""):
                            genericLabel = toUnicode(resource.genericLabel())

                        resourceUrl = self.readProperty(resource, "nie:url", "str")
                        if resourceUrl == "":
                            resourceUrl = genericLabel

                        value = '<!--' + genericLabel + '-->' + self.htmlRenderLink('uri', resource.uri(), genericLabel)
                        if ((resourceUrl[:7] == "http://") or (resourceUrl[:8] == "https://")) \
                                and (resourceUrl.find(" ") < 0):
                                # Seems a url so a link to the url could be great.
                                value += " <a title=\"%s\" href=\"%s\"><img src=\"file://%s\"></a>" \
                                            % (resourceUrl, resourceUrl, self.iconEmblemLink)

                        if ontLabel != '':
                            value += ' ' + self.htmlRenderLink('ontology', shorcut, genericLabel)

                elif currOnt == 'rdf:type':
                    value = NOCR(value)
                    if value == defaultType:
                        value = '<em>' + value + '</em>'

                elif currOnt == 'nie:url':
                    url = fromPercentEncoding(value)
                    if (mainResource.type() == noc_nfoArchiveItem):
                        value = "<a title=\"%(url)s\" href=\"%(url)s\">%(url)s</a>" % {"url": url}
                        value += ' ' + self.htmlLinkSystemRun % {"uri": url}
                        value += ' ' + self.htmlLinkOpenLocation % {"uri": os.path.dirname(url)}

                    else:
                        ext = os.path.splitext(url)[1][1:].lower()
                        if ext in self.supportedImageFormats:
                            if (lindex(images, url) == None):
                                images += [[url, os.path.basename(url)]]

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

                elif currOnt == "nao:numericRating":
                    try:
                        value = self.getRatingHtml(int(value), 16)

                    except:
                        pass

                elif currOnt == "nexif:orientation":
                    try:
                        value = self.getOrientationHtml(int(value), 48)

                    except:
                        pass

                else:
                    #if True:
                    try:
                        # Must check for full paths to avoid file detection in execution path.
                        if (((value[0] == "/") or (value[:7] == "file://")) and fileExists(value)):
                            ext = os.path.splitext(value)[1][1:].lower()
                            if ext != '' and ext in self.supportedImageFormats:
                                if (lindex(images, value) == None):
                                    images += [[value, os.path.basename(value)]]

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
                    processedData += [[currOnt, ontologyToHuman(ontInfo[0]), value]]

            if (not isAnEmptyResource and not mainResource.hasProperty(NOC("nao:numericRating", True))):
                try:
                    processedData += [["nao:numericRating", ontologyToHuman("nao:numericRating"), self.getRatingHtml(0, 16)]]

                except:
                    pass

        text = ''
        if len(processedData) > 0:
            processedData = sorted(processedData, key=lambda row: row[1] + row[2])
            oldOnt = ''
            # Default to add values.
            text += '<tr><td valign=\"top\" width=\"120px\">' \
                    '<a title=\"%(title)s\" href=\"propadd:/%(uri)s\"><b>%(label)s</b></a></td><td></td></tr>\n' \
                        % {"uri": uri, "title": _("Click to add a new value (Ctrl++)"), "label": _("Add new value")}
            for row in processedData:
                if (oldOnt != row[1]):
                    if text != '':
                        text += '</td></tr>\n'

                    text += '<tr><td valign=\"top\" width=\"120px\">' \
                            '<a title=\"%(ont)s (Click, Shift+Click, Ctrl+Click to add, edit or remove)\" ' \
                            'href=\"propedit:/%(uri)s&%(ont)s\"><b>%(label)s</b></a>:</td><td>%(value)s' \
                                % {"uri": uri, "ont": row[0], "label": row[1], "value": row[2]}
                    oldOnt = row[1]

                else:
                    text += ', ' + row[2]

        if text == '':
            output += '<p>%s.</p>\n' % (_("No data found for the uri \"%s\", resource was probably deleted.") % uri)

        else:
            # Special headers for some resources.
            if (defaultType in (ONTOLOGY_TYPE_CONTACT, ONTOLOGY_TYPE_MUSIC_ALBUM, ONTOLOGY_TYPE_TAG, ONTOLOGY_TYPE_MOVIE, ONTOLOGY_TYPE_TV_SERIES)):
                # Adding the header.

                symbolPattern = None
                if (defaultType == ONTOLOGY_TYPE_CONTACT):
                    ontologySymbol = NOC(ONTOLOGY_SYMBOL_CONTACT, True)
                    symbol = toUnicode(self.iconNoPhoto)
                    newResource = "&nbsp;<a title=\"%s\" href=\"addresource:/nco:Contact\"><img valign=\"middle\" src=\"file://%s\"></a>" % (_("Create an empty %s") % ONTOLOGY_TYPE_CONTACT, self.iconListAdd)

                elif (defaultType == ONTOLOGY_TYPE_MUSIC_ALBUM):
                    ontologySymbol = NOC(ONTOLOGY_MUSIC_ALBUM_COVER, True)
                    symbol = toUnicode(self.iconNoCover)
                    newResource = ""

                elif (defaultType == ONTOLOGY_TYPE_MOVIE):
                    ontologySymbol = NOC(ONTOLOGY_MOVIE_COVER, True)
                    symbolPattern = "(poster)"
                    symbol = toUnicode(self.iconNoCover)
                    newResource = ""

                elif (defaultType == ONTOLOGY_TYPE_TV_SERIES):
                    ontologySymbol = NOC(ONTOLOGY_TV_SERIES_COVER, True)
                    symbolPattern = "(poster)"
                    symbol = toUnicode(self.iconNoCover)
                    newResource = ""

                else:
                    ontologySymbol = NOC(ONTOLOGY_SYMBOL, True)
                    symbol = toUnicode(self.iconNoSymbol)
                    newResource = "&nbsp;<a title=\"%s\" href=\"addresource:/nco:Contact&%s\"><img valign=\"middle\" src=\"file://%s\"></a>" % (_("Create a %s based on this tag") % ONTOLOGY_TYPE_CONTACT, uri, self.iconListAdd)

                if mainResource.hasProperty(ontologySymbol):
                    symbols = mainResource.property(ontologySymbol)
                    if (vartype(symbols) == "list"):
                        symbol = urlDecode(self.readProperty(symbols[0].toStringList()[0], "nie:url", "str"))

                    else:
                        for item in symbols.toStringList():
                            symbol = urlDecode(self.readProperty(item, "nie:url", "str"))
                            if ((symbolPattern == None) or (symbol.find(symbolPattern) >= 0)):
                                break

                #if True:
                try:
                    if ((symbol[0] == "/") or (symbol[:7] == "file://")):
                        if fileExists(symbol):
                            if (symbol[:7] != "file://"):
                                symbol = "file://" + symbol

                        else:
                            symbol = "file://" + self.iconUnknown

                    ext = os.path.splitext(symbol)[1][1:].lower()
                    if ext in self.supportedImageFormats:
                        if ((defaultType == ONTOLOGY_TYPE_MUSIC_ALBUM) and (symbol == "file://" + toUnicode(self.iconNoCover))):
                            addCoverLink = "<br /><a title:=\"Automatic cover detection\" href=\"autocover:/%s\">Try to detect cover</a>" % toUnicode(mainResource.uri())

                        else:
                            addCoverLink = ""

                        symbol = urlHtmlEncode(symbol)
                        output += '<tr><td><img %(fmt)s title=\"%(title)s\" src=\"%(url)s\">%(addCoverLink)s</td>' \
                                    % {"fmt": "style=\"float:left; vertical-align:text-top; width: 100px\" border=\"2px\" hspace=\"10px\" vspace=\"0\"", \
                                        'title': os.path.basename(symbol), 'url': symbol, "addCoverLink": addCoverLink}

                        output += "<td><h3>%(resourceType)s%(newResource)s</h3>" % {"resourceType": ontologyInfo(defaultType)[1], "newResource": newResource}

                        if (defaultType == ONTOLOGY_TYPE_CONTACT):
                            fullname = toUnicode(mainResource.property(NOC("nco:fullname", True)).toString())
                            resourceIsA = self.resourceIsA(mainResource)
                            output += '<h2>%(title)s</h2><h4>%(resourceIsA)s%(rating)s</h4></td></tr>' \
                                        % {"title": fullname, "rating": self.getRatingHtml(mainResource, 22), "resourceIsA": resourceIsA}

                        elif (defaultType == ONTOLOGY_TYPE_MUSIC_ALBUM):
                            title = toUnicode(mainResource.property(noc_nieTitle).toString())
                            output += '<h2>%(title)s</h2><h4>%(rating)s</h4></td></tr>' \
                                        % {"title": title, "rating": self.getRatingHtml(mainResource, 22)}

                        elif (defaultType == ONTOLOGY_TYPE_MOVIE):
                            title = toUnicode(mainResource.property(noc_nieTitle).toString())
                            output += '<h2>%(title)s</h2><h4>%(rating)s</h4></td></tr>' \
                                        % {"title": title, "rating": self.getRatingHtml(mainResource, 22)}

                        elif (defaultType == ONTOLOGY_TYPE_TV_SERIES):
                            title = toUnicode(mainResource.property(noc_nieTitle).toString())

                            # Display actors.
                            contactsList = []
                            actors = ""
                            query = \
                                    "SELECT DISTINCT ?uri ?fullname\n" \
                                    "WHERE {\n" \
                                        "  ?tvshow nmm:series <%s> . ?tvshow nmm:actor ?uri . ?uri nco:fullname ?fullname .\n" \
                                    "}" \
                                    "ORDER BY ?fullname" % (mainResource.uri().toString())

                            data = self.model.executeQuery(query, Soprano.Query.QueryLanguageSparqlNoInference)
                            if data.isValid():
                                while data.next():
                                    contactsList += [self.htmlRenderLink('uri', toUnicode(data["uri"].toString()), toUnicode(data["fullname"].toString()))]

                            if (contactsList != []):
                                actors = "<b>All actors in the series</b>:<br />" + ", ".join(contactsList)

                            output += '<h2>%(title)s</h2><h4>%(rating)s</h4>%(actors)s</td></tr>' \
                                        % {"title": title, "rating": self.getRatingHtml(mainResource, 22), "actors": actors}

                        else:
                            title = toUnicode(mainResource.property(NOC("nao:prefLabel", True)).toString())
                            output += '<h2>%(title)s</h2><h4>%(rating)s</h4></td></tr>' \
                                        % {"title": title, "rating": self.getRatingHtml(mainResource, 22)}

                    else:
                        symbol = self.iconUnknown

                except:
                    symbol = self.iconUnknown

            output += text

        # Reverse resources.
        #query = "select ?uri ?ont\n" \
        #        "   where {\n" \
        #        "       ?uri ?ont <%s> ; nao:userVisible 1 .\n" \
        #        "}\n" \
        #        "order by ?ont\n" % uri
        query = "select ?uri ?ont\n" \
                "   where {\n" \
                "       ?uri ?ont <%s>.\n" \
                "}\n" \
                "order by ?ont\n" % uri
        data = self.model.executeQuery(query, SOPRANO_QUERY_LANGUAGE)
        reverseResourcesItems = []
        reverseResourcesList = []
        if data.isValid():
            while data.next():
                resUri = toUnicode(data["uri"].toString())
                ontology = toUnicode(data["ont"].toString())
                if ontology in self.hiddenOntologiesInverse:
                    continue

                if INTERNAL_RESOURCE:
                    res = cResource(resUri)

                else:
                    res = Nepomuk2.Resource(resUri)

                #val = fromPercentEncoding(toUnicode(res.genericLabel()))
                url = None
                if res.type() == NOC('nmm:TVSeason', True):
                    val = "%d" % self.readProperty(res, 'nmm:seasonNumber', 'int')

                else:
                    val = toUnicode(res.genericLabel())
                    if res.hasProperty(noc_nieUrl):
                        url = toUnicode(res.property(noc_nieUrl).toString())

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
                            if (lindex(images, url) == None):
                                images += [[url, os.path.basename(url)]]

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
            output += self.buildPlaylist(audios, 'audio')

        # Resource videos.
        if len(videos) > 0:
            output += self.buildPlaylist(videos, 'video')

        # Resource images.
        if len(images) > 0:
            if len(audios) + len(videos) > 0:
                output += "<br />"

            images = sorted(images, key=lambda item: item[1])
            for item in sorted(images):
                url = item[0]
                if ((url.find("://") < 0) and not (url[:7] == 'file://')):
                    url = 'file://' + url

                if self.enableImageViewer:
                    output += imageViewer % {"title": item[1], 'url': url}

                else:
                    output += '<img title=\"%(title)s\" style=\"height:auto; width: %(width)s; scalefit=1\" src=\"%(url)s\"><br />\n' \
                                % {"title": item[1], 'url': url, "width": self.viewerColumnsWidth}

                output += "<b>File name</b>:<em><a title=\"%(title)s\" href=\"%(url)s\">%(title)s</a></em><br />" % {"url": url, "title": item[1]}

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
