#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import imp
import os.path


from .context import engines


class TestInit(unittest.TestCase):

    def test_init(self):
        mock_engines = {}

        mock_listdir = mock.Mock(return_value=(
                'text_engine.txt',
                '0_engine.py',
                '.period_engine.py',
                '@at_engine.py',
                '__init__.py',
                '_underscore_engine.py',
                'normal_engine.py',
                'compiled_engine.pyc',
                'optimized_engine.pyo',
            ))

        valid_engines = {
                '_underscore_engine':   ('UnderscoreEngine', 'underscore'),
                'normal_engine':        ('NormalEngine',     'normal'),
                'compiled_engine':      ('CompiledEngine',   'compiled'),
                'optimized_engine':     ('OptimizedEngine',  'optimized'),
            }

        result_dict = {handle: None for __, (__, handle) in valid_engines.items()}

        def mock_import_module(name, package):
            self.assertEqual(package, 'eztemplate.engines')

            assert name.startswith('.')
            name = name[1:]

            module = imp.new_module('%s.%s' % (package, name))

            if name == '__init__':
                module.Engine = engines.Engine
            else:
                self.assertIn(name, valid_engines)
                class_name, engine_handle = valid_engines[name]

                class MockEngine(engines.Engine):
                    handle = engine_handle

                MockEngine.__name__ = class_name
                MockEngine.__qualname__ = class_name

                result_dict[engine_handle] = MockEngine
                setattr(module, class_name, MockEngine)

            return module

        with mock.patch.object(engines, 'engines', mock_engines), \
             mock.patch('os.listdir', mock_listdir), \
             mock.patch('importlib.import_module', mock_import_module):
            engines._init()

        mock_listdir.assert_called_once_with(os.path.dirname(engines.__file__))
        self.assertDictEqual(mock_engines, result_dict)


class TestEngine(unittest.TestCase):

    def test_not_instantiable(self):
        self.assertRaises(AssertionError, engines.Engine, dirname='/tmp/', tolerant=False)

    def test_handle_is_none(self):
        class TestEngine(engines.Engine):
            pass

        engine = TestEngine(dirname='/tmp/', tolerant=False)

        self.assertIsNone(engine.handle)

    def test_apply_not_implemented(self):
        class TestEngine(engines.Engine):
            pass

        engine = TestEngine(dirname='/tmp/', tolerant=False)

        self.assertRaises(NotImplementedError, engine.apply, {})


if __name__ == '__main__':
    unittest.main()
