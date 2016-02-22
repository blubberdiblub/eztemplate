#!/usr/bin/env python
"""Templating engine package."""

from __future__ import absolute_import
from __future__ import print_function

import collections
import itertools
import numbers
import sys

try:
    basestring
except NameError:
    basestring = str


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

    def str(self, value, tolerant=False, limit=1000, seen=frozenset()):
        """Transform value into a representation suitable for substitution."""
        if value is None:
            if tolerant:
                return ""

            raise ValueError("value is None")

        if isinstance(value, (bool, numbers.Number, basestring)):
            return str(value)

        if not isinstance(value, collections.Iterable):
            if not tolerant:
                raise ValueError("unknown value type")

            try:
                name = value.name
            except AttributeError:
                try:
                    name = value.__name__
                except AttributeError:
                    try:
                        name = value.__class__.__name__
                    except AttributeError:
                        return "<?>"

            return "<%s>" % (name,)

        is_mapping = isinstance(value, collections.Mapping)

        if not seen:
            wrap = "%s"
        elif is_mapping:
            wrap = "{%s}"
        else:
            wrap = "[%s]"

        id_ = id(value)
        if id_ in seen:
            if tolerant:
                return wrap % ("...",)
            raise ValueError("recursive representation")
        seen = seen.union((id_,))

        if is_mapping:
            items = [(self.str(n, tolerant=tolerant, limit=limit, seen=seen),
                      self.str(v, tolerant=tolerant, limit=limit, seen=seen))
                     for n, v in value.items()]
            items.sort()
            items = ("%s=%s" for n, v in items)
        else:
            it = iter(value)
            items = [self.str(item, tolerant=tolerant, limit=limit, seen=seen)
                     for item in itertools.islice(
                         it,
                         len(value)
                         if isinstance(value, collections.Sized)
                         else limit)]
            items.sort()
            try:
                next(it)
            except StopIteration:
                pass
            else:
                if not tolerant:
                    raise ValueError("iterable too long")
                items.append("...")

        return wrap % (", ".join(items),)

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
        match = re.match(r'^(?P<name>[A-Z_a-z]\w*)\.py[co]?$', filename)
        if match:
            module_names.add(match.group('name'))

    for module_name in module_names:
        try:
            module = importlib.import_module('.' + module_name, __name__)
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
