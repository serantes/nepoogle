#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from nepoogle import *

class Test_nsSparqlBuilder(unittest.TestCase):

    albumQueries = [\
                        [unicode('album:heart', 'utf-8'), 102, 6], \
                        [unicode('album:"heart station"', 'utf-8'), 16, 6], \
                        [unicode('album:+"HEART STATION"', 'utf-8'), 16, 6], \
                        [unicode('album:+"Singin\' In the Rain OST"', 'utf-8'), 30, 6] \
                    ]

    andQueries = [\
                    [unicode('actor:"Zhang Ziyi" and actor:"Bingbing Fan"', 'utf-8'), 1, 6], \
                    [unicode('actor:+"Zhang Ziyi" and actor:+"Bingbing Fan"', 'utf-8'), 1, 6], \
                    [unicode('actor:"Zhang Ziyi" and actor:-"Bingbing Fan"', 'utf-8'), 2, 6], \
                    [unicode('-dorama +"takeuchi yuuko" "hiroshi"', 'utf-8'), 3, 6], \
                    [unicode('hasTag:+dorama rating:>=5'), 4, 6],  \
                    [unicode('mimetype:video/x-msvideo url:".avi$"'), 1, 6],  \
                    [unicode('playcount:0 genre:drama actor:+"Yeong-ae Lee" director:Park'), 1, 6], \
                    [unicode('tvshow:Coupling season:2 episode:4'), 1, 6] \
                ]

    basicQueries = [\
                        [unicode('4minute', 'utf-8'), 285, 6], \
                        [unicode('película', 'utf-8'), 132, 6], \
                        [unicode('+película', 'utf-8'), 118, 6], \
                        [unicode('宇多田', 'utf-8'), 203, 6] \
                    ]

    commandQueries = [\
                    [unicode('--tags', 'utf-8'), 145, 3], \
                    [unicode('--actors:bing', 'utf-8'), 1, 2] \
                ]

    orQueries = [\
                    [unicode('película or hasTag:"takeuchi yuuko"', 'utf-8'), 138, 6] \
                ]

    def setUp(self):
        pass

    def test_albumQueries(self):
        #return True
        for itemQuery in self.albumQueries:
            o = nsSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(itemQuery[0])
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), itemQuery[1])
            self.assertEqual(len(structure), itemQuery[2])
            o = None

    def test_andQueries(self):
        #return True
        for itemQuery in self.andQueries:
            o = nsSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(itemQuery[0])
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), itemQuery[1])
            self.assertEqual(len(structure), itemQuery[2])
            o = None

    def test_basicQueries(self):
        #return True
        for itemQuery in self.basicQueries:
            o = nsSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(itemQuery[0])
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), itemQuery[1])
            self.assertEqual(len(structure), itemQuery[2])
            o = None

    def test_commandQueries(self):
        #return True
        for itemQuery in self.commandQueries:
            o = nsSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(itemQuery[0])
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), itemQuery[1])
            self.assertEqual(len(structure), itemQuery[2])
            o = None

    def test_orQueries(self):
        #return True
        for itemQuery in self.orQueries:
            o = nsSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(itemQuery[0])
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), itemQuery[1])
            self.assertEqual(len(structure), itemQuery[2])
            o = None

if __name__ == '__main__':
    unittest.main()

