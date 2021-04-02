from pathlib import Path
from datetime import datetime

import astropy.units as u

from radiospectra import data
from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import EOVSASpectrogram


def test_eovsa_xpall():
    file = Path(data.__file__).parent / 'EOVSA_XPall_20210213.fts'
    spec = Spectrogram(file)
    assert isinstance(spec, EOVSASpectrogram)
    assert spec.observatory == 'OWENS VALLEY'
    assert spec.instrument == 'EOVSA'
    assert spec.detector == 'EOVSA'
    assert spec.start_time.datetime == datetime(2021, 2, 13, 15, 41, 20, 999000)
    assert spec.end_time.datetime == datetime(2021, 2, 13, 20, 43, 18, 999000)
    assert spec.wavelength.min.to(u.GHz) == 1.105371117591858 * u.GHz
    assert spec.wavelength.max.to(u.GHz) == 17.979686737060547 * u.GHz
    assert spec.polarisation == 'I'


def test_eovsa_tpall():
    file = Path(data.__file__).parent / 'EOVSA_TPall_20210213.fts'
    spec = Spectrogram(file)
    assert isinstance(spec, EOVSASpectrogram)
    assert spec.observatory == 'OWENS VALLEY'
    assert spec.instrument == 'EOVSA'
    assert spec.detector == 'EOVSA'
    assert spec.start_time.datetime == datetime(2021, 2, 13, 15, 41, 20, 999000)
    assert spec.end_time.datetime == datetime(2021, 2, 13, 20, 43, 18, 999000)
    assert spec.wavelength.min.to(u.GHz) == 1.105371117591858 * u.GHz
    assert spec.wavelength.max.to(u.GHz) == 17.979686737060547 * u.GHz
    assert spec.polarisation == 'I'
