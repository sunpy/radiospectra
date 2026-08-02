import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram


@pytest.fixture
def spec():
    times = Time("2021-01-01T00:00:00") + np.arange(10) * u.s
    freqs = np.linspace(10, 20, 5) * u.MHz
    data = np.random.rand(5, 10)
    meta_dict = {
        "instrument": "TestInstrument",
        "observatory": "TestObservatory",
        "detector": "TestDetector",
        "start_time": times[0],
        "end_time": times[-1],
        "wavelength": u.Quantity([freqs[0], freqs[-1]]),
        "times": times,
        "freqs": freqs,
    }
    return GenericSpectrogram(data, meta_dict)


def test_time_profile_method(spec):
    freq = spec.frequencies[2]
    profile = spec.time_profile(freq)
    assert profile.shape == (10,)
    assert (profile.times == spec.times).all()


def test_line_profile_method(spec):
    time_val = spec.times[3]
    profile = spec.line_profile(time_val)
    assert profile.shape == (5,)
    assert (profile.frequencies == spec.frequencies).all()
