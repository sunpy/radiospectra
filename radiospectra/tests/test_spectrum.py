import numpy as np

from radiospectra.spectrum import Spectrum


def test_spectrum():
    spec = Spectrum(np.arange(10), np.arange(10))
    np.testing.assert_equal(spec.data, np.arange(10))
    np.testing.assert_equal(spec.freq_axis, np.arange(10))
def test_freq_axis_preserved_after_ufunc():
    data = np.arange(10)
    freq = np.linspace(100, 200, 10)

    spec = Spectrum(data, freq)

    new = np.sqrt(spec)

    assert isinstance(new, Spectrum)
    assert hasattr(new, "freq_axis")
    np.testing.assert_allclose(new.freq_axis, spec.freq_axis)


def test_freq_axis_preserved_after_binary_operation():
    data = np.arange(10)
    freq = np.linspace(100, 200, 10)

    spec = Spectrum(data, freq)

    new = spec + 5

    assert isinstance(new, Spectrum)
    assert hasattr(new, "freq_axis")
    np.testing.assert_allclose(new.freq_axis, spec.freq_axis)
