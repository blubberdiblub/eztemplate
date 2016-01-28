#!/usr/bin/env python3
"""Provide the standard Python string.Template engine."""

from __future__ import print_function


from string import Template

from . import Engine


class StringTemplate(Engine):

    """String.Template engine."""

    handle = 'string.Template'

    def __init__(self, template, **kwargs):
        """Initialize string.Template."""
        super(StringTemplate, self).__init__(**kwargs)

        self.template = Template(template)

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        return self.template.substitute(mapping)
