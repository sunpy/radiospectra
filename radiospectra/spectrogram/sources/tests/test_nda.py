from pathlib import Path
from unittest import mock

import numpy as np
import pytest

import astropy.units as u
from astropy.tests.helper import assert_quantity_allclose
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.sources import NDASpectrogram


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_nda(parse_path_moc):
    meta = {
        "fits_meta": {
            "TELESCOP": "NDA",
            "INSTRUME": "NEWROUTINE",
            "OBSGEO-B": 47.37,
            "OBSGEO-L": 2.19,
            "OBSGEO-H": 150.0,
        },
        "detector": "NEWROUTINE",
        "instrument": "NDA",
        "observatory": "ORN",
        "start_time": Time("2025-03-26T07:56:27.260"),
        "end_time": Time("2025-03-26T15:55:00.000"),
        "wavelength": a.Wavelength(10.01 * u.MHz, 87.99 * u.MHz),
        "times": Time("2025-03-26T07:56:27.260") + np.arange(10) * u.s,
        "freqs": np.linspace(10.01, 87.99, 50) * u.MHz,
        "polarisation": "LL",
    }
    array = np.zeros((50, 10))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake_nda.fits")
    spec = Spectrogram(file)
    assert isinstance(spec, NDASpectrogram)
    assert spec.observatory == "ORN"
    assert spec.instrument == "NDA"
    assert spec.detector == "NEWROUTINE"
    assert spec.start_time.isot == "2025-03-26T07:56:27.260"
    assert spec.wavelength.min.to(u.MHz).value == 10.01
    assert spec.wavelength.max.to(u.MHz).value == 87.99
    assert spec.polarisation == "LL"
    assert np.isclose(spec.observatory_location.lat.value, 47.37)
    assert np.isclose(spec.observatory_location.lon.value, 2.19)


@pytest.mark.remote_data
def test_nda_spectrogram_online():
    url = "https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/2025/03/orn_nda_newroutine_sun_edr_202503260756_202503261555_v1.1.fits"
    specs = Spectrogram(url)
    assert isinstance(specs, list)
    assert len(specs) == 2

    spec = specs[0]

    assert spec.instrument == "NDA"
    assert spec.detector == "NEWROUTINE"
    assert spec.polarisation in ["LL", "RR"]
    assert spec.observatory_location is not None
    assert spec.observatory_location.lat.value > 47.0
    assert spec.observatory_location.lon.value > 2.0

    assert spec.times[0].isot == "2025-03-26T07:56:27.260"
    assert_quantity_allclose(spec.frequencies[0], 10.01 * u.MHz, rtol=1e-3)
    assert_quantity_allclose(spec.frequencies[-1], 87.99 * u.MHz, rtol=1e-3)
