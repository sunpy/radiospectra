import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time
from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.sources.psp import RFSClient

client = RFSClient()


@pytest.mark.parametrize("req_wave,receivers", [
    # Completely contain the both receiver ranges
    (a.Wavelength(1*u.kHz, 25000*u.kHz), ['rfs_lfr', 'rfs_hfr']),
    # Min in lower freq and max in high freq receiver
    (a.Wavelength(20*u.kHz, 15*u.MHz), ['rfs_lfr', 'rfs_hfr']),
    # Min below and max in low freq receiver
    (a.Wavelength(1*u.kHz, 100*u.kHz), ['rfs_lfr']),
    # Min and max in low freq receiver
    (a.Wavelength(20*u.kHz, 100*u.kHz), ['rfs_lfr']),
    # Min and max in high freq receiver
    (a.Wavelength(1800*u.kHz, 18000*u.kHz), ['rfs_hfr']),
    # Min in high freq receiver and max above
    (a.Wavelength(1800*u.kHz, 20000*u.kHz), ['rfs_hfr']),
    # Min and max in the over lap
    (a.Wavelength(1.4*u.MHz, 1.5*u.MHz), ['rfs_lfr', 'rfs_hfr'])
])
def test_check_wavelength(req_wave, receivers):
    res = RFSClient._check_wavelengths(req_wave)
    assert set(res) == set(receivers)


@pytest.mark.remote_data
def test_fido():
    atr = a.Time('2019/10/01', '2019/10/02')
    res = Fido.search(atr, a.Instrument('rfs'))
    res0 = res.get_response(0)
    isinstance(res0.client, RFSClient)
    assert len(res0) == 4
    tr = res0.time_range()
    assert tr.start.datetime == Time('2019-10-01T00:00').datetime
    assert tr.end.datetime == Time('2019-10-02T23:59:59.999').datetime


@pytest.mark.remote_data
def test_search_with_wavelength():
    tr = a.Time('2019/10/13', '2019/10/15')
    wr1 = a.Wavelength(1*u.kHz, 1.1*u.MHz)
    res1 = client.search(tr, wr1)
    assert np.array_equal(res1.blocks[0]['Wavelength'], [10, 1700] * u.kHz)
    assert len(res1) == 3
    assert res1.time_range().start == Time('2019-10-13T00:00').datetime
    assert res1.time_range().end == Time('2019-10-15T23:59:59.999').datetime
    wr2 = a.Wavelength(2*u.MHz, 20*u.MHz)
    res2 = client.search(tr, wr2)
    assert np.array_equal(res2.blocks[0]['Wavelength'], [1300, 19200] * u.kHz)
    assert len(res2) == 3
    assert res2.time_range().start == Time('2019-10-13T00:00').datetime
    assert res2.time_range().end == Time('2019-10-15T23:59:59.999').datetime


@pytest.mark.remote_data
def test_get_url_for_time_range():
    url_start = 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_lfr/2019/' \
                'psp_fld_l2_rfs_lfr_20191001_v02.cdf'
    url_end = 'https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_hfr/2019/' \
              'psp_fld_l2_rfs_hfr_20191015_v02.cdf'
    tr = a.Time('2019/10/01', '2019/10/15')
    res = client.search(tr)
    urls = [i['url'] for i in res]
    assert urls[0] == url_start
    assert urls[-1] == url_end


def test_can_handle_query():
    atr = a.Time('2019/10/01', '2019/11/01')
    res = client._can_handle_query(atr, a.Instrument('rfs'))
    assert res is True
    res = client._can_handle_query(atr)
    assert res is False


@pytest.mark.remote_data
def test_get():
    query = client.search(a.Time('2019/10/05', '2019/10/10'), a.Instrument('rfr'))
    download_list = client.fetch(query)
    assert len(download_list) == len(query)
