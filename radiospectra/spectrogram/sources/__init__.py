"""
Datasource-specific classes.

This is where datasource specific logic is implemented.
Each mission should have its own file with one or more classes defined.
"""

from ..spectrogram_factory import Spectrogram  # NOQA
from .callisto import *  # NOQA
from .eovsa import *  # NOQA
from .ilofar357 import *  # NOQA
from .psp_rfs import *  # NOQA
from .rpw import *  # NOQA
from .rstn import *  # NOQA
from .swaves import *  # NOQA
from .waves import *  # NOQA

__all__ = [
    "SWAVESSpectrogram",  # NOQA: F405
    "RFSSpectrogram",  # NOQA: F405
    "CALISTOSpectrogram",  # NOQA: F405
    "EOVSASpectrogram",  # NOQA: F405
    "RSTNSpectrogram",  # NOQA: F405
    "RPWSpectrogram",  # NOQA: F405
    "ILOFARMode357Spectrogram",  # NOQA: F405
]
