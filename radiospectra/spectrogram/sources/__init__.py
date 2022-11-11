"""
Datasource-specific classes.

This is where datasource specific logic is implemented.
Each mission should have its own file with one or more classes defined.
"""

from ..spectrogram_factory import Spectrogram  # NOQA
from .callisto import *  # NOQA
from .eovsa import *  # NOQA
from .psp_rfs import *  # NOQA
from .rpw import *  # NOQA
from .rstn import *  # NOQA
from .swaves import *  # NOQA
from .waves import *  # NOQA

__all__ = [
    "SWAVESSpectrogram",
    "RFSSpectrogram",
    "CALISTOSpectrogram",
    "EOVSASpectrogram",
    "RSTNSpectrogram",
    "RPWSpectrogram",
]
