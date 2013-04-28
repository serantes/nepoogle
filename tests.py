#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   nepoogle - unit test script                                           *
#*                                                                         *
#*   Copyright (C) 2011 Ignacio Serantes <kde@aynoa.net>                   *
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

import unittest
from clsparql import *
from clsparql2 import *
from lglobals import *

class Test_cSparqlBuilder(unittest.TestCase):

    albumQueries = [\
                    [unicode('album:heart', 'utf-8'), 78, 1], \
                    [unicode('album:"heart station"', 'utf-8'), 13, 1], \
                    [unicode('album:+"HEART STATION"', 'utf-8'), 13, 1], \
                    [unicode('album:+"heart station"', 'utf-8'), 0, 0], \
                    [unicode('album:+"Singin\' In the Rain OST"', 'utf-8'), 30, 1] \
                ]

    andQueries = [\
                    [unicode('actor:"Zhang Ziyi" and actor:"Bingbing Fan"', 'utf-8'), 1, 1], \
                    [unicode('actor:+"Zhang Ziyi" and actor:+"Bingbing Fan"', 'utf-8'), 1, 1], \
                    [unicode('actor:+"Zhang Ziyi" and actor:-"Bingbing Fan"', 'utf-8'), 1, 1], \
                    [unicode('-dorama +"takeuchi yuuko" "hiroshi"', 'utf-8'), 2, 1], \
                    [unicode('ht:-dorama ht:+"takeuchi yuuko" ht:"hiroshi"', 'utf-8'), 2, 1], \
                    [unicode('hasTag:+dorama rating:>=5'), 4, 1],  \
                    [unicode('mimetype:video/x-msvideo url:".avi$"'), 1601, 1],  \
                    [unicode('genre:drama actor:+"Yeong-ae Lee" director:Park'), 1, 1], \
                    [unicode('tvshow:Coupling season:2 episode:4'), 1, 1], \
                    [unicode('mimetype:video performer:beg releasedate:-'), 13, 1], \
                    [unicode('flash:yes meteringmode:"center weighted average" whitebalance:auto saturation:- sharpness:-'), 6, 1], \
                    [unicode('hastag:live released:-'), 513, 1] \
                ]

    basicQueries = [\
                    [unicode('4minute', 'utf-8'), 335, 1], \
                    [unicode('película', 'utf-8'), 112, 1], \
                    [unicode('+película', 'utf-8'), 112, 1], \
                    [unicode('宇多田', 'utf-8'), 136, 1], \
                    [unicode('actors:.*bing.*', 'utf-8'), 2, 1] \
                ]

    commandQueries = [\
                    [unicode('--tags', 'utf-8'), 146, 1], \
                    [unicode('--actors:.*bing.*', 'utf-8'), 2, 1] \
                ]

    orQueries = [\
                    [unicode('película or hasTag:"takeuchi yuuko"', 'utf-8'), 128, 1] \
                ]

    parenthesesQueries = [\
                    [unicode('(performer:miryo or performer:narsha) and performer:-beg and hastag:videoclip', 'utf-8'), 9, 1], \
                    [unicode('performer:-beg and (performer:miryo or performer:narsha) and (url:.mp3$ or mimetype:mpeg)', 'utf-8'), 8, 1], \
                    [unicode('movies: and (actor:bing or actor:ziyi)', 'utf-8'), 3, 1] \
                ]

    def setUp(self):
        pass

    def runQueryAndCheck(self, textQuery = '', auxData = []):
        if (textQuery != '') and auxData != []:
            o = cSparqlBuilder2()
            query = o.buildQuery(textQuery)
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), auxData[0], 'Query = %s (%s != %s)' % (textQuery, len(data), auxData[0]))
            #self.assertEqual(len(structure), auxData[1], 'Query = %s (%s != %s)' % (textQuery, len(structure), auxData[0]))
            o = None

    def test_albumQueries(self):
        #return True
        for itemQuery in self.albumQueries:
            self.runQueryAndCheck(itemQuery[0], [itemQuery[1], itemQuery[2]])

    def test_andQueries(self):
        #return True
        for itemQuery in self.andQueries:
            self.runQueryAndCheck(itemQuery[0], [itemQuery[1], itemQuery[2]])

    def test_basicQueries(self):
        #return True
        for itemQuery in self.basicQueries:
            self.runQueryAndCheck(itemQuery[0], [itemQuery[1], itemQuery[2]])

    def test_commandQueries(self):
        #return True
        for itemQuery in self.commandQueries:
            self.runQueryAndCheck(itemQuery[0], [itemQuery[1], itemQuery[2]])

    def test_orQueries(self):
        #return True
        for itemQuery in self.orQueries:
            self.runQueryAndCheck(itemQuery[0], [itemQuery[1], itemQuery[2]])

    def test_parenthesesQueries(self):
        #return True
        for itemQuery in self.parenthesesQueries:
            self.runQueryAndCheck(itemQuery[0], [itemQuery[1], itemQuery[2]])

if __name__ == '__main__':
    # Whithout this nepomuk don't works.
    app = QCoreApplication(sys.argv)

    unittest.main()
