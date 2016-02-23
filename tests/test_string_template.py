#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import unittest


from .context import engines


HANDLE = 'string.Template'


class TestStringTemplate(unittest.TestCase):

    def test_valid_engine(self):
        self.assertIn(HANDLE, engines.engines)
        engine = engines.engines[HANDLE]
        assert issubclass(engine, engines.Engine)

    def test_escape(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Several escaped dollar signs:\n'
                '$$ $$ $$$$$$\n',
            )

        result = template.apply({
                'random':  'value',
                '$':       'provocation',
            })

        self.assertMultiLineEqual(result,
                'Several escaped dollar signs:\n'
                '$ $ $$$\n'
            )
    
    def test_plain_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '$essen mit\n'
                '$beilage.\n',
            )

        result = template.apply({
                'random':  'value',
                'essen':   'Szegediner Gulasch',
                'beilage': 'Kartoffeln',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                'Szegediner Gulasch mit\n'
                'Kartoffeln.\n'
            )
    
    def test_curly_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '${essen} mit\n'
                '${beilage}.\n',
            )

        result = template.apply({
                'random':  'value',
                'essen':   'Szegediner Gulasch',
                'beilage': 'Kartoffeln',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                'Szegediner Gulasch mit\n'
                'Kartoffeln.\n'
            )

    def test_strict_template_missing_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '$essen mit\n'
                '${beilage}.\n',
            )

        self.assertRaises(Exception, template.apply, ({
                'random':  'value',
            }))

    def test_tolerant_template_missing_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '$essen mit\n'
                '${beilage}.\n',
                tolerant=True,
            )

        result = template.apply({
                'random':  'value',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                '$essen mit\n'
                '${beilage}.\n'
            )


if __name__ == '__main__':
    unittest.main()
