from pathlib import Path
from unittest import mock

import numpy as np
import pytest

from sunpy.net import attrs as a
from sunpy.net.fido_factory import Fido

from radiospectra.net.attrs import PolType
from radiospectra.net.sources.eovsa import EOVSAClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return EOVSAClient()


@pytest.fixture
def http_responses():
    paths = [Path(__file__).parent / "data" / n for n in ["eovsa_resp1.html", "eovsa_resp2.html"]]
    response_htmls = []
    for p in paths:
        with p.open("r") as f:
            response_htmls.append(f.read())

    return response_htmls


@mock.patch(MOCK_PATH)
def test_client(urlopen, client, http_responses):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = http_responses
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(a.Time("2020/10/05 00:00", "2020/10/06 23:00"), a.Instrument("EOVSA"))
    assert urlopen.call_count == 2
    # last call should be for 2020/10/06
    assert urlopen.call_args[0][0] == "http://ovsa.njit.edu/fits/synoptic/2020/10/06/"
    assert len(query) == 4


@mock.patch(MOCK_PATH)
def test_client_observatory(urlopen, client, http_responses):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = http_responses
    urlopen.close = mock.MagicMock(return_value=None)
    query = client.search(a.Time("2020/10/05 00:00", "2020/10/06 00:00"), a.Instrument("EOVSA"), PolType.cross)
    assert urlopen.call_count == 2
    # last call should be for 2020/10/06
    assert urlopen.call_args[0][0] == "http://ovsa.njit.edu/fits/synoptic/2020/10/06/"
    assert len(query) == 2
    assert np.all(query["PolType"] == "Cross")


@pytest.mark.remote_data
def test_fido():
    query = Fido.search(a.Time("2020/10/05 00:00", "2020/10/06 00:00"), a.Instrument("EOVSA"), PolType.cross)
    assert len(query[0]) == 2
    assert np.all(query[0]["PolType"] == "Cross")
