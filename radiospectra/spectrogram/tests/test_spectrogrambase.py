from unittest import mock

import matplotlib.pyplot as plt
import numpy as np

import astropy.units as u


def test_plot_mixed_frequency_units_on_same_axes(make_spectrogram):
    """Two spectrograms with different frequency units should plot on the same axes."""
    rad1 = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    rad2 = make_spectrogram(np.array([1, 2, 3, 4]) * u.MHz)

    rad1.plot()
    axes = plt.gca()
    rad2.plot(axes=axes)

    # The y-axis unit should be set by the first spectrogram (kHz)
    assert axes.yaxis.units == u.kHz
    # The y-axis range should cover the converted MHz values (up to 4000 kHz)
    y_min, y_max = axes.get_ylim()
    plt.close("all")

    assert y_max > 1000, "MHz values should be converted to kHz on the y-axis"


def test_plot_mixed_frequency_units_mhz_first(make_spectrogram):
    """Plot MHz spectrogram first, then kHz — units should stay as MHz."""
    rad1 = make_spectrogram(np.array([1, 2, 3, 4]) * u.MHz)
    rad2 = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)

    rad1.plot()
    axes = plt.gca()
    rad2.plot(axes=axes)

    # The y-axis unit should be set by the first spectrogram (MHz)
    assert axes.yaxis.units == u.MHz
    # kHz values should be converted to MHz; 40 kHz = 0.04 MHz
    y_min, y_max = axes.get_ylim()
    plt.close("all")

    assert y_max >= 4, "y-axis should cover up to 4 MHz"


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


# --------- Tests for GenericSpectrogram.slice() ---------


def test_slice_by_time_only(make_spectrogram):
    """Slicing by time should keep only matching rows."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    t0 = spec.times[1]
    t1 = spec.times[2]

    sliced = spec.slice(time=(t0, t1))

    assert sliced.data.shape == (2, 4)
    np.testing.assert_array_equal(sliced.times, spec.times[1:3])
    np.testing.assert_array_equal(sliced.frequencies, spec.frequencies)
    np.testing.assert_array_equal(sliced.data, spec.data[1:3, :])
    assert sliced.start_time == t0
    assert sliced.end_time == t1


def test_slice_by_freq_only(make_spectrogram):
    """Slicing by frequency should keep only matching columns."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    sliced = spec.slice(freq=(20 * u.kHz, 30 * u.kHz))

    assert sliced.data.shape == (4, 2)
    np.testing.assert_array_equal(sliced.frequencies, np.array([20, 30]) * u.kHz)
    np.testing.assert_array_equal(sliced.data, spec.data[:, 1:3])


def test_slice_by_time_and_freq(make_spectrogram):
    """Slicing by both axes simultaneously."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    t0, t1 = spec.times[1], spec.times[2]
    sliced = spec.slice(time=(t0, t1), freq=(20 * u.kHz, 30 * u.kHz))

    assert sliced.data.shape == (2, 2)
    np.testing.assert_array_equal(sliced.data, spec.data[1:3, 1:3])


def test_slice_no_arguments_returns_copy(make_spectrogram):
    """Calling slice() with no arguments returns equivalent spectrogram."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    sliced = spec.slice()

    assert sliced is not spec
    assert sliced.data.shape == spec.data.shape
    np.testing.assert_array_equal(sliced.data, spec.data)
    np.testing.assert_array_equal(sliced.times, spec.times)
    np.testing.assert_array_equal(sliced.frequencies, spec.frequencies)


def test_slice_with_string_times(make_spectrogram):
    """Time range can be given as ISO-format strings."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    sliced = spec.slice(time=("2020-01-01 00:01", "2020-01-01 00:02"))

    assert sliced.data.shape[0] == 2
    assert sliced.start_time == spec.times[1]
    assert sliced.end_time == spec.times[2]


def test_slice_freq_with_unit_conversion(make_spectrogram):
    """Frequency limits in a different unit should be converted automatically."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    sliced = spec.slice(freq=(0.015 * u.MHz, 0.035 * u.MHz))

    assert sliced.data.shape == (4, 2)
    np.testing.assert_array_equal(sliced.frequencies.value, [20, 30])


def test_slice_preserves_class(make_spectrogram):
    """Sliced result should be the same class as the original."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    sliced = spec.slice(freq=(10 * u.kHz, 30 * u.kHz))

    assert type(sliced) is type(spec)


def test_slice_does_not_modify_original(make_spectrogram):
    """The original spectrogram must remain unchanged after slicing."""
    spec = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    original_shape = spec.data.shape
    original_times_len = len(spec.times)
    original_freqs_len = len(spec.frequencies)

    spec.slice(time=(spec.times[1], spec.times[2]), freq=(20 * u.kHz, 30 * u.kHz))

    assert spec.data.shape == original_shape
    assert len(spec.times) == original_times_len
    assert len(spec.frequencies) == original_freqs_len
