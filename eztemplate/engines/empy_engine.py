#!/usr/bin/env python
"""Provide the empy templating engine."""

from __future__ import absolute_import
from __future__ import print_function

import os.path

import em

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from . import Engine


class SubsystemWrapper(em.Subsystem):

    """Wrap EmPy's Subsystem class.

    Allows to open files relative to a base directory.
    """

    def __init__(self, basedir=None, **kwargs):
        """Initialize Subsystem plus a possible base directory."""
        em.Subsystem.__init__(self, **kwargs)

        self.basedir = basedir

    def open(self, name, *args, **kwargs):
        """Open file, possibly relative to a base directory."""
        if self.basedir is not None:
            name = os.path.join(self.basedir, name)

        return em.Subsystem.open(self, name, *args, **kwargs)


class EmpyEngine(Engine):

    """Empy templating engine."""

    handle = 'empy'

    def __init__(self, template, dirname=None, **kwargs):
        """Initialize empy template."""
        super(EmpyEngine, self).__init__(**kwargs)

        if dirname is not None:
            # FIXME: This is a really bad idea, as it works like a global.
            # Blame EmPy.
            em.theSubsystem = SubsystemWrapper(basedir=dirname)

        self.output = StringIO()
        self.interpreter = em.Interpreter(output=self.output)
        self.template = template

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        self.output.seek(0)
        self.output.truncate(0)
        self.interpreter.string(self.template, locals=mapping)
        return self.output.getvalue()
