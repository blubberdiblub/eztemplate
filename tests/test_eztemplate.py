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

import argparse
import string
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import eztemplate


class TestArgumentParser(unittest.TestCase):

    def test_empty_arguments(self):
        parser = eztemplate.argument_parser()
        args = parser.parse_args([])
        self.assertDictEqual(args.__dict__, {
                'arg':      None,
                'engine':   'string.Template',
                'file':     [sys.stdin],
                'outfile':  sys.stdout,
                'delete_empty': False,
                'tolerant': False,
            })

    def test_one_argument_and_output_delete_empty(self):
        parser = eztemplate.argument_parser()
        mock_open = mock.mock_open()
        mock_open.return_value = '<filehandle>'
        with mock.patch.object(builtins, 'open', mock_open):
            args = parser.parse_args([
                    '--outfile=template2',
                    '--delete-empty',
                    'template1',
                ])
        self.assertEqual(mock_open.call_count, 2)
        self.assertDictEqual(args.__dict__, {
                'arg':      None,
                'engine':   'string.Template',
                'file':     ['<filehandle>'],
                'outfile':  '<filehandle>',
                'delete_empty': True,
                'tolerant': False,
            })

    def test_engine_tolerant_stdout_args_multiple_files(self):
        parser = eztemplate.argument_parser()
        mock_open = mock.mock_open()
        mock_open.return_value = '<filehandle>'
        with mock.patch.object(builtins, 'open', mock_open):
            args = parser.parse_args([
                    '-e', 'string.Template',
                    '--tolerant',
                    '-a', 'beilage=Kartoffeln',
                    '--arg', 'essen=Szegediner Gulasch',
                    'template1',
                    'template2',
                ])
        self.assertEqual(mock_open.call_count, 2)
        self.assertDictEqual(args.__dict__, {
                'arg':      [
                    'beilage=Kartoffeln',
                    'essen=Szegediner Gulasch',
                    ],
                'engine':   'string.Template',
                'file':     [
                    '<filehandle>',
                    '<filehandle>',
                    ],
                'outfile':  sys.stdout,
                'delete_empty': False,
                'tolerant': True,
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
