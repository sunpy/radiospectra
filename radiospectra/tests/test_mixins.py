import numpy as np

from astropy.time import Time

from radiospectra.mixins import PcolormeshPlotMixin


class MockSpectrogram(PcolormeshPlotMixin):
    def __init__(self, times, data):
        self.times = times
        self.data = data


def test_insert_time_gaps_no_gaps():
    times = Time(["2023-01-01T00:00:00", "2023-01-01T00:00:01", "2023-01-01T00:00:02"])
    data = np.ones((3, 5))
    spec = MockSpectrogram(times, data)

    new_times, new_data = spec._insert_time_gaps(times, data)

    assert len(new_times) == 3
    assert new_data.shape == (3, 5)
    assert not np.isnan(new_data).any()


def test_insert_time_gaps_with_gap():
    times = Time(["2023-01-01T00:00:00", "2023-01-01T00:00:01", "2023-01-01T00:00:11"])
    data = np.array([[1, 1], [2, 2], [3, 3]])
    spec = MockSpectrogram(times, data)

    new_times, new_data = spec._insert_time_gaps(times, data)

    assert len(new_times) == 4
    assert new_data.shape == (4, 2)

    assert new_times[2].isot == "2023-01-01T00:00:06.000"
    assert np.isnan(new_data[2]).all()

    np.testing.assert_array_equal(new_data[0], [1.0, 1.0])
    np.testing.assert_array_equal(new_data[1], [2.0, 2.0])
    np.testing.assert_array_equal(new_data[3], [3.0, 3.0])


def test_insert_time_gaps_multiple_gaps():
    times = Time(
        [
            "2023-01-01T00:00:00",
            "2023-01-01T00:00:01",
            "2023-01-01T00:00:10",
            "2023-01-01T00:00:11",
            "2023-01-01T00:00:20",
        ]
    )
    data = np.ones((5, 2))
    spec = MockSpectrogram(times, data)

    new_times, new_data = spec._insert_time_gaps(times, data)

    assert len(new_times) == 7
    assert new_data.shape == (7, 2)
    assert np.isnan(new_data[2]).all()
    assert np.isnan(new_data[5]).all()


def test_insert_time_gaps_float_input():
    """Verify that float data is copied, not cast again."""
    times = Time(["2023-01-01T00:00:00", "2023-01-01T00:00:01", "2023-01-01T00:00:11"])
    data = np.array([[1.5, 2.5], [3.5, 4.5], [5.5, 6.5]])
    spec = MockSpectrogram(times, data)

    new_times, new_data = spec._insert_time_gaps(times, data)

    assert len(new_times) == 4
    assert np.isnan(new_data[2]).all()
    np.testing.assert_array_equal(new_data[0], [1.5, 2.5])
    np.testing.assert_array_equal(new_data[3], [5.5, 6.5])


def test_insert_time_gaps_manual_threshold():
    """Verify that a manual gap_threshold overrides the automatic detection."""
    times = Time(["2023-01-01T00:00:00", "2023-01-01T00:00:01", "2023-01-01T00:00:04"])
    data = np.ones((3, 2))
    spec = MockSpectrogram(times, data)

    new_times, _ = spec._insert_time_gaps(times, data)
    assert len(new_times) == 4

    new_times_manual, new_data_manual = spec._insert_time_gaps(times, data, gap_threshold=5.0)
    assert len(new_times_manual) == 3
    assert not np.isnan(new_data_manual).any()
