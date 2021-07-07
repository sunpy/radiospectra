from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import RFSSpectrogram


@mock.patch('radiospectra.spectrogram2.spectrogram.parse_path')
def test_psp_rfs_lfr(parse_path_moc):
    start_time = Time('2019-04-09 00:01:16.197889')
    end_time = Time('2019-04-10 00:01:04.997573')
    meta = {
        'cdf_meta': {
            'TITLE': 'PSP FIELDS RFS LFR data',
            'Project': 'PSP',
            'Source_name': 'PSP_FLD>Parker Solar Probe FIELDS',
            'Descriptor': 'RFS_LFR>Radio Frequency Spectrometer LFR',
            'Data_type': 'L2>Level 2 Data',
            'Data_version': '01',
            'MODS': 'Revision 1',
            'Logical_file_id': 'psp_fld_l2_rfs_lfr_20190409_v01',
            'Mission_group': 'PSP'},
        'detector': 'lfr',
        'instrument': 'FIELDS/RFS',
        'observatory': 'PSP',
        'start_time': start_time,
        'end_time': end_time,
        'wavelength': a.Wavelength(10.546879882812501 * u.kHz, 1687.5 * u.kHz),
        'times': start_time + np.linspace(0, (end_time - start_time).to_value('s'), 12359) * u.s,
        'freqs': [10546.88, 18750., 28125., 37500., 46875., 56250., 65625., 75000., 84375., 89062.5,
                  94921.88, 100781.25, 106640.62, 112500., 118359.38, 125390.62, 132421.88, 140625.,
                  146484.38, 157031.25, 166406.25, 175781.25, 186328.12, 196875., 208593.75,
                  220312.5, 233203.12, 247265.62, 261328.12, 276562.5, 292968.75, 309375., 328125.,
                  346875., 366796.88, 387890.62, 411328.12, 434765.62, 459375., 486328.12,
                  514453.12, 544921.9, 576562.5, 609375., 645703.1, 682031.25, 721875., 764062.5,
                  808593.75, 855468.75, 904687.5, 957421.9, 1013671.9, 1072265.6, 1134375.,
                  1196484.4, 1265625., 1312500., 1368750., 1425000., 1481250., 1565625., 1621875.,
                  1687500.] * u.Hz
    }
    array = np.zeros((64, 12359))
    parse_path_moc.return_value = [(array, meta)]
    file = Path('fake.cdf')
    spec = Spectrogram(file)
    assert isinstance(spec, RFSSpectrogram)
    assert spec.observatory == 'PSP'
    assert spec.instrument == 'FIELDS/RFS'
    assert spec.detector == 'LFR'
    # TODO check why not exact prob base on spacecrast ET so won't match utc exacly
    assert spec.start_time.datetime == datetime(2019, 4, 9, 0, 1, 16, 197889)
    assert spec.end_time.datetime == datetime(2019, 4, 10, 0, 1, 4, 997573)
    assert spec.wavelength.min.round(1) == 10.5 * u.kHz
    assert spec.wavelength.max == 1687.5 * u.kHz
    assert spec.level == 'L2'
    assert spec.version == 1


@mock.patch('radiospectra.spectrogram2.spectrogram.parse_path')
def test_psp_rfs_hfr(parse_path_moc):
    start_time = Time('2019-04-09 00:01:13.904188')
    end_time = Time('2019-04-10 00:01:02.758315')
    meta = {
        'cdf_meta': {
            'TITLE': 'PSP FIELDS RFS HFR data',
            'Project': 'PSP',
            'Source_name': 'PSP_FLD>Parker Solar Probe FIELDS',
            'Descriptor': 'RFS_HFR>Radio Frequency Spectrometer HFR',
            'Data_type': 'L2>Level 2 Data',
            'Data_version': '01',
            'MODS': 'Revision 1',
            'Logical_file_id': 'psp_fld_l2_rfs_lfr_20190409_v01',
            'Mission_group': 'PSP'},
        'detector': 'hfr',
        'instrument': 'FIELDS/RFS',
        'observatory': 'PSP',
        'start_time': start_time,
        'end_time': end_time,
        'wavelength': a.Wavelength(1275.0*u.kHz, 19171.876*u.kHz),
        'times': start_time + np.linspace(0, (end_time - start_time).to_value('s'), 12359) * u.s,
        'freqs': [1275000., 1321875., 1378125., 1425000., 1471875., 1575000., 1621875., 1678125.,
                  1771875., 1828125., 1921875., 2025000., 2128125., 2221875., 2278125., 2371875.,
                  2521875., 2625000., 2728125., 2878125., 2971875., 3121875., 3271875., 3375000.,
                  3525000., 3721875., 3871875., 4021875., 4228125., 4425000., 4575000., 4771875.,
                  5025000., 5221875., 5475000., 5728125., 5971875., 6225000., 6478125., 6778125.,
                  7078125., 7425000., 7725000., 8071875., 8428125., 8821875., 9178125., 9571875.,
                  10021875., 10471875., 10921875., 11428125., 11925000., 12421875., 13021875.,
                  13575000., 14175000., 14821875., 15478125., 16125000., 16875000., 17625000.,
                  18375000., 19171876.] * u.Hz
    }
    array = np.zeros((64, 12359))
    parse_path_moc.return_value = [(array, meta)]
    file = Path('fake.cdf')
    spec = Spectrogram(file)
    assert isinstance(spec, RFSSpectrogram)
    assert spec.observatory == 'PSP'
    assert spec.instrument == 'FIELDS/RFS'
    assert spec.detector == 'HFR'
    # TODO check why not exact prob base on spacecrast ET so won't match utc exacly
    assert spec.start_time.datetime == datetime(2019, 4, 9, 0, 1, 13, 904188)
    assert spec.end_time.datetime == datetime(2019, 4, 10, 0, 1, 2, 758315)
    assert spec.wavelength.min == 1275.0 * u.kHz
    assert spec.wavelength.max == 19171.876 * u.kHz
    assert spec.level == 'L2'
    assert spec.version == 1
