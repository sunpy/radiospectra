from pathlib import Path
from unittest import mock

import pytest

from astropy.time import Time

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.attrs import Observatory
from radiospectra.net.sources.learmonth import ASWSClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return ASWSClient()


@pytest.fixture
def learmonth_html_page():
    p = Path(__file__).parent / "data" / "learmonth_page.html"
    with p.open() as f:
        return [f.read()]


@mock.patch(MOCK_PATH)
def test_learmonth_client_search(urlopen, client, learmonth_html_page):
    urlopen.return_value.read = mock.MagicMock()
    urlopen.return_value.read.side_effect = learmonth_html_page
    urlopen.close = mock.MagicMock(return_value=None)

    query = client.search(
        a.Time("2017/09/06 00:00", "2017/09/06 23:59"),
        a.Instrument("RSTN"),
        Observatory("Learmonth"),
    )

    assert urlopen.call_count == 1
    assert len(query) == 1

    row = query[0]
    assert row["Instrument"] == "RSTN"
    assert row["Provider"] == "SWS"
    assert row["Observatory"] == "Learmonth"
    assert row["Start Time"] == Time("2017-09-06T00:00:00.000")
    assert row["End Time"] == Time("2017-09-06T23:59:59.999")


@pytest.mark.remote_data
def test_learmonth_fido_provider():
    query = Fido.search(
        a.Time("2017/09/06 00:00", "2017/09/06 23:59"),
        a.Instrument("RSTN"),
        Observatory("Learmonth"),
        a.Provider("ASWS"),
    )

    # Pinning Provider='SWS' should exclude RSTNClient (Provider='RSTN').
    all_providers = {row["Provider"] for block in query for row in block}
    assert all_providers == {"ASWS"}

    block = query["learmonth"]
    row = block[0]
    assert row["Instrument"] == "RSTN"
    assert row["Provider"] == "ASWS"
    assert row["Observatory"] == "Learmonth"
    assert row["Start Time"] == Time("2017-09-06T00:00:00.000")
    assert row["End Time"] == Time("2017-09-06T23:59:59.999")


@pytest.mark.remote_data
def test_learmonth_fido_both_archives():
    """Fido query without ``Provider``: should provide to both
    ``LearmonthClient`` (SWS) and ``RSTNClient`` (NOAA RSTN) for a
    pre-2019 date where both archives hold the file.
    """
    query = Fido.search(
        a.Time("2017/09/06 00:00", "2017/09/06 23:59"),
        a.Instrument("RSTN"),
        Observatory("Learmonth"),
    )
    providers = {row["Provider"] for block in query for row in block}
    assert {"ASWS", "RSTN"}.issubset(providers)
