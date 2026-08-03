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


def test_slice_by_time_objects(spec):
    start = spec.times[2]
    end = spec.times[5]
    sliced = spec[:, start:end]
    assert sliced.shape == (5, 3)
    assert sliced.times[0] == start
    assert sliced.times[-1] == spec.times[4]


def test_slice_by_time_strings(spec):
    sliced = spec[:, "2021-01-01T00:00:02":"2021-01-01T00:00:05"]
    assert sliced.shape == (5, 3)
    assert sliced.times[0] == spec.times[2]
    assert sliced.times[-1] == spec.times[4]


def test_slice_by_frequency_quantities(spec):
    low = spec.frequencies[1]
    high = spec.frequencies[3]
    sliced = spec[low:high, :]
    assert sliced.shape == (2, 10)
    assert sliced.frequencies[0] == low
    assert sliced.frequencies[-1] == spec.frequencies[2]


def test_slice_by_time_and_frequency(spec):
    sliced = spec[spec.frequencies[1] : spec.frequencies[3], spec.times[2] : spec.times[5]]
    assert sliced.shape == (2, 3)


def test_single_time_index(spec):
    sliced = spec[:, spec.times[2]]
    assert sliced.shape == (5,)
    assert (sliced.frequencies == spec.frequencies).all()


def test_single_frequency_index(spec):
    sliced = spec[spec.frequencies[2], :]
    assert sliced.shape == (10,)
    assert (sliced.times == spec.times).all()


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
