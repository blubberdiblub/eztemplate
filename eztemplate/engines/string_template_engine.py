#!/usr/bin/env python
"""Provide the standard Python string.Template engine."""

from __future__ import absolute_import
from __future__ import print_function

from string import Template

from . import Engine


class StringTemplate(Engine):

    """String.Template engine."""

    handle = 'string.Template'

    def __init__(self, template, tolerant=False, **kwargs):
        """Initialize string.Template."""
        super(StringTemplate, self).__init__(**kwargs)

        self.template = Template(template)
        self.tolerant = tolerant

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        mapping = {name: self.str(value, tolerant=self.tolerant)
                   for name, value in mapping.items()
                   if value is not None or self.tolerant}

        if self.tolerant:
            return self.template.safe_substitute(mapping)

        return self.template.substitute(mapping)
