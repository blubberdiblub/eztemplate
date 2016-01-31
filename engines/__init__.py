#!/usr/bin/env python
"""Templating engine package."""

from __future__ import print_function

import sys


class Engine(object):

    """Abstract class representing a templating engine."""

    handle = None

    def __init__(self, dirname=None, tolerant=False, **kwargs):
        """Initialize template, potentially "compiling" it."""
        assert self.__class__ is not Engine, (
                "must only instantiate subclasses of Engine")

        super(Engine, self).__init__(**kwargs)

        if tolerant:
            print("WARNING: This engine doesn't support tolerant mode",
                  file=sys.stderr)

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        raise NotImplementedError


engines = {}


def _init():
    """Dynamically import engines that initialize successfully."""
    import importlib
    import os
    import re

    filenames = os.listdir(os.path.dirname(__file__))

    module_names = set()
    for filename in filenames:
        match = re.match(r'^(?P<name>[^_\W]\w*)\.py[co]?$', filename)
        if match:
            module_names.add(match.group('name'))

    for module_name in module_names:
        try:
            module = importlib.import_module('.' + module_name, __package__)
        except ImportError:
            continue

        for name, member in module.__dict__.items():
            if not isinstance(member, type):
                # skip non-new-style classes
                continue
            if not issubclass(member, Engine):
                # skip non-subclasses of Engine
                continue
            if member is Engine:
                # skip "abstract" class Engine
                continue

            try:
                handle = member.handle
            except AttributeError:
                continue

            engines[handle] = member


_init()
