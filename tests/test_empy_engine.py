#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import unittest


from .context import engines


HANDLE = 'empy'


class TestAvailability(unittest.TestCase):

    def test_module_availabilty_coincides_with_template_availability(self):
        try:
            import em
        except ImportError:
            self.assertNotIn(HANDLE, engines.engines, "engine available but module not importable")
        else:
            self.assertIn(HANDLE, engines.engines, "engine not available but module importable")


@unittest.skipIf(HANDLE not in engines.engines, "engine not available")
class TestTemplating(unittest.TestCase):

    def test_valid_engine(self):
        self.assertIn(HANDLE, engines.engines)
        engine = engines.engines[HANDLE]
        assert issubclass(engine, engines.Engine)

    def test_escape(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Several escaped at signs:\n'
                '@@ @@ @@@@@@\n',
            )

        result = template.apply({
                'random': 'value',
                '@':      'provocation',
            })

        self.assertMultiLineEqual(result,
                'Several escaped at signs:\n'
                '@ @ @@@\n',
            )
    
    def test_conditional(self):
        engine = engines.engines[HANDLE]

        template = engine(
                '@[if value < 10]@\n'
                'less than ten\n'
                '@[else]@\n'
                'greater or equal\n'
                '@[end if]@\n',
            )

        result = template.apply({
                'value': 4,
            })

        self.assertMultiLineEqual(result,
                'less than ten\n',
            )

        result = template.apply({
                'value': 14,
            })

        self.assertMultiLineEqual(result,
                'greater or equal\n',
            )
    
    def test_expression_evaluation(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '@essen mit\n'
                '@(beilage) und\n'
                '@(5 - 3) @("".join(["Nach", "speise", "n"])).\n'
            )

        result = template.apply({
                'random':  'value',
                'essen':   'Szegediner Gulasch',
                'beilage': 'Kartoffeln',
            })

        self.assertMultiLineEqual(result,
            'Heute gibt es\n'
            'Szegediner Gulasch mit\n'
            'Kartoffeln und\n'
            '2 Nachspeisen.\n'
        )

    def test_statement_blocks(self):
        engine = engines.engines[HANDLE]

        template = engine(
                '@{import sys}@\n'
                'Heute gibt es\n'
                '@{sys.stdout.write(essen)} mit\n'
                '@{sys.stdout.write(beilage)} und\n'
                '@{sys.stdout.write("%d" % (5 - 3,))} @{\n'
                'print("".join([\n'
                '               "Nach",\n'
                '               "speise",\n'
                '               "n",\n'
                '              ]) + ".")\n'
                '}@\n'
            )

        result = template.apply({
                'random':  'value',
                'essen':   'Szegediner Gulasch',
                'beilage': 'Kartoffeln',
            })

        self.assertMultiLineEqual(result,
            'Heute gibt es\n'
            'Szegediner Gulasch mit\n'
            'Kartoffeln und\n'
            '2 Nachspeisen.\n'
        )

    def test_strict_template_missing_identifier(self):
        engine = engines.engines[HANDLE]

        template = engine(
                'Heute gibt es\n'
                '@essen mit\n'
                '@(beilage).\n',
            )

        self.assertRaises(NameError, template.apply, ({
                'random':  'value',
            }))


if __name__ == '__main__':
    unittest.main()
