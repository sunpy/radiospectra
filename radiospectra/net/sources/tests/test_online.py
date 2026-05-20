import pytest

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net import attrs as ra
from radiospectra.spectrogram import Spectrogram


@pytest.mark.remote_data
def test_wind_waves_online():
    query = Fido.search(a.Time("2020/01/02", "2020/01/02"), a.Instrument("WAVES"))
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    spec = Spectrogram(files[0])
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "WAVES"


@pytest.mark.remote_data
def test_ecallisto_online():
    query = Fido.search(
        a.Time("2019/10/05 23:00", "2019/10/05 23:30"), a.Instrument("eCALLISTO"), ra.Observatory("ALASKA")
    )
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    spec = Spectrogram(files[0])
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "E-CALLISTO"


@pytest.mark.remote_data
@pytest.mark.xfail(reason="EOVSA backend now requires authentication, pending upstream Fido support.")
def test_eovsa_online():
    query = Fido.search(a.Time("2020/10/05 00:00", "2020/10/05 00:30"), a.Instrument("EOVSA"), ra.PolType.cross)
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    spec = Spectrogram(files[0])
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "EOVSA"


@pytest.mark.remote_data
def test_ilofar_online():
    query = Fido.search(a.Time("2018/06/01 10:00", "2018/06/01 10:15"), a.Instrument("ILOFAR"))
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    spec = Spectrogram(files[0])
    if isinstance(spec, list):
        spec = spec[0]
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "ILOFAR"


@pytest.mark.remote_data
def test_psp_rfs_online():
    query = Fido.search(a.Time("2019/10/05", "2019/10/05"), a.Instrument("rfs"))
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    spec = Spectrogram(files[0])
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "FIELDS/RFS"


@pytest.mark.remote_data
def test_rstn_online():
    query = Fido.search(
        a.Time("2003/03/15 00:00", "2003/03/15 01:00"), a.Instrument("RSTN"), ra.Observatory("San Vito")
    )
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    spec = Spectrogram(files[0])
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "RSTN"
