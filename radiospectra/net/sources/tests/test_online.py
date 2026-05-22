import os

import pytest

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra.net import attrs as ra


@pytest.mark.remote_data
def test_wind_waves_query():
    query = Fido.search(a.Time("2020/01/02", "2020/01/02"), a.Instrument("WAVES"))
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    assert any(f.endswith((".R1", ".R2")) for f in files), f"Expected .R1 or .R2 extension, got {files}"


@pytest.mark.remote_data
def test_ecallisto_query():
    query = Fido.search(
        a.Time("2019/10/05 23:00", "2019/10/05 23:30"), a.Instrument("eCALLISTO"), ra.Observatory("ALASKA")
    )
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    assert any(f.endswith(".fit.gz") for f in files), f"Expected .fit.gz extension, got {files}"


@pytest.mark.remote_data
@pytest.mark.xfail(reason="EOVSA backend now requires authentication, pending upstream Fido support.")
def test_eovsa_query():
    query = Fido.search(a.Time("2020/10/05 00:00", "2020/10/05 00:30"), a.Instrument("EOVSA"), ra.PolType.cross)
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    assert any(f.endswith(".fts") for f in files), f"Expected .fts extension, got {files}"


@pytest.mark.remote_data
def test_ilofar_query():
    query = Fido.search(a.Time("2018/06/01 10:00", "2018/06/01 10:15"), a.Instrument("ILOFAR"))
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    assert any(f.endswith(".dat") for f in files), f"Expected .dat extension, got {files}"


@pytest.mark.remote_data
def test_psp_rfs_query():
    query = Fido.search(a.Time("2019/10/05", "2019/10/05"), a.Instrument("rfs"))
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    assert any(f.endswith(".cdf") for f in files), f"Expected .cdf extension, got {files}"


@pytest.mark.remote_data
def test_rstn_query():
    query = Fido.search(
        a.Time("2003/03/15 00:00", "2003/03/15 01:00"), a.Instrument("RSTN"), ra.Observatory("San Vito")
    )
    assert len(query[0]) > 0
    files = Fido.fetch(query[0][0])
    assert len(files) >= 1
    basename = os.path.basename(files[0])
    assert basename.endswith(".SRS.gz"), f"Expected .SRS.gz extension, got {basename}"
