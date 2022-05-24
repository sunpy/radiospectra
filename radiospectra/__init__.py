"""
Radiospectra
============

An open-source Python library for radio spectra in solar physics.

* Homepage: https://sunpy.org
* Documentation: https://docs.radiospectra.org/en/stable/
* Source code: https://github.com/sunpy/radiospectra
"""
import sys

from .version import version as __version__

# Enforce Python version check during package import.
__minimum_python_version__ = "3.7"


class UnsupportedPythonError(Exception):
    """
    Running on an unsupported version of Python.
    """


if sys.version_info < tuple(int(val) for val in __minimum_python_version__.split(".")):
    # This has to be .format to keep backwards compatibly.
    raise UnsupportedPythonError("sunpy does not support Python < {}".format(__minimum_python_version__))

__all__ = ["__version__"]
