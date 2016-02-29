#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import unittest


from .context import engines


HANDLE = 'string.Formatter'


class TestStringFormatter(unittest.TestCase):

    def test_valid_engine(self):
        self.assertIn(HANDLE, engines.engines)
        engine = engines.engines[HANDLE]
        assert issubclass(engine, engines.Engine)

    def test_escape(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Several escaped braces:\n'
                '}} {{ {{foo}} {{{{bar}}}}\n',
            )

        result = template.apply({
                'random':  'value',
                'foo':     'provocation',
            })

        self.assertMultiLineEqual(result,
                'Several escaped braces:\n'
                '} { {foo} {{bar}}\n'
            )
    
    def test_string_selector(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '{essen} mit\n'
                '{beilage}.\n',
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

    def test_strict_template_int_selector(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '{1} mit\n'
                '{2}.\n',
                tolerant=False,
            )

        self.assertRaises(KeyError, template.apply, {
                0:   '<zero>',
                1:   'Szegediner Gulasch',
                '2': 'Kartoffeln',
            })

    def test_tolerant_template_int_selector(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '{1} mit\n'
                '{2} und {drinks.first[0]!r:20s}.\n',
                tolerant=True,
            )

        result = template.apply({
                0:   '<zero>',
                1:   'Szegediner Gulasch',
                '1': 'Eisbergsalat',
                '2': 'Kartoffeln',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                'Szegediner Gulasch mit\n'
                'Kartoffeln und {drinks.first[0]!r:20s}.\n'
            )

    def test_strict_template_missing_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '{essen} mit\n'
                '{beilage}.\n',
                tolerant=False,
            )

        self.assertRaises(KeyError, template.apply, {
                'random': 'value',
                'essen':  'Szegediner Gulasch',
            })

    def test_tolerant_template_missing_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '{essen} mit\n'
                '{beilage}.\n',
                tolerant=True,
            )

        result = template.apply({
                'random': 'value',
                'essen':  'Szegediner Gulasch',
            })

        self.assertMultiLineEqual(result,
                'Heute gibt es\n'
                'Szegediner Gulasch mit\n'
                '{beilage}.\n'
            )


if __name__ == '__main__':
    unittest.main()
