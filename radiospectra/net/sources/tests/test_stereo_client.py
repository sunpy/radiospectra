from datetime import datetime
from unittest import mock

import numpy as np
import pytest

import astropy.units as u
from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.attrs import Spacecraft
from radiospectra.net.sources.stereo import SWAVESClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return SWAVESClient()


@pytest.mark.remote_data
def test_fido():
    atr = a.Time("2010/10/01", "2010/10/02")
    res = Fido.search(atr, a.Instrument("swaves"))

    assert isinstance(res[1].client, SWAVESClient)
    assert len(res[1]) == 8


http_cont = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
 <html>
 <head>
   <title>Index of /data/stereo/summary/2010</title>
 </head>
 <body>
   <h1>Index of /data/stereo/summary/2010</h1>
<pre><a href="?C=N;O=D">Name</a><a href="?C=M;O=A">Last modified</a><a href="?C=S;O=A">Size</a><hr>
<a href="swaves_average_20100101_a.sav">
swaves_average_20100101_a.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100101_a_hfr.dat">
swaves_average_20100101_a_hfr.dat</a> 13-Jul-2010 20:51  3.5M
<a href="swaves_average_20100101_a_lfr.dat">
swaves_average_20100101_a_lfr.dat</a> 13-Jul-2010 20:51  548K
<a href="swaves_average_20100101_b.sav">
swaves_average_20100101_b.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100101_b_hfr.dat">
swaves_average_20100101_b_hfr.dat</a> 13-Jul-2010 20:51  3.5M
<a href="swaves_average_20100101_b_lfr.dat">
swaves_average_20100101_b_lfr.dat</a> 13-Jul-2010 20:51  548K
<a href="swaves_average_20100102_a.sav">
swaves_average_20100102_a.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100102_a_hfr.dat">
swaves_average_20100102_a_hfr.dat</a> 13-Jul-2010 20:51  3.5M
<a href="swaves_average_20100102_a_lfr.dat">
swaves_average_20100102_a_lfr.dat</a> 13-Jul-2010 20:51  548K
<a href="swaves_average_20100102_b.sav">
swaves_average_20100102_b.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100102_b_hfr.dat">
swaves_average_20100102_b_hfr.dat</a> 13-Jul-2010 20:51  3.5M
<a href="swaves_average_20100102_b_lfr.dat">
swaves_average_20100102_b_lfr.dat</a> 13-Jul-2010 20:51  548K
<a href="swaves_average_20100103_a.sav">
swaves_average_20100103_a.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100103_a_hfr.dat">
swaves_average_20100103_a_hfr.dat</a> 13-Jul-2010 20:51  3.5M
<a href="swaves_average_20100103_a_lfr.dat">
swaves_average_20100103_a_lfr.dat</a> 13-Jul-2010 20:51  548K
<a href="swaves_average_20100103_b.sav">
swaves_average_20100103_b.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100103_b_hfr.dat">
swaves_average_20100103_b_hfr.dat</a> 13-Jul-2010 20:51  3.5M
<a href="swaves_average_20100103_b_lfr.dat">
swaves_average_20100103_b_lfr.dat</a> 13-Jul-2010 20:51  548K
<a href="swaves_average_20100104_a.sav">
swaves_average_20100104_a.sav</a>     13-Jul-2010 20:51  2.0M
<a href="swaves_average_20100104_a_hfr.dat">
swaves_average_20100104_a_hfr.dat</a> 13-Jul-2010 20:52  3.5M
<a href="swaves_average_20100104_a_lfr.dat">
swaves_average_20100104_a_lfr.dat</a> 13-Jul-2010 20:52  548K
<a href="swaves_average_20100104_b.sav">
swaves_average_20100104_b.sav</a>     13-Jul-2010 20:52  2.0M
<a href="swaves_average_20100104_b_hfr.dat">
swaves_average_20100104_b_hfr.dat</a> 13-Jul-2010 20:52  3.5M
<a href="swaves_average_20100104_b_lfr.dat">
swaves_average_20100104_b_lfr.dat</a> 13-Jul-2010 20:52  548K
</pre>
</body>"""


@mock.patch(MOCK_PATH)
def test_swaves_client(mock_urlopen, client):
    mock_urlopen.return_value.read = mock.MagicMock(return_value=http_cont)
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time("2010/01/02", "2010/01/03")
    query = client.search(atr, a.Instrument("swaves"), Spacecraft("a"))
    mock_urlopen.assert_called_with("https://solar-radio.gsfc.nasa.gov/data/stereo/summary/2010/")
    assert len(query) == 8
    assert query[0]["Source"] == "STEREO"
    assert query[0]["Spacecraft"] == "a"
    assert np.array_equal(query[0]["Wavelength"], [10, 160] * u.kHz)
    assert query[0]["Start Time"].datetime == datetime(2010, 1, 2)
    assert query[0]["End Time"].datetime == datetime(2010, 1, 2, 23, 59, 59, 999000)
    assert query[7]["Source"] == "STEREO"
    assert query[7]["Spacecraft"] == "b"
    assert np.array_equal(query[7]["Wavelength"], [125, 16000] * u.kHz)
    assert query[7]["Start Time"].datetime == datetime(2010, 1, 3)
    assert query[7]["End Time"].datetime == datetime(2010, 1, 3, 23, 59, 59, 999000)


@pytest.mark.parametrize(
    "query_wave, receivers",
    [
        (a.Wavelength(1 * u.GHz, 2 * u.GHz), []),
        (a.Wavelength(1 * u.Hz, 2 * u.Hz), []),
        (a.Wavelength(20 * u.kHz, 150 * u.kHz), ["lfr"]),
        (a.Wavelength(0.13 * u.MHz, 15 * u.MHz), ["hfr"]),
        (a.Wavelength(10 * u.MHz, 200 * u.MHz), ["hfr"]),
        (a.Wavelength(100 * u.Hz, 100 * u.kHz), ["lfr"]),
        (a.Wavelength(20 * u.kHz, 15 * u.MHz), ["lfr", "hfr"]),
        (a.Wavelength(5 * u.kHz, 20 * u.MHz), ["lfr", "hfr"]),
    ],
)
def test_check_wavelength(query_wave, receivers, client):
    assert set(client._check_wavelengths(query_wave)) == set(receivers)
