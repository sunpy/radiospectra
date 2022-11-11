import gzip
from pathlib import Path
from unittest import mock

import pytest

from sunpy.net import attrs as a
from sunpy.net.fido_factory import Fido

from radiospectra.net.sources.ecallisto import Observatory, eCALLISTOClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return eCALLISTOClient()


@pytest.fixture
def http_responses():
    paths = [Path(__file__).parent / "data" / n for n in ["ecallisto_resp1.html.gz", "ecallisto_resp2.html.gz"]]
    response_htmls = []
    for p in paths:
        with gzip.open(p) as f:
            response_htmls.append(f.read())
    return response_htmls


@pytest.fixture
def http_response_alt():
    path = Path(__file__).parent / "data" / "ecallisto_resp_alt_format.html"
    with path.open("r") as file:
        response_html = file.read()
        return response_html


@mock.patch(MOCK_PATH)
def test_client(urlopen, client, http_responses):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = http_responses
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(a.Time("2019/10/05 23:00", "2019/10/06 00:59"), a.Instrument("eCALLISTO"))
    assert urlopen.call_count == 2
    # 2nd call
    urlopen.assert_called_with("http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2019/10/06/")
    assert len(query) == 156


@mock.patch(MOCK_PATH)
def test_client_alt_format(urlopen, client, http_response_alt):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.return_value = http_response_alt
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(
        a.Time("2010/03/27 00:00", "2010/03/27 23:59"), a.Instrument("eCALLISTO"), Observatory("PHOENIX3-B1")
    )
    assert len(query) == 24


@mock.patch(MOCK_PATH)
def test_client_with_observatory(urlopen, client, http_responses):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = http_responses
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(
        a.Time("2019/10/05 23:00", "2019/10/06 00:59"), a.Instrument("eCALLISTO"), Observatory("ALASKA")
    )
    assert urlopen.call_count == 2
    # 2nd call
    urlopen.assert_called_with("http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2019/10/06/")
    assert len(query) == 8


@pytest.mark.remote_data
def test_fido():
    query = Fido.search(
        a.Time("2019/10/05 23:00", "2019/10/06 00:59"), a.Instrument("eCALLISTO"), Observatory("ALASKA")
    )
    assert len(query[0]) == 8
    assert all(query[0]["Observatory"] == "ALASKA")
