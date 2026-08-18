from pathlib import Path
from datetime import datetime
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
import pytest

import astropy.units as u

from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.sources import WAVESSpectrogram
from radiospectra.spectrogram.sources.waves import WAVESMeta
from radiospectra.spectrogram.spectrogram_factory import SpectrogramFactory
from radiospectra.tests.helpers import figure_test


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_waves_rad1(parse_path_moc):
    header = {"instrument": "waves", "file_type": "idl_sav", "file_path": Path("wind_waves_rad1_20201128.R1")}
    array = np.zeros((256, 1441))
    raw_object = {"arrayb": array}
    parse_path_moc.return_value = [(header, raw_object)]
    file = Path("fake.r1")
    spec = Spectrogram(file)
    assert isinstance(spec, WAVESSpectrogram)
    assert spec.observatory == "WIND"
    assert spec.instrument == "WAVES"
    assert spec.detector == "RAD1"
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59, 59)
    assert spec.wavelength.min == 20.0 * u.kHz
    assert spec.wavelength.max == 1040.0 * u.kHz


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_waves_rad2(parse_path_moc):
    header = {"instrument": "waves", "file_type": "idl_sav", "file_path": Path("wind_waves_rad2_20201128.R2")}
    array = np.zeros((256, 1441))
    raw_object = {"arrayb": array}
    parse_path_moc.return_value = [(header, raw_object)]
    file = Path("fake.dat")
    spec = Spectrogram(file)
    assert isinstance(spec, WAVESSpectrogram)
    assert spec.observatory == "WIND"
    assert spec.instrument == "WAVES"
    assert spec.detector == "RAD2"
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59, 59)
    assert spec.wavelength.min == 1.075 * u.MHz
    assert spec.wavelength.max == 13.825 * u.MHz


@mock.patch("radiospectra.spectrogram.spectrogram_factory.readsav")
def test_waves_prefixed_filename_parses_date(readsav_mock):
    data_array = np.zeros((256, 1441))
    readsav_mock.return_value = {"arrayb": data_array}

    header, raw_object = SpectrogramFactory._read_idl_sav(Path("wind_waves_rad1_20200711.R1"), instrument="waves")
    spec = WAVESSpectrogram.from_raw(header, raw_object)

    assert spec.start_time.isot == "2020-07-11T00:00:00.000"


@pytest.mark.remote_data
def test_waves_spectrogram_online():
    spec = Spectrogram(
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad1_idl_binary/2020/wind_waves_rad1_20200102.R1"
    )
    assert spec.instrument == "WAVES"
    assert spec.times[0].isot == "2020-01-02T00:00:30.000"
    assert spec.times[-1].isot == "2020-01-02T23:59:30.000"
    assert spec.frequencies[0] == 20.0 * u.kHz
    assert spec.frequencies[-1] == 1040.0 * u.kHz
    assert spec.data.shape == (256, 1440)


def test_waves_meta():
    meta = WAVESMeta(
        {
            "instrument": "WAVES",
            "background": "test_bg",
            "detector": "rad1",
        }
    )
    assert meta.instrument == "WAVES"
    assert meta.background == "test_bg"
    assert meta.receiver == "rad1"


@pytest.mark.remote_data
@figure_test
def test_waves_rad1_plot():
    spec = Spectrogram(
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad1_idl_binary/2020/wind_waves_rad1_20200102.R1"
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    spec.plot(axes=ax)
    return fig


@pytest.mark.remote_data
@figure_test
def test_waves_rad2_plot():
    spec = Spectrogram(
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad2_idl_binary/2020/wind_waves_rad2_20200102.R2"
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    spec.plot(axes=ax)
    return fig
