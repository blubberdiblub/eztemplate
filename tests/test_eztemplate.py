#!/usr/bin/env python

from __future__ import absolute_import
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

from .context import eztemplate


class TestArgumentParser(unittest.TestCase):

    def test_empty_arguments(self):
        args = eztemplate.__main__.parse_args([])
        self.assertDictEqual(vars(args), {
                'args':         [{}],
                'concatenate':  False,
                'delete_empty': False,
                'engine':       'string.Template',
                'infiles':      [sys.stdin],
                'outfiles':     [sys.stdout],
                'read_old':     False,
                'tolerant':     False,
                'vary':         False,
            })

    def test_one_argument_and_output_delete_empty(self):
        args = eztemplate.__main__.parse_args([
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
                'read_old':     False,
                'tolerant':     False,
                'vary':         False,
            })

    def test_engine_tolerant_stdout_concatenate_args_multiple_files(self):
        args = eztemplate.__main__.parse_args([
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
                'read_old':     False,
                'tolerant':     True,
                'vary':         False,
            })

    def test_engine_separator_template_separator_args(self):
        args = eztemplate.__main__.parse_args([
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
                'read_old':     False,
                'tolerant':     False,
                'vary':         False,
            })

    def test_fail_multiple_infiles(self):
        mock_stderr = StringIO()
        try:
            with mock.patch('sys.stderr', mock_stderr):
                eztemplate.__main__.parse_args([
                    '--args', 'foo=bar',
                    'template1',
                    'template2',
                ])
        except SystemExit as e:
            self.assertEqual(e.args[0], 2, "didn't exit with return code 2")
        else:
            self.fail("didn't exit")


class TestCheckEngine(unittest.TestCase):
    
    def test_help(self):
        mock_dump_engines = mock.Mock()
        with mock.patch('eztemplate.__main__.dump_engines', mock_dump_engines):
            try:
                eztemplate.__main__.parse_args(args=['-e', 'help'])
            except SystemExit as e:
                self.assertEqual(e.args[0], 0, "didn't exit with return code 0")
            else:
                self.fail("didn't exit")

        mock_dump_engines.assert_called_once_with()

    def test_unavailable_engine(self):
        mock_stdout = StringIO()
        mock_stderr = StringIO()
        with mock.patch('sys.stdout', mock_stdout), \
             mock.patch('sys.stderr', mock_stderr):
            try:
                eztemplate.__main__.parse_args(args=['-e', '<NONEXISTENT_ENGINE>'])
            except SystemExit as e:
                self.assertEqual(e.args[0], 2, "didn't exit with return code 2")
            else:
                self.fail("didn't exit")

        self.assertEqual(mock_stdout.getvalue(), '')
        self.assertIn("Engine '<NONEXISTENT_ENGINE>' is not available.",
                      mock_stderr.getvalue())

    def test_built_in_engines(self):
        for engine in ('string.Template',):
            eztemplate.__main__.check_engine(engine)


if __name__ == '__main__':
    unittest.main()
