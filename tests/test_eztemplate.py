#!/usr/bin/env python

from __future__ import print_function

import unittest

try:
    from unittest import mock
except ImportError:
    import mock

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

import string
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import eztemplate


class TestArgumentParser(unittest.TestCase):

    def test_empty_arguments(self):
        args = eztemplate.parse_args([])
        self.assertDictEqual(vars(args), {
                'args':         [{}],
                'concatenate':  False,
                'delete_empty': False,
                'engine':       'string.Template',
                'infiles':      [sys.stdin],
                'outfiles':     [sys.stdout],
                'tolerant':     False,
                'vary':         None,
            })

    def test_one_argument_and_output_delete_empty(self):
        args = eztemplate.parse_args([
                '--outfile=template2',
                '--delete-empty',
                'template1',
            ])
        self.assertDictEqual(vars(args), {
                'args':         [{}],
                'concatenate':  False,
                'delete_empty': True,
                'engine':       'string.Template',
                'infiles':      ['template1'],
                'outfiles':     ['template2'],
                'tolerant':     False,
                'vary':         None,
            })

    def test_engine_tolerant_stdout_concatenate_args_multiple_files(self):
        args = eztemplate.parse_args([
                '-e', 'string.Template',
                '--tolerant',
                '--stdout',
                '--concatenate',
                '-a', 'beilage=Kartoffeln',
                '--arg', 'essen=Szegediner Gulasch',
                'template1',
                'template2',
            ])
        self.assertDictEqual(vars(args), {
                'args':         [{
                                    'beilage': 'Kartoffeln',
                                    'essen':   'Szegediner Gulasch',
                                }],
                'concatenate':  True,
                'delete_empty': False,
                'engine':       'string.Template',
                'infiles':      [
                                    'template1',
                                    'template2',
                                ],
                'outfiles':     [sys.stdout],
                'tolerant':     True,
                'vary':         None,
            })

    def test_engine_separator_template_separator_args(self):
        args = eztemplate.parse_args([
                '--engine', 'string.Template',
                '--',
                'template',
                '--',
                'beilage=Kartoffeln',
                'essen=Szegediner Gulasch',
            ])
        self.assertDictEqual(vars(args), {
                'args':         [{
                                    'beilage': 'Kartoffeln',
                                    'essen':   'Szegediner Gulasch',
                                }],
                'concatenate':  False,
                'delete_empty': False,
                'engine':       'string.Template',
                'infiles':      ['template'],
                'outfiles':     [sys.stdout],
                'tolerant':     False,
                'vary':         None,
            })


class TestCheckEngine(unittest.TestCase):
    
    def test_help(self):
        mock_dump_engines = mock.Mock()
        with mock.patch('eztemplate.dump_engines', mock_dump_engines):
            try:
                eztemplate.check_engine('help')
            except SystemExit as e:
                self.assertEqual(e.args[0], 0, "didn't exit with return code 0")
            else:
                self.fail("didn't exit")

        mock_dump_engines.assert_called_once_with()

    def test_unavailable_engine(self):
        mock_stderr = StringIO()
        with mock.patch('sys.stderr', mock_stderr):
            try:
                eztemplate.check_engine('<NONEXISTENT_ENGINE>')
            except SystemExit as e:
                self.assertEqual(e.args[0], 1, "didn't exit with return code 1")
            else:
                self.fail("didn't exit")

        self.assertEqual(mock_stderr.getvalue().strip(),
                         'Engine "<NONEXISTENT_ENGINE>" is not available.')

    def test_built_in_engines(self):
        for engine in ('string.Template',):
            eztemplate.check_engine(engine)


if __name__ == '__main__':
    unittest.main()
