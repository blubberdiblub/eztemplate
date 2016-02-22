#!/usr/bin/env python
"""Provide the mako templating engine."""

from __future__ import absolute_import
from __future__ import print_function


from mako.template import Template
from mako.lookup import TemplateLookup

from . import Engine


class MakoEngine(Engine):

    """Mako templating engine."""

    handle = 'mako'

    def __init__(self, template, dirname=None, tolerant=False, **kwargs):
        """Initialize mako template."""
        super(MakoEngine, self).__init__(**kwargs)

        directories = [dirname] if dirname is not None else ['.']
        lookup = TemplateLookup(directories=directories)

        default_filters = ['filter_undefined'] if tolerant else None
        encoding_errors = 'replace' if tolerant else 'strict'
        imports = ['def filter_undefined(value):\n'
                   '    if value is UNDEFINED:\n'
                   '        return \'<UNDEFINED>\'\n'
                   '    return value\n']
        self.template = Template(template,
                                 default_filters=default_filters,
                                 encoding_errors=encoding_errors,
                                 imports=imports,
                                 lookup=lookup,
                                 strict_undefined=not tolerant,
                                 )

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        return self.template.render(**mapping)
