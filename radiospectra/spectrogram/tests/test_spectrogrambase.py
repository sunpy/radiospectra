from unittest import mock

import matplotlib.pyplot as plt
import numpy as np

import astropy.units as u
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


def test_plot_uses_time_support_for_datetime_conversion():
    spec = _get_spectrogram_with_time_scale("tt")

    mesh = spec.plot()
    x_limits = np.array(mesh.axes.get_xlim())
    expected_tt_limits = mesh.axes.convert_xunits(spec.times[[0, -1]])

    plt.close(mesh.axes.figure)

    np.testing.assert_allclose(x_limits, expected_tt_limits)


def test_plotim_uses_time_support_for_datetime_conversion():
    spec = _get_spectrogram_with_time_scale("tt")
    fig, axes = plt.subplots()

    with (
        mock.patch("matplotlib.image.NonUniformImage.set_interpolation", autospec=True),
        mock.patch("matplotlib.image.NonUniformImage.set_data", autospec=True) as set_data,
    ):
        spec.plotim(fig=fig, axes=axes)

    plt.close(fig)

    _, x_values, y_values, image = set_data.call_args.args
    expected_tt = axes.convert_xunits(spec.times)

    np.testing.assert_allclose(x_values, expected_tt)
    np.testing.assert_allclose(y_values, spec.frequencies.value)
    np.testing.assert_allclose(image, spec.data)
