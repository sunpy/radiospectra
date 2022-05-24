from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import SWAVESSpectrogram


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_swaves_lfr(parse_path_moc):
    meta = {
        "instrument": "swaves",
        "observatory": "STEREO A",
        "product": "average",
        "start_time": Time("2020-11-28 00:00:00"),
        "end_time": Time("2020-11-28 23:59:00"),
        "wavelength": a.Wavelength(2.6 * u.kHz, 153.4 * u.kHz),
        "detector": "lfr",
        "freqs": [
            2.6,
            2.8,
            3.1,
            3.4,
            3.7,
            4.0,
            4.4,
            4.8,
            5.2,
            5.7,
            6.2,
            6.8,
            7.4,
            8.1,
            8.8,
            9.6,
            10.4,
            11.4,
            12.4,
            13.6,
            14.8,
            16.1,
            17.6,
            19.2,
            20.9,
            22.8,
            24.9,
            27.1,
            29.6,
            32.2,
            35.2,
            38.3,
            41.8,
            45.6,
            49.7,
            54.2,
            59.1,
            64.5,
            70.3,
            76.7,
            83.6,
            91.2,
            99.4,
            108.4,
            118.3,
            129.0,
            140.6,
            153.4,
        ]
        * u.kHz,
        "times": np.arange(1440) * u.min,
    }
    array = np.zeros((48, 1440))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.dat")
    spec = Spectrogram(file)
    assert isinstance(spec, SWAVESSpectrogram)
    assert spec.observatory == "STEREO A"
    assert spec.instrument == "SWAVES"
    assert spec.detector == "LFR"
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 2.6 * u.kHz
    assert spec.wavelength.max == 153.4 * u.kHz


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_swaves_hfr(parse_path_moc):
    meta = {
        "instrument": "swaves",
        "observatory": "STEREO A",
        "product": "average",
        "start_time": Time("2020-11-28 00:00:00"),
        "end_time": Time("2020-11-28 23:59:00"),
        "wavelength": a.Wavelength(125.0 * u.kHz, 16025.0 * u.kHz),
        "detector": "hfr",
        "freqs": np.linspace(125, 16025, 319) * u.kHz,
        "times": np.arange(1440) * u.min,
    }
    array = np.zeros((319, 1440))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.dat")
    spec = Spectrogram(file)
    assert isinstance(spec, SWAVESSpectrogram)
    assert spec.observatory == "STEREO A"
    assert spec.instrument == "SWAVES"
    assert spec.detector == "HFR"
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 125 * u.kHz
    assert spec.wavelength.max == 16025 * u.kHz
