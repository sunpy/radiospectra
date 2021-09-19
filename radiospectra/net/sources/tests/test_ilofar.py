from pathlib import Path
from unittest import mock

import pytest

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net.sources.ilofar import ILOFARClient


@pytest.fixture
def client():
    return ILOFARClient()


@pytest.fixture
def html_responses():
    paths = [Path(__file__).parent / 'data' / n for n in ['ilofar_resp1.html', 'ilofar_resp2.html']]
    response_htmls = []
    for p in paths:
        with p.open('r') as f:
            response_htmls.append(f.read())

    return response_htmls


@mock.patch('sunpy.util.scraper.urlopen')
def test_ilofar_client(mock_urlopen, client, html_responses):
    mock_urlopen.return_value.read = mock.MagicMock()
    mock_urlopen.return_value.read.side_effect = html_responses
    mock_urlopen.close = mock.MagicMock(return_value=None)
    atr = a.Time('2018/06/01', '2018/06/02')
    query = client.search(atr)

    called_urls = ['https://data.lofar.ie/2018/06/01/bst/kbt/rcu357_1beam/',
                   'https://data.lofar.ie/2018/06/02/bst/kbt/rcu357_1beam/']
    assert called_urls == [call[0][0] for call in mock_urlopen.call_args_list]
    assert len(query) == 8
    assert query[0]['Source'] == 'ILOFAR'
    assert query[0]['Provider'] == 'ILOFAR'
    assert query[0]['Start Time'].iso == '2018-06-01 10:00:41.000'
    assert query[0]['Polarisation'] == 'X'


@pytest.mark.remote_data
def test_fido():
    atr = a.Time('2018/06/01', '2018/06/02')
    query = Fido.search(atr, a.Instrument('ILOFAR'))

    assert isinstance(query[0].client, ILOFARClient)
    query = query[0]
    assert len(query) == 8
    assert query[0]['Source'] == 'ILOFAR'
    assert query[0]['Provider'] == 'ILOFAR'
    assert query[0]['Start Time'].iso == '2018-06-01 10:00:41.000'
    assert query[0]['Polarisation'] == 'X'
