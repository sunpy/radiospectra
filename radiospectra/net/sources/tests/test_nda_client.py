import pytest
from unittest import mock
from pathlib import Path
import warnings

from astropy.time import Time
from sunpy.net import attrs as a
from sunpy.net.fido_factory import Fido

from radiospectra.net.sources.nda import NDAClient
import erfa


MOCK_PATH = "sunpy.net.scraper.urlopen"


# -------------------------
# FIXTURE: NDA HTML page
# -------------------------
@pytest.fixture
def nda_html_pages():
    base = Path(__file__).parent / "data"
    with open(base / "nda_page.html") as f:
        return [f.read()]


# -------------------------
# CLIENT TEST
# -------------------------
@mock.patch(MOCK_PATH)
def test_nda_client_search(urlopen, nda_html_pages):
    client = NDAClient()

    urlopen.return_value.read.side_effect = nda_html_pages

    query = client.search(
        a.Time("2025-03-26", "2025-03-27"),
        a.Instrument("NDA")
    )

    # scraper called
    assert urlopen.call_count == 1

    # results
    assert len(query) == 2

    row0, row1 = query[0], query[1]

    # ---- first file ----
    assert row0["Start Time"] == Time("2025-03-26T07:56:00")
    assert row0["End Time"] == Time("2025-03-26T15:56:00")

    # ---- second file ----
    assert row1["Start Time"] == Time("2025-03-26T08:00:00")
    assert row1["End Time"] == Time("2025-03-26T16:00:00")

    # metadata
    assert all(query["Instrument"] == "NDA")
    assert all(query["Source"] == "NDA")

    # Version check
    assert all(query["version"] == "1")


# -------------------------
# CLIENT TEST: URL request
# -------------------------
@mock.patch(MOCK_PATH)
def test_nda_client_url_building_and_call(urlopen, nda_html_pages):
    client = NDAClient()

    urlopen.return_value.read.side_effect = nda_html_pages

    client.search(
        a.Time("2025-03-26", "2025-03-27"),
        a.Instrument("NDA")
    )

    assert urlopen.called  


# -------------------------
# CLIENT TEST: post_search_hook (no ERFA crash)
# -------------------------
def test_nda_post_search_hook():
    client = NDAClient()

    fake_exdict = {
        "start_year": "2025",
        "start_month": "03",
        "start_day": "26",
        "start_hour": "07",
        "start_minute": "56",
        "end_year": "2025",
        "end_month": "03",
        "end_day": "26",
        "end_hour": "15",
        "end_minute": "56",
    }

    fake_matchdict = {}

    # silence astropy ERFA warning (this is expected behavior)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", erfa.ErfaWarning)

        row = client.post_search_hook(fake_exdict.copy(), fake_matchdict)

    assert "End Time" in row
    assert isinstance(row["End Time"], Time)


# -------------------------
# INTEGRATION TEST: Fido 
# -------------------------
def test_nda_fido():
    query = Fido.search(
        a.Time("2025-03-26", "2025-03-27"),
        a.Instrument("NDA")
    )

    assert len(query) >= 1

    result_block = query[0]
    assert len(result_block) > 0

    row = result_block[0]

    assert row["Instrument"] == "NDA"
    assert row["Source"] == "NDA"
    assert row["version"] == "1.1"

    assert isinstance(row["Start Time"], Time)
    assert isinstance(row["End Time"], Time)