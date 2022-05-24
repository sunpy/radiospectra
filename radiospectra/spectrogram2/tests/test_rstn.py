from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import RSTNSpectrogram


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_rstn(parse_path_moc):
    start_time = Time("2020-01-01T06:17:38.000")
    end_time = Time("2020-01-01T15:27:43.000")
    meta = {
        "instrument": "RSTN",
        "observatory": "San Vito",
        "start_time": start_time,
        "end_time": end_time,
        "detector": "RSTN",
        "wavelength": a.Wavelength(25000.0 * u.kHz, 180000.0 * u.kHz),
        "freqs": np.concatenate([np.linspace(25, 75, 401), np.linspace(75, 180, 401)]) * u.MHz,
        "times": start_time + np.linspace(0, (end_time - start_time).to_value("s"), 11003) * u.s,
    }
    array = np.zeros((802, 11003))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fakes.srs")
    spec = Spectrogram(file)
    assert isinstance(spec, RSTNSpectrogram)
    assert spec.observatory == "SAN VITO"
    assert spec.instrument == "RSTN"
    assert spec.detector == "RSTN"
    assert spec.start_time.datetime == datetime(2020, 1, 1, 6, 17, 38)
    assert spec.end_time.datetime == datetime(2020, 1, 1, 15, 27, 43)
    assert spec.wavelength.min == 25000 * u.kHz
    assert spec.wavelength.max == 180000 * u.kHz
