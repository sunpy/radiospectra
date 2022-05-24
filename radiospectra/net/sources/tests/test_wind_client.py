from datetime import datetime
from unittest import mock

import numpy as np
import pytest

import astropy.units as u
from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.sources.wind import WAVESClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return WAVESClient()


@pytest.mark.remote_data
def test_fido():
    atr = a.Time("2010/10/01", "2010/10/02")
    res = Fido.search(atr, a.Instrument("waves"))

    assert isinstance(res[0].client, WAVESClient)
    assert len(res[0]) == 4


# Taken from https://solar-radio.gsfc.nasa.gov/data/wind/rad1/2010/rad1/
http_cont_rad1 = """
      <a href="20100102.R1">20100102.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100103.R1">20100103.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100104.R1">20100104.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100105.R1">20100105.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100106.R1">20100106.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100107.R1">20100107.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100108.R1">20100108.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100109.R1">20100109.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100110.R1">20100110.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100111.R1">20100111.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100112.R1">20100112.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100113.R1">20100113.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100114.R1">20100114.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100115.R1">20100115.R1</a>             11-May-2015 15:32  1.4M
      <a href="20100116.R1">20100116.R1</a>             11-May-2015 15:32  1.4M
"""

# Taken from https://solar-radio.gsfc.nasa.gov/data/wind/rad2/2010/rad2/
http_cont_rad2 = """
      <a href="20100102.R2">20100102.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100103.R2">20100103.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100104.R2">20100104.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100105.R2">20100105.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100106.R2">20100106.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100107.R2">20100107.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100108.R2">20100108.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100109.R2">20100109.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100110.R2">20100110.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100111.R2">20100111.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100112.R2">20100112.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100113.R2">20100113.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100114.R2">20100114.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100115.R2">20100115.R2</a>             11-May-2015 15:36  1.4M
      <a href="20100116.R2">20100116.R2</a>             11-May-2015 15:36  1.4M
"""


@pytest.fixture
def html_responses():
    return [http_cont_rad1, http_cont_rad2]


@mock.patch(MOCK_PATH)
def test_waves_client(mock_urlopen, client, html_responses):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = html_responses
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time("2010/01/02", "2010/01/03")
    query = client.search(atr)

    called_urls = [
        "https://solar-radio.gsfc.nasa.gov/data/wind/rad1/2010/rad1/",
        "https://solar-radio.gsfc.nasa.gov/data/wind/rad2/2010/rad2/",
    ]
    assert called_urls == [call[0][0] for call in mock_urlopen.call_args_list]
    assert len(query) == 4
    assert query[0]["Source"] == "WIND"

    wave = [20, 1040] * u.kHz
    assert np.array_equal(query[0]["Wavelength"], wave)
    assert query[0]["Start Time"].datetime == datetime(2010, 1, 2)
    assert query[0]["End Time"].datetime == datetime(2010, 1, 2, 23, 59, 59, 999000)

    wave = [1075, 13825] * u.kHz
    assert np.array_equal(query[3]["Wavelength"], wave)
    assert query[3]["Start Time"].datetime == datetime(2010, 1, 3)
    assert query[3]["End Time"].datetime == datetime(2010, 1, 3, 23, 59, 59, 999000)


@pytest.mark.parametrize(
    "query_wave, receivers",
    [
        (a.Wavelength(1 * u.GHz, 2 * u.GHz), []),
        (a.Wavelength(1 * u.Hz, 2 * u.Hz), []),
        (a.Wavelength(20 * u.kHz, 150 * u.kHz), ["rad1"]),
        (a.Wavelength(1.5 * u.MHz, 15 * u.MHz), ["rad2"]),
        (a.Wavelength(5 * u.MHz, 10 * u.MHz), ["rad2"]),
        (a.Wavelength(100 * u.Hz, 100 * u.kHz), ["rad1"]),
        (a.Wavelength(20 * u.kHz, 15 * u.MHz), ["rad1", "rad2"]),
        (a.Wavelength(5 * u.kHz, 20 * u.MHz), ["rad1", "rad2"]),
    ],
)
def test_check_wavelength(query_wave, receivers, client):
    assert set(client._check_wavelengths(query_wave)) == set(receivers)
