from pathlib import Path
from unittest import mock

import pytest

from sunpy.net import attrs as a
from sunpy.net.fido_factory import Fido

from radiospectra.net.attrs import Observatory
from radiospectra.net.sources.rstn import RSTNClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return RSTNClient()


@pytest.fixture
def http_responses():
    paths = [
        Path(__file__).parent / "data" / n for n in ["rstn_holloman.html", "rstn_learmonth.html", "rstn_san-vito.html"]
    ]
    response_htmls = []
    for p in paths:
        with p.open("r") as f:
            response_htmls.append(f.read())

    # For the chosen test dates there was no data form  Palehua or Sagamore so insert two empty
    # responses in there place
    response_htmls = response_htmls[:2] + ["", ""] + [response_htmls[-1]]
    return response_htmls


@mock.patch(MOCK_PATH)
def test_client(urlopen, client, http_responses):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = http_responses
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(a.Time("2003/03/15 00:00", "2003/03/15 23:59"), a.Instrument("RSTN"))
    assert urlopen.call_count == 5
    # last call arg should be san-vito url
    assert (
        urlopen.call_args[0][0] == "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/"
        "solar-features/solar-radio/rstn-spectral/san-vito/2003/03/"
    )
    assert len(query) == 3


@mock.patch(MOCK_PATH)
def test_client_observatory(urlopen, client, http_responses):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = http_responses[-1:]
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(a.Time("2003/03/15 00:00", "2003/03/15 23:59"), a.Instrument("RSTN"), Observatory("San Vito"))
    urlopen.assert_called_once_with(
        "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/"
        "solar-features/solar-radio/rstn-spectral/san-vito/2003/03/"
    )
    assert len(query) == 1
    assert query["Observatory"] == "San Vito"


@pytest.mark.remote_data
def test_fido():
    query = Fido.search(a.Time("2003/03/15 00:00", "2003/03/15 23:59"), a.Instrument("RSTN"), Observatory("San Vito"))
    assert len(query[0]) == 1
    assert all(query[0]["Observatory"] == "San Vito")
