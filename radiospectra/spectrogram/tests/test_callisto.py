from pathlib import Path
from datetime import datetime

import astropy.units as u

from radiospectra import data
from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.sources import CALISTOSpectrogram


def test_callisto():
    file = Path(data.__file__).parent / 'BIR_20110607_062400_10.fit'
    spec = Spectrogram(file)
    assert isinstance(spec, CALISTOSpectrogram)
    assert spec.observatory == 'BIR'
    assert spec.instrument == 'E-CALLISTO'
    assert spec.detector == 'E-CALLISTO'
    assert spec.start_time.datetime == datetime(2011, 6, 7, 6, 24, 0, 213000)
    assert spec.end_time.datetime == datetime(2011, 6, 7, 6, 39)
    assert spec.wavelength.min.to(u.MHz) == 20 * u.MHz
    assert spec.wavelength.max.to(u.MHz).round(1) == 91.8 * u.MHz
    assert str(spec.observatory_location) == '(3801942.21260148, 528924.60367802, 5077174.56861812) m'
