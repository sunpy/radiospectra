from unittest import mock

import matplotlib

import astropy.units as u

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from astropy.time import Time

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram


def _get_spectrogram_with_time_scale(scale):
    times = Time("2020-01-01T00:00:00", format="isot", scale=scale) + np.arange(4) * u.min
    frequencies = np.linspace(10, 40, 4) * u.MHz
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


def test_plot_uses_utc_times_for_datetime_conversion():
    spec = _get_spectrogram_with_time_scale("tt")

    mesh = spec.plot()
    x_limits = np.array(mesh.axes.get_xlim())
    expected_utc_limits = mdates.date2num(spec.times.utc.datetime[[0, -1]])
    expected_tt_limits = mdates.date2num(spec.times.datetime[[0, -1]])
    plt.close(mesh.axes.figure)

    np.testing.assert_allclose(x_limits, expected_utc_limits)
    assert not np.allclose(x_limits, expected_tt_limits, rtol=0.0, atol=1e-6)


def test_plotim_uses_utc_times_for_datetime_conversion():
    spec = _get_spectrogram_with_time_scale("tt")
    fig, axes = plt.subplots()

    with (
        mock.patch("matplotlib.image.NonUniformImage.set_interpolation", autospec=True),
        mock.patch("matplotlib.image.NonUniformImage.set_data", autospec=True) as set_data,
    ):
        spec.plotim(fig=fig, axes=axes)
    plt.close(fig)

    _, x_values, y_values, image = set_data.call_args.args
    expected_utc = mdates.date2num(spec.times.utc.datetime)
    expected_tt = mdates.date2num(spec.times.datetime)

    np.testing.assert_allclose(x_values, expected_utc)
    assert not np.allclose(x_values, expected_tt, rtol=0.0, atol=1e-6)
    np.testing.assert_allclose(y_values, spec.frequencies.value)
    np.testing.assert_allclose(image, spec.data)
