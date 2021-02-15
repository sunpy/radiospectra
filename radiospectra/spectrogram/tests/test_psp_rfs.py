from pathlib import Path
from datetime import datetime

import astropy.units as u

from radiospectra import data
from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.spectrogram import RFSSpectrogram


def test_psp_rfs_lfr():
    file = Path(data.__file__).parent / 'psp_fld_l2_rfs_lfr_20190409_v01.cdf'
    spec = Spectrogram(file)
    assert isinstance(spec, RFSSpectrogram)
    assert spec.observatory == 'PSP'
    assert spec.instrument == 'FIELDS/RFS'
    assert spec.detector == 'LFR'
    # TODO check why not exact prob base on spacecrast ET so won't match utc exacly
    assert spec.start_time.datetime == datetime(2019, 4, 9, 0, 1, 16, 197889)
    assert spec.end_time.datetime == datetime(2019, 4, 10, 0, 1, 4, 997573)
    assert spec.wavelength.min.round(1) == 10.5 * u.kHz
    assert spec.wavelength.max == 1687.5 * u.kHz
    assert spec.level == 'L2'
    assert spec.version == 1


def test_psp_rfs_hfr():
    file = Path(data.__file__).parent / 'psp_fld_l2_rfs_hfr_20190409_v01.cdf'
    spec = Spectrogram(file)
    assert isinstance(spec, RFSSpectrogram)
    assert spec.observatory == 'PSP'
    assert spec.instrument == 'FIELDS/RFS'
    assert spec.detector == 'HFR'
    # TODO check why not exact prob base on spacecrast ET so won't match utc exacly
    assert spec.start_time.datetime == datetime(2019, 4, 9, 0, 1, 13, 904188)
    assert spec.end_time.datetime == datetime(2019, 4, 10, 0, 1, 2, 758315)
    assert spec.wavelength.min == 1275.0 * u.kHz
    assert spec.wavelength.max == 19171.876 * u.kHz
    assert spec.level == 'L2'
    assert spec.version == 1
