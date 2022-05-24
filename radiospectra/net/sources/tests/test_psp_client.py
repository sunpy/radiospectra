import gzip
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time
from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.sources.psp import RFSClient

MOCK_PATH = "sunpy.net.scraper.urlopen"


@pytest.fixture
def client():
    return RFSClient()


@pytest.mark.parametrize(
    "req_wave,receivers",
    [
        # Completely contain the both receiver ranges
        (a.Wavelength(1 * u.kHz, 25000 * u.kHz), ["rfs_lfr", "rfs_hfr"]),
        # Min in lower freq and max in high freq receiver
        (a.Wavelength(20 * u.kHz, 15 * u.MHz), ["rfs_lfr", "rfs_hfr"]),
        # Min below and max in low freq receiver
        (a.Wavelength(1 * u.kHz, 100 * u.kHz), ["rfs_lfr"]),
        # Min and max in low freq receiver
        (a.Wavelength(20 * u.kHz, 100 * u.kHz), ["rfs_lfr"]),
        # Min and max in high freq receiver
        (a.Wavelength(1800 * u.kHz, 18000 * u.kHz), ["rfs_hfr"]),
        # Min in high freq receiver and max above
        (a.Wavelength(1800 * u.kHz, 20000 * u.kHz), ["rfs_hfr"]),
        # Min and max in the over lap
        (a.Wavelength(1.4 * u.MHz, 1.5 * u.MHz), ["rfs_lfr", "rfs_hfr"]),
    ],
)
def test_check_wavelength(req_wave, receivers, client):
    res = client._check_wavelengths(req_wave)
    assert set(res) == set(receivers)


@pytest.mark.remote_data
def test_fido():
    atr = a.Time("2019/10/01", "2019/10/02")
    res = Fido.search(atr, a.Instrument("rfs"))
    res0 = res[0]
    isinstance(res0.client, RFSClient)
    assert len(res0) == 4
    assert res["rfs"]["Start Time"].min() == Time("2019-10-01T00:00").datetime
    assert res["rfs"]["End Time"].max() == Time("2019-10-02T23:59:59.999").datetime


@pytest.fixture
def http_responces():
    paths = [Path(__file__).parent / "data" / n for n in ["psp_resp1.html.gz", "psp_resp2.html.gz"]]
    response_htmls = []
    for p in paths:
        with gzip.open(p) as f:
            response_htmls.append(f.read())
    return response_htmls


@mock.patch(MOCK_PATH)
def test_search_with_wavelength(mock_urlopen, client, http_responces):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = http_responces
    mock_urlopen.close = mock.MagicMock(return_value=None)
    tr = a.Time("2019/10/13", "2019/10/15")
    wr1 = a.Wavelength(1 * u.kHz, 1.1 * u.MHz)
    res1 = client.search(tr, wr1)

    mock_urlopen.assert_called_with("https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_lfr/2019/")
    assert np.array_equal(res1[0]["Wavelength"], [10, 1700] * u.kHz)
    assert len(res1) == 3
    assert res1["Start Time"].min().datetime == Time("2019-10-13T00:00").datetime
    assert res1["End Time"].max().datetime == Time("2019-10-15T23:59:59.999").datetime
    wr2 = a.Wavelength(2 * u.MHz, 20 * u.MHz)
    res2 = client.search(tr, wr2)
    mock_urlopen.assert_called_with("https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_hfr/2019/")
    assert np.array_equal(res2[0]["Wavelength"], [1300, 19200] * u.kHz)
    assert len(res2) == 3
    assert res2.time_range().start == Time("2019-10-13T00:00").datetime
    assert res2.time_range().end == Time("2019-10-15T23:59:59.999").datetime


@pytest.mark.remote_data
def test_get_url_for_time_range(client):
    url_start = "https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_lfr/2019/" "psp_fld_l2_rfs_lfr_20191001_v02.cdf"
    url_end = "https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_hfr/2019/" "psp_fld_l2_rfs_hfr_20191015_v02.cdf"
    tr = a.Time("2019/10/01", "2019/10/15")
    res = client.search(tr)
    urls = [i["url"] for i in res]
    assert urls[0] == url_start
    assert urls[-1] == url_end


def test_can_handle_query(client):
    atr = a.Time("2019/10/01", "2019/11/01")
    res = client._can_handle_query(atr, a.Instrument("rfs"))
    assert res is True
    res = client._can_handle_query(atr)
    assert res is False


@pytest.mark.remote_data
def test_download(client):
    query = client.search(a.Time("2019/10/05", "2019/10/06"), a.Instrument("rfs"))
    download_list = client.fetch(query)
    assert len(download_list) == len(query)
