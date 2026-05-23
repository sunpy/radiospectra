import parfive
import pytest

from radiospectra.spectrogram import Spectrogram

KNOWN_URLS = {
    "waves": ("https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad1_idl_binary/2020/wind_waves_rad1_20200102.R1"),
    "ecallisto": (
        "http://soleil80.cs.technik.fhnw.ch/solarradio/data/"
        "2002-20yy_Callisto/2019/10/05/ALASKA-COHOE_20191005_230000_00.fit.gz"
    ),
    "ilofar": ("https://data.lofar.ie/2018/06/01/bst/kbt/rcu357_1beam/20180601_100041_bst_00X.dat"),
    "psp_rfs": ("https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/rfs_lfr/2019/psp_fld_l2_rfs_lfr_20191005_v03.cdf"),
    "rstn": (
        "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/"
        "solar-features/solar-radio/rstn-spectral/san-vito/2003/03/"
        "SV030315.SRS.gz"
    ),
}


def download_and_parse_spectrogram(url, tmp_path):
    dl = parfive.Downloader()
    dl.enqueue_file(url, path=tmp_path)
    res = dl.download()
    if not res:
        raise RuntimeError(f"Failed to download {url}")
    return Spectrogram(res[0])


@pytest.mark.remote_data
def test_waves_spectrogram(tmp_path):
    spec = download_and_parse_spectrogram(KNOWN_URLS["waves"], tmp_path)
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "WAVES"


@pytest.mark.remote_data
def test_ecallisto_spectrogram(tmp_path):
    spec = download_and_parse_spectrogram(KNOWN_URLS["ecallisto"], tmp_path)
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "E-CALLISTO"


@pytest.mark.remote_data
@pytest.mark.xfail(reason="EOVSA backend now requires authentication, pending upstream Fido support.")
def test_eovsa_spectrogram(tmp_path):
    url = "https://ovsa.njit.edu/fits/synoptic/2020/10/05/EOVSA_XPall_20201005.fts"
    spec = download_and_parse_spectrogram(url, tmp_path)
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "EOVSA"


@pytest.mark.remote_data
def test_ilofar_spectrogram(tmp_path):
    spec = download_and_parse_spectrogram(KNOWN_URLS["ilofar"], tmp_path)
    if isinstance(spec, list):
        spec = spec[0]
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "ILOFAR"


@pytest.mark.remote_data
def test_psp_rfs_spectrogram(tmp_path):
    spec = download_and_parse_spectrogram(KNOWN_URLS["psp_rfs"], tmp_path)
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "FIELDS/RFS"


@pytest.mark.remote_data
def test_rstn_spectrogram(tmp_path):
    spec = download_and_parse_spectrogram(KNOWN_URLS["rstn"], tmp_path)
    assert spec.times is not None
    assert spec.frequencies is not None
    assert spec.data.size > 0
    assert spec.instrument == "RSTN"
