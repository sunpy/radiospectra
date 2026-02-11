import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time, TimeDelta

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram


def _mk_spec(start, ntime=5, dt_s=1, nfreq=3):
    times = Time(start) + TimeDelta(np.arange(ntime) * dt_s * u.s)
    freqs = np.arange(nfreq) * u.MHz
    data = np.arange(nfreq * ntime).reshape(nfreq, ntime)

    meta = {
        "times": times,
        "freqs": freqs,
        "observatory": "TEST",
        "instrument": "TEST",
        "detector": "TEST",
        "start_time": times[0],
        "end_time": times[-1],
        "wavelength": (1 * u.m, 2 * u.m),
    }
    return GenericSpectrogram(data, meta)

def test_join_many_contiguous():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    b = _mk_spec("2020-01-01T00:00:05", ntime=5, dt_s=1)  # contiguous
    out = GenericSpectrogram.join_many([a, b], maxgap=TimeDelta(0 * u.s), fill_gaps=False)
    assert out.data.shape[1] == 10
    assert out.times[0] == a.times[0]
    assert out.times[-1] == b.times[-1]
    # Check simple data concat
    assert np.all(out.data[:, :5] == a.data)
    assert np.all(out.data[:, 5:] == b.data)

def test_join_many_gap_fill():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    # Ends at 04s. Next expected is 05s.
    # b starts at 08s. Gap is 05s, 06s, 07s (3 steps missing).
    b = _mk_spec("2020-01-01T00:00:08", ntime=5, dt_s=1)

    out = GenericSpectrogram.join_many([a, b], maxgap=None, fill_gaps=True)

    # a has 5 cols, missing 3, b has 5 cols => 13 total
    assert out.data.shape[1] == 13
    assert len(out.times) == 13

    # filled columns should repeat last column of a
    last_a = a.data[:, -1]
    # Columns 5, 6, 7 are filled
    assert np.all(out.data[:, 5] == last_a)
    assert np.all(out.data[:, 6] == last_a)
    assert np.all(out.data[:, 7] == last_a)

    # Check time continuity in filled region
    dt = TimeDelta(1*u.s)
    # Use loose comparison for floating point times
    # out.times[5] should be a.times[-1] + dt
    t5 = a.times[-1] + dt
    assert np.isclose(out.times[5].to_value("unix"), t5.to_value("unix"), atol=1e-5)

    t6 = a.times[-1] + 2*dt
    assert np.isclose(out.times[6].to_value("unix"), t6.to_value("unix"), atol=1e-5)

    t7 = a.times[-1] + 3*dt
    assert np.isclose(out.times[7].to_value("unix"), t7.to_value("unix"), atol=1e-5)

def test_join_many_gap_no_fill():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    b = _mk_spec("2020-01-01T00:00:08", ntime=5, dt_s=1)
    out = GenericSpectrogram.join_many([a, b], maxgap=None, fill_gaps=False)

    # 5 + 5 = 10 cols
    assert out.data.shape[1] == 10
    # Times are discontinuous
    assert out.times[4] == a.times[-1]
    assert out.times[5] == b.times[0]

def test_join_many_maxgap_error():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    b = _mk_spec("2020-01-01T00:00:20", ntime=5, dt_s=1)
    # Gap is ~15s. maxgap=5s should raise.
    with pytest.raises(ValueError, match="Too large gap"):
        GenericSpectrogram.join_many([a, b], maxgap=TimeDelta(5 * u.s))

def test_join_many_overlap():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    # a ends at 04s.
    # b starts at 03s. Overlap of 03s, 04s.
    b = _mk_spec("2020-01-01T00:00:03", ntime=5, dt_s=1)

    out = GenericSpectrogram.join_many([a, b])

    # Result should have a full (0..4s) + b trimmed (starts > 04s => 05s, 06s, 07s)
    # b original times: 03, 04, 05, 06, 07
    # trimmed b: 05, 06, 07 (3 cols)
    # total: 5 + 3 = 8
    assert out.data.shape[1] == 8
    assert len(out.times) == 8

    # Check monotonicity
    # Robust check using unix timestamp values
    assert np.all(np.diff(out.times.to_value("unix")) > 0)

def test_join_many_sort():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    b = _mk_spec("2020-01-01T00:00:05", ntime=5, dt_s=1)

    # Pass in wrong order
    out = GenericSpectrogram.join_many([b, a])

    assert out.times[0] == a.times[0]
    assert out.times[-1] == b.times[-1]
    assert out.data.shape[1] == 10

def test_join_many_subclass():
    class SubSpectrogram(GenericSpectrogram):
        pass

    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1)
    # Manually cast to subclass
    a = SubSpectrogram(a.data, a.meta)

    b = _mk_spec("2020-01-01T00:00:05", ntime=5, dt_s=1)
    b = SubSpectrogram(b.data, b.meta)

    out = SubSpectrogram.join_many([a, b])
    assert isinstance(out, SubSpectrogram)

def test_join_many_mismatch_freq():
    a = _mk_spec("2020-01-01T00:00:00", ntime=5, dt_s=1, nfreq=3)
    b = _mk_spec("2020-01-01T00:00:05", ntime=5, dt_s=1, nfreq=4)
    with pytest.raises(ValueError, match="frequency axes"):
        GenericSpectrogram.join_many([a, b])

    # Same length but different values
    c_base = _mk_spec("2020-01-01T00:00:05", ntime=5, dt_s=1, nfreq=3)
    # Create new instance with different freqs to avoid mutation issues
    new_meta = c_base.meta.copy()
    new_meta["freqs"] = (np.arange(3) + 10) * u.MHz
    c = GenericSpectrogram(c_base.data, new_meta)

    with pytest.raises(ValueError, match="frequency axes"):
        GenericSpectrogram.join_many([a, c])
