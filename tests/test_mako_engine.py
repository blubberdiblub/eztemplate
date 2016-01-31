#!/usr/bin/env python

from __future__ import print_function

import unittest


import engines


HANDLE = 'mako'


class TestStringTemplate(unittest.TestCase):

    def setUp(self):
        try:
            import mako
        except ImportError:
            self.skipTest("mako module not available")

    def test_valid_engine(self):
        self.assertIn(HANDLE, engines.engines)
        engine = engines.engines[HANDLE]
        assert issubclass(engine, engines.Engine)

    def test_escape(self):
        engine = engines.engines[HANDLE]

        template = engine(
                '<%text>Heute gibt es\n'
                '${essen} mit\n'
                '${beilage}.\n</%text>',
            )

        result = template.apply({
                'random':  'value',
                'essen':   'Szegediner Gulasch',
                'beilage': 'Kartoffeln',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                '${essen} mit\n'
                '${beilage}.\n',
            )
    
    def test_conditional(self):
        engine = engines.engines[HANDLE]

        template = engine(
                '% if value < 10:\n'
                'less than ten\n'
                '% else:\n'
                'greater or equal\n'
                '% endif\n',
            )

        result = template.apply({
                'value':  4,
            })

        self.assertMultiLineEqual(result,
                'less than ten\n',
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
                '${essen} mit\n'
                '${beilage}.\n',
            )

        self.assertRaises(Exception, template.apply, ({
                'random':  'value',
            }))

    def test_tolerant_template_missing_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '${essen} mit\n'
                '${beilage}.\n',
                tolerant=True,
            )

        result = template.apply({
                'random':  'value',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                '<UNDEFINED> mit\n'
                '<UNDEFINED>.\n'
            )


if __name__ == '__main__':
    unittest.main()
