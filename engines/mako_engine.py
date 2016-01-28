#!/usr/bin/env python3
"""Provide the mako templating engine."""

from __future__ import print_function


from mako.template import Template
from mako.lookup import TemplateLookup

from . import Engine


class MakoEngine(Engine):

    """Mako templating engine."""

    handle = 'mako'

    def __init__(self, template, tolerant=False, **kwargs):
        """Initialize mako template."""
        super(MakoEngine, self).__init__(**kwargs)

        encoding_errors = 'replace' if tolerant else 'strict'
        lookup = TemplateLookup(directories=['.'])
        self.template = Template(template,
                                 lookup=lookup,
                                 encoding_errors=encoding_errors,
                                 )

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        return self.template.render(**mapping)
