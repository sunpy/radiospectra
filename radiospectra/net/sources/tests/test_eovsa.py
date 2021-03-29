import numpy as np
import pytest

from sunpy.net import attrs as a

from radiospectra.net.sources.eovsa import EOVSAClient, PolType


@pytest.fixture
def client():
    return EOVSAClient()


def test_client(client):
    query = client.search(a.Time('2020/10/05 00:00', '2020/10/06 00:00'),
                          a.Instrument('EOVSA'))
    assert len(query) == 4


def test_client_observatory(client):
    query = client.search(a.Time('2020/10/05 00:00', '2020/10/06 00:00'),
                          a.Instrument('EOVSA'), PolType.cross)
    assert len(query) == 2
    assert np.all(query['PolType'] == 'Cross')
