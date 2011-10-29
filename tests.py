#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from clsparql import *

class Test_cSparqlBuilder(unittest.TestCase):

    albumQueries = [\
                        [unicode('album:heart', 'utf-8'), 89, 6], \
                        [unicode('album:"heart station"', 'utf-8'), 13, 6], \
                        [unicode('album:+"HEART STATION"', 'utf-8'), 13, 6], \
                        [unicode('album:+"heart station"', 'utf-8'), 0, 0], \
                        [unicode('album:+"Singin\' In the Rain OST"', 'utf-8'), 30, 6] \
                    ]

    andQueries = [\
                    [unicode('actor:"Zhang Ziyi" and actor:"Bingbing Fan"', 'utf-8'), 1, 6], \
                    [unicode('actor:+"Zhang Ziyi" and actor:+"Bingbing Fan"', 'utf-8'), 1, 6], \
                    [unicode('actor:+"Zhang Ziyi" and actor:-"Bingbing Fan"', 'utf-8'), 2, 6], \
                    [unicode('-dorama +"takeuchi yuuko" "hiroshi"', 'utf-8'), 2, 6], \
                    [unicode('ht:-dorama ht:+"takeuchi yuuko" ht:"hiroshi"', 'utf-8'), 2, 6], \
                    [unicode('hasTag:+dorama rating:>=5'), 4, 6],  \
                    [unicode('mimetype:video/x-msvideo url:".avi$"'), 1, 6],  \
                    [unicode('playcount:0 genre:drama actor:+"Yeong-ae Lee" director:Park'), 1, 6], \
                    [unicode('tvshow:Coupling season:2 episode:4'), 1, 6] \
                ]

    basicQueries = [\
                        [unicode('4minute', 'utf-8'), 220, 6], \
                        [unicode('película', 'utf-8'), 130, 6], \
                        [unicode('+película', 'utf-8'), 118, 6], \
                        [unicode('宇多田', 'utf-8'), 174, 6] \
                    ]

    commandQueries = [\
                    [unicode('--tags', 'utf-8'), 144, 3], \
                    [unicode('--actors:bing', 'utf-8'), 1, 2] \
                ]

    orQueries = [\
                    [unicode('película or hasTag:"takeuchi yuuko"', 'utf-8'), 136, 6] \
                ]

    def setUp(self):
        pass

    def runQueryAndCheck(self, textQuery = '', auxData = []):
        if (textQuery != '') and auxData != []:
            o = cSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(textQuery)
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), auxData[0], 'Query = %s' % textQuery)
            self.assertEqual(len(structure), auxData[1], 'Query = %s' % textQuery)
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

if __name__ == '__main__':
    unittest.main()
