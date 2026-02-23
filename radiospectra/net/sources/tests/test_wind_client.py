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
    atr = a.Time("2020/01/02", "2020/01/03")
    res = Fido.search(atr, a.Instrument("WAVES"))

    assert isinstance(res[0].client, WAVESClient)
    assert len(res[0]) == 4


# Taken from https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad1_idl_binary/2020/
http_cont_rad1 = """
<a href="wind_waves_rad1_20200102.R1">wind_waves_rad1_20200102.R1</a>
<a href="wind_waves_rad1_20200103.R1">wind_waves_rad1_20200103.R1</a>
"""

# Taken from https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad2_idl_binary/2020/
http_cont_rad2 = """
<a href="wind_waves_rad2_20200102.R2">wind_waves_rad2_20200102.R2</a>
<a href="wind_waves_rad2_20200103.R2">wind_waves_rad2_20200103.R2</a>
"""


@pytest.fixture
def html_responses():
    return [http_cont_rad1, http_cont_rad2]


@mock.patch(MOCK_PATH)
def test_waves_client(mock_urlopen, client, html_responses):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = html_responses
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time("2020/01/02", "2020/01/03")
    query = client.search(atr)

    called_urls = [
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad1_idl_binary/2020/",
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad2_idl_binary/2020/",
    ]
    assert called_urls == [call[0][0] for call in mock_urlopen.call_args_list]
    assert len(query) == 4
    assert query[0]["Source"] == "WIND"
    assert query[0]["Provider"] == "SPDF"

    wave = [20, 1040] * u.kHz
    assert np.array_equal(query[0]["Wavelength"], wave)
    assert query[0]["Start Time"].datetime == datetime(2020, 1, 2)
    assert query[0]["End Time"].datetime == datetime(2020, 1, 2, 23, 59, 59, 999000)

    wave = [1075, 13825] * u.kHz
    assert np.array_equal(query[3]["Wavelength"], wave)
    assert query[3]["Start Time"].datetime == datetime(2020, 1, 3)
    assert query[3]["End Time"].datetime == datetime(2020, 1, 3, 23, 59, 59, 999000)

    query_urls = [row["url"] for row in query]
    assert (
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad1_idl_binary/2020/wind_waves_rad1_20200102.R1" in query_urls
    )
    assert (
        "https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad2_idl_binary/2020/wind_waves_rad2_20200103.R2" in query_urls
    )


@pytest.mark.parametrize(
    ("query_wave", "receivers"),
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
