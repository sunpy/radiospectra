from pathlib import Path
from unittest import mock

import numpy as np
import pytest

import astropy.units as u
from astropy.tests.helper import assert_quantity_allclose

from radiospectra.spectrogram import ILOFARMode357Spectrogram, Spectrogram


@mock.patch("numpy.fromfile")
@mock.patch("sunpy.util.io.is_file")
def test_ilofar(mock_is_file, mock_fromfile):
    mock_fromfile.return_value = np.ones(10117216)
    mock_is_file.return_value = True

    spec = Spectrogram(Path("20180602_063247_bst_00X.dat"))
    assert len(spec) == 3
    assert spec[0].polarisation == "X"
    assert spec[0].start_time.iso == "2018-06-02 06:32:47.000"
    assert spec[0].end_time.iso == "2018-06-02 12:18:18.000"
    assert spec[0].mode == "3"
    assert spec[0].frequencies[0].to_value("MHz") == 10.546875
    assert spec[0].frequencies[-1].to_value("MHz") == 88.28125
    assert spec[1].mode == "5"
    assert spec[1].frequencies[0].to_value("MHz") == 110.546875
    assert spec[1].frequencies[-1].to_value("MHz") == 188.28125
    assert spec[2].mode == "7"
    assert spec[2].frequencies[0].to_value("MHz") == 210.546875
    assert spec[2].frequencies[-1].to_value("MHz") == 244.53125


@pytest.mark.remote_data
def test_ilofar_spectrogram_online():
    spec = Spectrogram("https://data.lofar.ie/2018/06/01/bst/kbt/rcu357_1beam/20180601_100041_bst_00X.dat")
    spec = spec[0]
    assert isinstance(spec, ILOFARMode357Spectrogram)
    assert spec.instrument == "ILOFAR"
    assert spec.times[0].isot == "2018-06-01T10:00:41.000"
    assert spec.times[-1].isot == "2018-06-01T10:26:20.000"
    assert_quantity_allclose(spec.frequencies[0], 10.547 * u.MHz, rtol=1e-3)
    assert_quantity_allclose(spec.frequencies[-1], 88.281 * u.MHz, rtol=1e-3)
    assert spec.data.shape == (200, 1540)
