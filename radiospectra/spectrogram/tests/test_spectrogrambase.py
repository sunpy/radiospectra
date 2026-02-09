import astropy.units as u
import numpy as np
import pytest
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram


def _make_spectrogram_with_time_array():
    times = Time("2020-01-01T00:00:00") + np.arange(10) * u.s
    freqs = np.linspace(10, 50, 5) * u.MHz
    meta = {
        "times": times,
        "freqs": freqs,
        "observatory": "TEST",
        "instrument": "TEST",
        "detector": "TEST",
        "start_time": times[0],
        "end_time": times[-1],
        "wavelength": a.Wavelength(freqs.min(), freqs.max()),
    }
    return GenericSpectrogram(np.zeros((5, 10)), meta)


def _make_spectrogram_with_quantity_array():
    start = Time("2020-01-01T00:00:00")
    times = np.arange(10) * u.s
    freqs = np.linspace(10, 50, 5) * u.MHz
    meta = {
        "times": times,
        "freqs": freqs,
        "observatory": "TEST",
        "instrument": "TEST",
        "detector": "TEST",
        "start_time": start,
        "end_time": start + times[-1],
        "wavelength": a.Wavelength(freqs.min(), freqs.max()),
    }
    return GenericSpectrogram(np.zeros((5, 10)), meta)


def test_set_times_updates_times_and_bounds():
    spec = _make_spectrogram_with_time_array()
    new_times = spec.times + 500 * u.s

    spec.times = new_times

    assert (spec.times == new_times).all()
    assert spec.start_time == new_times[0]
    assert spec.end_time == new_times[-1]


def test_set_times_supports_light_travel_time_offset():
    spec = _make_spectrogram_with_time_array()
    original_start = spec.start_time
    offset = 123 * u.s

    spec.times = spec.times + offset

    assert spec.start_time == original_start + offset
    assert spec.end_time == spec.times[-1]


def test_set_times_raises_for_wrong_length():
    spec = _make_spectrogram_with_time_array()

    with pytest.raises(ValueError, match="length"):
        spec.times = spec.times[:-1]


def test_set_times_raises_for_non_time_input():
    spec = _make_spectrogram_with_time_array()

    with pytest.raises(TypeError, match="Time"):
        spec.times = np.arange(10)


def test_set_times_raises_for_incompatible_quantity_units():
    spec = _make_spectrogram_with_time_array()

    with pytest.raises(ValueError, match="compatible with time"):
        spec.times = np.arange(10) * u.m


def test_set_times_updates_bounds_for_quantity_times():
    spec = _make_spectrogram_with_quantity_array()
    old_start = spec.start_time
    old_end = spec.end_time

    spec.times = spec.times + 30 * u.s

    assert spec.start_time == old_start + 30 * u.s
    assert spec.end_time == old_end + 30 * u.s
