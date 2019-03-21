# -*- coding: utf-8 -*-
"""
radiospectra
============

Provide support for some type of radiospectra on solar physics.
"""
# Enforce Python version check during package import.
# This is the same check as the one at the top of setup.py
from __future__ import absolute_import, division, print_function

import sys

__minimum_python_version__ = "2.7"


class UnsupportedPythonError(Exception):
    pass


if sys.version_info < tuple((int(val) for val in __minimum_python_version__.split('.'))):
    raise UnsupportedPythonError("sunpy does not support Python < {}".format(__minimum_python_version__))

# this indicates whether or not we are in the package's setup.py
try:
    _SUNPY_SETUP_
except NameError:
    try:
        import builtins
    except ImportError:
        import __builtin__ as builtins
    builtins._SUNPY_SETUP_ = False

try:
    from .version import version as __version__
except ImportError:
    __version__ = ''
try:
    from .version import githash as __githash__
except ImportError:
    __githash__ = ''
