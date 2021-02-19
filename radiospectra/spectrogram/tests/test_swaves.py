from pathlib import Path
from datetime import datetime

import astropy.units as u

from radiospectra import data
from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.sources import SWAVESSpectrogram


def test_swaves_lfr():
    file = Path(data.__file__).parent / 'swaves_average_20201128_a_lfr.dat'
    spec = Spectrogram(file)
    assert isinstance(spec, SWAVESSpectrogram)
    assert spec.observatory == 'STEREO A'
    assert spec.instrument == 'SWAVES'
    assert spec.detector == 'LFR'
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 2.6 * u.kHz
    assert spec.wavelength.max == 153.4 * u.kHz


def test_swaves_hfr():
    file = Path(data.__file__).parent / 'swaves_average_20201128_a_hfr.dat'
    spec = Spectrogram(file)
    assert isinstance(spec, SWAVESSpectrogram)
    assert spec.observatory == 'STEREO A'
    assert spec.instrument == 'SWAVES'
    assert spec.detector == 'HFR'
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 125 * u.kHz
    assert spec.wavelength.max == 16025 * u.kHz
