#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from nepoogle import *

class Test_nsSparqlBuilder(unittest.TestCase):

    simpleQueries = [\
                        [unicode('4minute', 'utf-8'), 41, 6], \
                        [unicode('宇多田', 'utf-8'), 48, 6] \
                    ]

    def setUp(self):
        pass

    def test_basicQuery(self):
        for simpleQuery in self.simpleQueries:
            o = nsSparqlBuilder()
            o.columns = '?x0 AS ?id ' + o.columns
            query = o.buildQuery(simpleQuery[0])
            data, structure, time = o.executeQuery(query)
            self.assertEqual(len(data), simpleQuery[1])
            self.assertEqual(len(structure), simpleQuery[2])
            o = None
       
if __name__ == '__main__':
    unittest.main()

