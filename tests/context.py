#!/usr/bin/env python
"""Provide explicit import context for tests."""

from __future__ import absolute_import
from __future__ import print_function

import os.path
import sys
sys.path.insert(0, os.path.abspath('..'))

import eztemplate
import eztemplate.__main__
import eztemplate.engines as engines
