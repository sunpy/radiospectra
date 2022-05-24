from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import RFSSpectrogram


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_psp_rfs_lfr(parse_path_moc):
    start_time = Time("2019-04-09 00:01:16.197889")
    end_time = Time("2019-04-10 00:01:04.997573")
    meta = {
        "cdf_meta": {
            "TITLE": "PSP FIELDS RFS LFR data",
            "Project": "PSP",
            "Source_name": "PSP_FLD>Parker Solar Probe FIELDS",
            "Descriptor": "RFS_LFR>Radio Frequency Spectrometer LFR",
            "Data_type": "L2>Level 2 Data",
            "Data_version": "01",
            "MODS": "Revision 1",
            "Logical_file_id": "psp_fld_l2_rfs_lfr_20190409_v01",
            "Mission_group": "PSP",
        },
        "detector": "lfr",
        "instrument": "FIELDS/RFS",
        "observatory": "PSP",
        "start_time": start_time,
        "end_time": end_time,
        "wavelength": a.Wavelength(10.546879882812501 * u.kHz, 1687.5 * u.kHz),
        "times": start_time + np.linspace(0, (end_time - start_time).to_value("s"), 12359) * u.s,
        "freqs": [
            10546.88,
            18750.0,
            28125.0,
            37500.0,
            46875.0,
            56250.0,
            65625.0,
            75000.0,
            84375.0,
            89062.5,
            94921.88,
            100781.25,
            106640.62,
            112500.0,
            118359.38,
            125390.62,
            132421.88,
            140625.0,
            146484.38,
            157031.25,
            166406.25,
            175781.25,
            186328.12,
            196875.0,
            208593.75,
            220312.5,
            233203.12,
            247265.62,
            261328.12,
            276562.5,
            292968.75,
            309375.0,
            328125.0,
            346875.0,
            366796.88,
            387890.62,
            411328.12,
            434765.62,
            459375.0,
            486328.12,
            514453.12,
            544921.9,
            576562.5,
            609375.0,
            645703.1,
            682031.25,
            721875.0,
            764062.5,
            808593.75,
            855468.75,
            904687.5,
            957421.9,
            1013671.9,
            1072265.6,
            1134375.0,
            1196484.4,
            1265625.0,
            1312500.0,
            1368750.0,
            1425000.0,
            1481250.0,
            1565625.0,
            1621875.0,
            1687500.0,
        ]
        * u.Hz,
    }
    array = np.zeros((64, 12359))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.cdf")
    spec = Spectrogram(file)
    assert isinstance(spec, RFSSpectrogram)
    assert spec.observatory == "PSP"
    assert spec.instrument == "FIELDS/RFS"
    assert spec.detector == "LFR"
    # TODO check why not exact prob base on spacecrast ET so won't match utc exacly
    assert spec.start_time.datetime == datetime(2019, 4, 9, 0, 1, 16, 197889)
    assert spec.end_time.datetime == datetime(2019, 4, 10, 0, 1, 4, 997573)
    assert spec.wavelength.min.round(1) == 10.5 * u.kHz
    assert spec.wavelength.max == 1687.5 * u.kHz
    assert spec.level == "L2"
    assert spec.version == 1


@mock.patch("radiospectra.spectrogram2.spectrogram.parse_path")
def test_psp_rfs_hfr(parse_path_moc):
    start_time = Time("2019-04-09 00:01:13.904188")
    end_time = Time("2019-04-10 00:01:02.758315")
    meta = {
        "cdf_meta": {
            "TITLE": "PSP FIELDS RFS HFR data",
            "Project": "PSP",
            "Source_name": "PSP_FLD>Parker Solar Probe FIELDS",
            "Descriptor": "RFS_HFR>Radio Frequency Spectrometer HFR",
            "Data_type": "L2>Level 2 Data",
            "Data_version": "01",
            "MODS": "Revision 1",
            "Logical_file_id": "psp_fld_l2_rfs_lfr_20190409_v01",
            "Mission_group": "PSP",
        },
        "detector": "hfr",
        "instrument": "FIELDS/RFS",
        "observatory": "PSP",
        "start_time": start_time,
        "end_time": end_time,
        "wavelength": a.Wavelength(1275.0 * u.kHz, 19171.876 * u.kHz),
        "times": start_time + np.linspace(0, (end_time - start_time).to_value("s"), 12359) * u.s,
        "freqs": [
            1275000.0,
            1321875.0,
            1378125.0,
            1425000.0,
            1471875.0,
            1575000.0,
            1621875.0,
            1678125.0,
            1771875.0,
            1828125.0,
            1921875.0,
            2025000.0,
            2128125.0,
            2221875.0,
            2278125.0,
            2371875.0,
            2521875.0,
            2625000.0,
            2728125.0,
            2878125.0,
            2971875.0,
            3121875.0,
            3271875.0,
            3375000.0,
            3525000.0,
            3721875.0,
            3871875.0,
            4021875.0,
            4228125.0,
            4425000.0,
            4575000.0,
            4771875.0,
            5025000.0,
            5221875.0,
            5475000.0,
            5728125.0,
            5971875.0,
            6225000.0,
            6478125.0,
            6778125.0,
            7078125.0,
            7425000.0,
            7725000.0,
            8071875.0,
            8428125.0,
            8821875.0,
            9178125.0,
            9571875.0,
            10021875.0,
            10471875.0,
            10921875.0,
            11428125.0,
            11925000.0,
            12421875.0,
            13021875.0,
            13575000.0,
            14175000.0,
            14821875.0,
            15478125.0,
            16125000.0,
            16875000.0,
            17625000.0,
            18375000.0,
            19171876.0,
        ]
        * u.Hz,
    }
    array = np.zeros((64, 12359))
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.cdf")
    spec = Spectrogram(file)
    assert isinstance(spec, RFSSpectrogram)
    assert spec.observatory == "PSP"
    assert spec.instrument == "FIELDS/RFS"
    assert spec.detector == "HFR"
    # TODO check why not exact prob base on spacecrast ET so won't match utc exacly
    assert spec.start_time.datetime == datetime(2019, 4, 9, 0, 1, 13, 904188)
    assert spec.end_time.datetime == datetime(2019, 4, 10, 0, 1, 2, 758315)
    assert spec.wavelength.min == 1275.0 * u.kHz
    assert spec.wavelength.max == 19171.876 * u.kHz
    assert spec.level == "L2"
    assert spec.version == 1
