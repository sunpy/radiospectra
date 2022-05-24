from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import WAVESSpectrogram


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_waves_rad1(parse_path_moc):
    meta = {
        "instrument": "WAVES",
        "observatory": "wind",
        "start_time": Time("2020-11-28 00:00:00"),
        "end_time": Time("2020-11-28 23:59:00"),
        "wavelength": a.Wavelength(20 * u.kHz, 1040 * u.kHz),
        "detector": "rad1",
        "freqs": np.linspace(20, 1040, 256) * u.kHz,
        "times": np.arange(1440) * u.min,
    }
    array = np.zeros((256, 1440))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.r1")
    spec = Spectrogram(file)
    assert isinstance(spec, WAVESSpectrogram)
    assert spec.observatory == "WIND"
    assert spec.instrument == "WAVES"
    assert spec.detector == "RAD1"
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 20.0 * u.kHz
    assert spec.wavelength.max == 1040.0 * u.kHz


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_waves_rad2(parse_path_moc):
    meta = {
        "instrument": "WAVES",
        "observatory": "WIND",
        "start_time": Time("2020-11-28 00:00:00"),
        "end_time": Time("2020-11-28 23:59:00"),
        "wavelength": a.Wavelength(1.075 * u.MHz, 13.825 * u.MHz),
        "detector": "RAD2",
        "freqs": np.linspace(1.075, 13.825, 256) * u.MHz,
        "times": np.arange(1440) * u.min,
    }
    array = np.zeros((319, 1440))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.dat")
    spec = Spectrogram(file)
    assert isinstance(spec, WAVESSpectrogram)
    assert spec.observatory == "WIND"
    assert spec.instrument == "WAVES"
    assert spec.detector == "RAD2"
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 1.075 * u.MHz
    assert spec.wavelength.max == 13.825 * u.MHz
