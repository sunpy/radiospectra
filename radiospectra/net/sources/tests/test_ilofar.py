from pathlib import Path
from unittest import mock

import pytest

import astropy.units as u

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.attrs import PolType
from radiospectra.net.sources.ilofar import ILOFARMode357Client


@pytest.fixture
def client():
    return ILOFARMode357Client()


@pytest.fixture
def html_responses():
    paths = [Path(__file__).parent / "data" / n for n in ["ilofar_resp1.html", "ilofar_resp2.html"]]
    response_htmls = []
    for p in paths:
        with p.open("r") as f:
            response_htmls.append(f.read())

    return response_htmls


@mock.patch("sunpy.net.scraper.urlopen")
def test_ilofar_client(mock_urlopen, client, html_responses):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = html_responses * 2
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time("2018/06/01", "2018/06/02")
    query = client.search(atr)

    called_urls = [
        "https://data.lofar.ie/2018/06/01/bst/kbt/rcu357_1beam/",
        "https://data.lofar.ie/2018/06/02/bst/kbt/rcu357_1beam/",
        "https://data.lofar.ie/2018/06/01/bst/kbt/rcu357_1beam_datastream/",
        "https://data.lofar.ie/2018/06/02/bst/kbt/rcu357_1beam_datastream/",
    ]
    assert called_urls == [call[0][0] for call in mock_urlopen.call_args_list]
    assert len(query) == 8
    assert query[0]["Source"] == "ILOFAR"
    assert query[0]["Provider"] == "ILOFAR"
    assert query[0]["Start Time"].iso == "2018-06-01 10:00:41.000"
    assert query[0]["Polarisation"] == "X"


@mock.patch("sunpy.net.scraper.urlopen")
def test_ilofar_client_polarisation(mock_urlopen, client, html_responses):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = html_responses * 2
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time("2018/06/01", "2018/06/02")
    query_x = client.search(atr, PolType("X"))
    assert len(query_x) == 4
    assert query_x[0]["Source"] == "ILOFAR"
    assert query_x[0]["Provider"] == "ILOFAR"
    assert query_x[0]["Start Time"].iso == "2018-06-01 10:00:41.000"
    assert query_x[0]["Polarisation"] == "X"


@mock.patch("sunpy.net.scraper.urlopen")
def test_ilofar_client_wavelength(mock_urlopen, client, html_responses):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = html_responses * 6
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time("2018/06/01", "2018/06/02")
    query_both_low = client.search(atr, a.Wavelength(1 * u.MHz, 5 * u.MHz))
    query_both_high = client.search(atr, a.Wavelength(1 * u.GHz, 2 * u.GHz))

    assert len(query_both_low) == 0
    assert len(query_both_high) == 0

    query_low_in = client.search(atr, a.Wavelength(90 * u.MHz, 1 * u.GHz))
    query_both_in = client.search(atr, a.Wavelength(15 * u.MHz, 230 * u.MHz))
    query_high_in = client.search(atr, a.Wavelength(5 * u.MHz, 90 * u.MHz))

    for query in [query_low_in, query_both_in, query_high_in]:
        assert len(query) == 8


@pytest.mark.remote_data
def test_fido():
    atr = a.Time("2018/06/01", "2018/06/02")
    query = Fido.search(atr, a.Instrument("ILOFAR"))

    assert isinstance(query[0].client, ILOFARMode357Client)
    query = query[0]
    assert len(query) == 8
    assert query[0]["Source"] == "ILOFAR"
    assert query[0]["Provider"] == "ILOFAR"
    assert query[0]["Start Time"].iso == "2018-06-01 10:00:41.000"
    assert query[0]["Polarisation"] == "X"


@pytest.mark.remote_data
def test_fido_other_dataset():
    atr = a.Time("2021/08/01", "2021/10/01")
    query = Fido.search(atr, a.Instrument("ILOFAR"))

    assert isinstance(query[0].client, ILOFARMode357Client)
    query = query[0]
    assert len(query) == 38
