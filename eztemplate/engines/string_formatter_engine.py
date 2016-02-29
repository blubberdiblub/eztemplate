#!/usr/bin/env python
"""Provide the standard Python string.Formatter engine."""

from __future__ import absolute_import
from __future__ import print_function

import string

try:
    basestring
except NameError:
    basestring = str

from . import Engine


class MissingField(object):

    """Represent a missing field for unprocessed output."""

    def __init__(self, field_name):
        """Initialize field name."""
        self.field_name = field_name
        self.conversion = None
        self.format_spec = None

    def __str__(self):
        """Yield representation as close to original spec as possible."""
        return '{%s%s%s}' % (
                self.field_name,
                '!' + self.conversion if self.conversion else '',
                ':' + self.format_spec if self.format_spec else '',
            )


class FormatterWrapper(string.Formatter):

    """Wrap string.Formatter.

    Handle only a mapping and provide tolerance.
    """

    def __init__(self, tolerant=False, **kwargs):
        """Initialize FormatterWrapper."""
        super(FormatterWrapper, self).__init__(**kwargs)

        self.tolerant = tolerant

    def get_value(self, key, args, kwargs):
        """Get value only from mapping and possibly convert key to string."""
        if (self.tolerant and
                not isinstance(key, basestring) and
                key not in kwargs):
            key = str(key)

        return kwargs[key]

    def get_field(self, field_name, args, kwargs):
        """Create a special value when field missing and tolerant."""
        try:
            obj, arg_used = super(FormatterWrapper, self).get_field(
                    field_name, args, kwargs)
        except (KeyError, IndexError, AttributeError):
            if not self.tolerant:
                raise

            obj = MissingField(field_name)
            arg_used = field_name

        return obj, arg_used

    def convert_field(self, value, conversion):
        """When field missing, store conversion specifier."""
        if isinstance(value, MissingField):
            if conversion is not None:
                value.conversion = conversion
            return value

        return super(FormatterWrapper, self).convert_field(value, conversion)

    def format_field(self, value, format_spec):
        """When field missing, return original spec."""
        if isinstance(value, MissingField):
            if format_spec is not None:
                value.format_spec = format_spec
            return str(value)

        return super(FormatterWrapper, self).format_field(value, format_spec)


class StringFormatter(Engine):

    """String.Formatter engine."""

    handle = 'string.Formatter'

    def __init__(self, template, tolerant=False, **kwargs):
        """Initialize string.Formatter."""
        super(StringFormatter, self).__init__(**kwargs)

        self.template = template
        self.formatter = FormatterWrapper(tolerant=tolerant)

    def apply(self, mapping):
        """Apply a mapping of name-value-pairs to a template."""
        return self.formatter.vformat(self.template, None, mapping)
