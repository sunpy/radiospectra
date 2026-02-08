import numpy as np
import pytest

from radiospectra.spectrum import Spectrum


def test_spectrum():
    spec = Spectrum(np.arange(10), np.arange(10))
    np.testing.assert_equal(spec.data, np.arange(10))
    np.testing.assert_equal(spec.freq_axis, np.arange(10))


def test_freq_at_index():
    data = [1, 2, 3]
    freqs = [100, 200, 300]
    spec = Spectrum(data, freqs)

    # Test valid indices
    assert spec.freq_at_index(0) == 100
    assert spec.freq_at_index(2) == 300

    # Test out-of-bounds index
    with pytest.raises(ValueError, match="Index out of bounds"):
        spec.freq_at_index(5)
