import pytest

from sunpy.net import attrs as a

from radiospectra.net.sources.rstn import Observatory, RSTNClient


@pytest.fixture
def client():
    return RSTNClient()


def test_client(client):
    query = client.search(a.Time('2003/03/15 00:00', '2003/03/15 23:59'),
                          a.Instrument('RSTN'))
    assert len(query) == 3


def test_client_observatory(client):
    query = client.search(a.Time('2003/03/15 00:00', '2003/03/15 23:59'),
                          a.Instrument('RSTN'), Observatory('San Vito'))
    assert len(query) == 1
