import matplotlib

matplotlib.use("Agg")

import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram


@pytest.fixture
def make_spectrogram():
    """Factory fixture to create test spectrograms with given frequencies."""

    def _make(frequencies, times=None, scale="utc"):
        if times is None:
            times = Time("2020-01-01T00:00:00", format="isot", scale=scale) + np.arange(4) * u.min
        meta = {
            "observatory": "Test",
            "instrument": "TestInst",
            "detector": "TestDet",
            "start_time": times[0],
            "end_time": times[-1],
            "wavelength": np.array([1, 10]) * u.m,
            "times": times,
            "freqs": frequencies,
        }
        return GenericSpectrogram(np.arange(16).reshape(4, 4), meta)

    return _make
