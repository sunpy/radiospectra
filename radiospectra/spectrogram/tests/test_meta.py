import pytest

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram.meta import SpectrogramMeta


def test_spectrogram_meta_required_keys():
    meta = SpectrogramMeta(
        {
            "instrument": "test_inst",
            "observatory": "test_obs",
            "detector": "test_det",
            "start_time": "2020-01-01",
            "end_time": "2020-01-02",
        }
    )

    assert meta.instrument == "test_inst"
    assert meta.observatory == "test_obs"
    assert meta.detector == "test_det"
    assert meta.date_start == Time("2020-01-01")
    assert meta.date_end == Time("2020-01-02")


def test_spectrogram_meta_missing_required():
    meta = SpectrogramMeta({})
    with pytest.raises(KeyError):
        _ = meta.instrument


def test_spectrogram_meta_optional_keys():
    meta = SpectrogramMeta(
        {
            "processing_level": "L2",
            "version": "1.0",
            "wavelength": a.Wavelength(1 * u.kHz, 10 * u.kHz),
        }
    )

    assert meta.processing_level == "L2"
    assert meta.version == "1.0"
    assert meta.frequency_range == a.Wavelength(1 * u.kHz, 10 * u.kHz)
    assert meta.temporal_resolution is None
