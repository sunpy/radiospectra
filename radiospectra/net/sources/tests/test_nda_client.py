from pathlib import Path
from unittest import mock

import pytest

from astropy.time import Time

from sunpy.net import attrs as a
from sunpy.net.fido_factory import Fido

from radiospectra.net.sources.nda import NDAClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def nda_html_pages():
    base = Path(__file__).parent / "data"
    with open(base / "nda_page.html") as f:
        return [f.read()]


@mock.patch(MOCK_PATH)
def test_nda_client_search(urlopen, nda_html_pages):
    client = NDAClient()

    urlopen.return_value.read.side_effect = nda_html_pages

    query = client.search(a.Time("2025-03-26", "2025-03-27"), a.Instrument("NDA"))

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
    assert all(query["Version"] == "1")


@pytest.mark.remote_data
def test_nda_fido():
    query = Fido.search(a.Time("2025-03-26", "2025-03-27"), a.Instrument("NDA"))

    assert len(query) >= 1

    result_block = query["nda"]
    assert len(result_block) > 0

    row = result_block[0]

    assert row["Instrument"] == "NDA"
    assert row["Source"] == "NDA"
    assert row["Version"] == "1.1"

    assert row["Start Time"] == Time("2025-03-26 07:56:00.000")
    assert row["End Time"] == Time("2025-03-26 15:55:00")
