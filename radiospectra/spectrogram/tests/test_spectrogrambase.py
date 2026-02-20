from unittest import mock

import matplotlib.pyplot as plt
import numpy as np

import astropy.units as u

from radiospectra.mixins import _get_axis_converter


def test_plot_mixed_frequency_units_on_same_axes(make_spectrogram):
    """Two spectrograms with different frequency units should plot on the same axes."""
    rad1 = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    rad2 = make_spectrogram(np.array([1, 2, 3, 4]) * u.MHz)
    fig, axes = plt.subplots()

    rad1.plot(axes=axes)
    rad2.plot(axes=axes)

    # The y-axis unit should be set by the first spectrogram (kHz)
    y_label = axes.get_ylabel()
    # The y-axis range should cover the converted MHz values (up to 4000 kHz)
    y_min, y_max = axes.get_ylim()
    plt.close(fig)

    assert "kHz" in y_label
    assert y_max > 1000, "MHz values should be converted to kHz on the y-axis"


def test_plotim(make_spectrogram):
    """Test NonUniformImagePlotMixin.plotim() executes without error."""
    rad_im = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    with (
        mock.patch("matplotlib.image.NonUniformImage.set_interpolation", autospec=True),
        mock.patch("matplotlib.image.NonUniformImage.set_data", autospec=True) as set_data,
    ):
        rad_im.plotim()
    plt.close("all")

    _, x_values, y_values, image = set_data.call_args.args
    assert len(x_values) == len(rad_im.times)
    np.testing.assert_allclose(y_values, rad_im.frequencies.value)
    np.testing.assert_allclose(image, rad_im.data)


def test_plotim_mixed_frequency_units_on_same_axes(make_spectrogram):
    """Two NonUniformImage plots with different units should share conversion."""
    rad1 = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    rad2 = make_spectrogram(np.array([1, 2, 3, 4]) * u.MHz)
    fig, axes = plt.subplots()
    with (
        mock.patch("matplotlib.image.NonUniformImage.set_interpolation", autospec=True),
        mock.patch("matplotlib.image.NonUniformImage.set_data", autospec=True) as set_data,
    ):
        rad1.plotim(axes=axes)
        rad2.plotim(axes=axes)
    plt.close(fig)

    _, _, y_values, _ = set_data.call_args.args
    np.testing.assert_allclose(y_values, np.array([1000, 2000, 3000, 4000]))


def test_plot_with_quantity_data(make_spectrogram):
    """Test plotting when data is an astropy Quantity."""
    rad = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    rad.data = rad.data * u.ct
    rad.plot()
    plt.close("all")


def test_plot_with_shape_mismatch(make_spectrogram):
    """Test plotting branch when data shape doesn't exactly match time/freq arrays."""
    rad = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    # times/freqs are length 4, data shape (4, 4) matches.
    # make data (5, 5) to trigger the `else` branch (data[:-1, :-1])
    rad.data = np.zeros((5, 5))
    rad.plot()
    plt.close("all")


def test_plot_instrument_detector_differ(make_spectrogram):
    """Test title generation when instrument and detector differ."""
    rad = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    # GenericSpectrogram gets instrument/detector from meta dictionary
    rad.meta["detector"] = "DifferentDetector"
    mesh = rad.plot()
    assert "DifferentDetector".upper() in mesh.axes.get_title().upper()
    plt.close("all")


def test_plot_uses_time_support_for_datetime_conversion(make_spectrogram):
    """Plotting with non-UTC time scale should use time_support."""
    spec = make_spectrogram(np.linspace(10, 40, 4) * u.MHz, scale="tt")

    mesh = spec.plot()
    x_limits = np.array(mesh.axes.get_xlim())
    expected_tt_limits = mesh.axes.convert_xunits(spec.times[[0, -1]])

    plt.close(mesh.axes.figure)

    np.testing.assert_allclose(x_limits, expected_tt_limits)


def test_plotim_uses_time_support_for_datetime_conversion(make_spectrogram):
    """plotim with non-UTC time scale should use time_support."""
    spec = make_spectrogram(np.linspace(10, 40, 4) * u.MHz, scale="tt")
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


def test_get_axis_converter_without_attribute():
    """_get_axis_converter should return None when no converter exists."""

    class DummyAxis:
        pass

    assert _get_axis_converter(DummyAxis()) is None
