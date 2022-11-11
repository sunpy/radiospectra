import numpy as np

from radiospectra.spectrum import Spectrum


def test_spectrum():
    spec = Spectrum(np.arange(10), np.arange(10))
    np.testing.assert_equal(spec.data, np.arange(10))
    np.testing.assert_equal(spec.freq_axis, np.arange(10))
