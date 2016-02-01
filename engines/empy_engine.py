#!/usr/bin/env python
"""Provide the empy templating engine."""

from __future__ import print_function


import em

from . import Engine


class EmpyEngine(Engine):

    """Empy templating engine."""

    handle = 'empy'

    def __init__(self, template, **kwargs):
        """Initialize empy template."""
        super(EmpyEngine, self).__init__(**kwargs)

        self.template = template

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        return em.expand(self.template, mapping)
