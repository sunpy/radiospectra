"""
The spectrogram2 module aims to provide a more sunpy-like interface to radiospectra data similar to.

that of `~sunpy.map.Map` and `~sunpy.timeseries.TimeSeries`.
"""

from radiospectra.spectrogram2.sources import (
    CALISTOSpectrogram,
    EOVSASpectrogram,
    RFSSpectrogram,
    SWAVESSpectrogram,
)
from radiospectra.spectrogram2.spectrogram import Spectrogram
