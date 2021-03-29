from pathlib import Path
from datetime import datetime

import astropy.units as u

from radiospectra import data
from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import RSTNSpectrogram


def test_psp_rfs_lfr():
    file = Path(data.__file__).parent / 'sv200101.srs'
    spec = Spectrogram(file)
    assert isinstance(spec, RSTNSpectrogram)
    assert spec.observatory == 'SAN VITO'
    assert spec.instrument == 'RSTN'
    assert spec.detector == 'RSTN'
    assert spec.start_time.datetime == datetime(2020, 1, 1, 6, 17, 38)
    assert spec.end_time.datetime == datetime(2020, 1, 1, 15, 27, 43)
    assert spec.wavelength.min == 25000 * u.kHz
    assert spec.wavelength.max == 180000 * u.kHz
