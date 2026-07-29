from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram


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
    rad = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz, data=np.arange(16).reshape(4, 4) * u.ct)
    rad.plot()
    plt.close("all")


def test_data_shape_mismatch_is_rejected(make_spectrogram):
    """NDCube rejects replacing data with a different shape."""
    rad = make_spectrogram(np.array([10, 20, 30, 40]) * u.kHz)
    with pytest.raises(TypeError, match="same shape"):
        rad.data = np.zeros((5, 5))


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


def test_generic_spectrogram_from_dict():
    """Test creating a GenericSpectrogram from a raw dict and check properties/types/slicing."""
    times = Time("2021-01-01T00:00:00") + np.arange(10) * u.s
    freqs = np.linspace(10, 20, 5) * u.MHz
    data = np.random.rand(5, 10)

    meta_dict = {
        "instrument": "TestInstrument",
        "observatory": "TestObservatory",
        "detector": "TestDetector",
        "start_time": times[0],
        "end_time": times[-1],
        "wavelength": a.Wavelength(freqs[0], freqs[-1]),
        "times": times,
        "freqs": freqs,
    }

    spec = GenericSpectrogram(data, meta_dict)
    assert spec.instrument == "TESTINSTRUMENT"
    assert spec.observatory == "TESTOBSERVATORY"
    assert spec.detector == "TESTDETECTOR"
    assert isinstance(spec.start_time, Time)
    assert spec.start_time == times[0]
    assert isinstance(spec.end_time, Time)
    assert spec.end_time == times[-1]
    sliced = spec[1:3, 2:5]
    assert sliced.meta["instrument"] == "TestInstrument"


def test_crop_time(make_spectrogram):
    """Test cropping a spectrogram by time."""
    times = Time("2021-01-01T00:00:00") + np.arange(10) * u.s
    freqs = np.linspace(10, 20, 5) * u.MHz
    data = np.random.rand(5, 10)
    spec = make_spectrogram(freqs, data=data, times=times)

    start = times[2]
    end = times[5]

    cropped = spec.crop_time(start, end)
    assert cropped.shape == (5, 4)
    assert cropped.times[0] == start
    assert cropped.times[-1] == end
    assert (cropped.frequencies == spec.frequencies).all()


def test_crop_freq(make_spectrogram):
    """Test cropping a spectrogram by frequency."""
    times = Time("2021-01-01T00:00:00") + np.arange(10) * u.s
    freqs = np.linspace(10, 20, 5) * u.MHz
    data = np.random.rand(5, 10)
    spec = make_spectrogram(freqs, data=data, times=times)

    low = freqs[1]
    high = freqs[3]

    cropped = spec.crop_freq(low, high)
    assert cropped.shape == (3, 10)
    assert cropped.frequencies[0] == low
    assert cropped.frequencies[-1] == high
    assert (cropped.times == spec.times).all()
