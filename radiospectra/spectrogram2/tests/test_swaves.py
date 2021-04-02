from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram2 import Spectrogram
from radiospectra.spectrogram2.sources import SWAVESSpectrogram


@mock.patch('radiospectra.spectrogram2.spectrogram.SpectrogramFactory._read_dat')
def test_swaves_lfr(read_dat):
    meta = {
        'instrument': 'swaves',
        'observatory': 'STEREO A',
        'product': 'average',
        'start_time': Time('2020-11-28 00:00:00'),
        'end_time': Time('2020-11-28 23:59:00'),
        'wavelength': a.Wavelength(2.6 * u.kHz, 153.4 * u.kHz),
        'detector': 'lfr',
        'freqs': [2.6, 2.8, 3.1, 3.4, 3.7, 4., 4.4, 4.8, 5.2, 5.7, 6.2, 6.8, 7.4, 8.1, 8.8, 9.6,
                  10.4, 11.4, 12.4, 13.6, 14.8, 16.1, 17.6, 19.2, 20.9, 22.8, 24.9, 27.1, 29.6,
                  32.2, 35.2, 38.3, 41.8, 45.6, 49.7, 54.2, 59.1, 64.5, 70.3, 76.7, 83.6, 91.2,
                  99.4, 108.4, 118.3, 129., 140.6, 153.4] * u.kHz,
        'times': np.arange(1440) * u.min
    }
    array = np.zeros((48, 1440))
    read_dat.return_value = (meta, array)
    file = Path('fake.dat')
    spec = Spectrogram(file)
    assert isinstance(spec, SWAVESSpectrogram)
    assert spec.observatory == 'STEREO A'
    assert spec.instrument == 'SWAVES'
    assert spec.detector == 'LFR'
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 2.6 * u.kHz
    assert spec.wavelength.max == 153.4 * u.kHz


@mock.patch('radiospectra.spectrogram2.spectrogram.SpectrogramFactory._read_dat')
def test_swaves_hfr(read_dat):
    meta = {
        'instrument': 'swaves',
        'observatory': 'STEREO A',
        'product': 'average',
        'start_time': Time('2020-11-28 00:00:00'),
        'end_time': Time('2020-11-28 23:59:00'),
        'wavelength': a.Wavelength(125.0 * u.kHz, 16025.0 * u.kHz),
        'detector': 'hfr',
        'freqs': [125., 175., 225., 275., 325., 375., 425., 475., 525., 575., 625.,
                  675., 725., 775., 825., 875., 925., 975., 1025., 1075., 1125., 1175.,
                  1225., 1275., 1325., 1375., 1425., 1475., 1525., 1575., 1625., 1675.,
                  1725., 1775., 1825., 1875., 1925., 1975., 2025., 2075., 2125., 2175.,
                  2225., 2275., 2325., 2375., 2425., 2475., 2525., 2575., 2625., 2675.,
                  2725., 2775., 2825., 2875., 2925., 2975., 3025., 3075., 3125., 3175.,
                  3225., 3275., 3325., 3375., 3425., 3475., 3525., 3575., 3625., 3675.,
                  3725., 3775., 3825., 3875., 3925., 3975., 4025., 4075., 4125., 4175.,
                  4225., 4275., 4325., 4375., 4425., 4475., 4525., 4575., 4625., 4675.,
                  4725., 4775., 4825., 4875., 4925., 4975., 5025., 5075., 5125., 5175.,
                  5225., 5275., 5325., 5375., 5425., 5475., 5525., 5575., 5625., 5675.,
                  5725., 5775., 5825., 5875., 5925., 5975., 6025., 6075., 6125., 6175.,
                  6225., 6275., 6325., 6375., 6425., 6475., 6525., 6575., 6625., 6675.,
                  6725., 6775., 6825., 6875., 6925., 6975., 7025., 7075., 7125., 7175.,
                  7225., 7275., 7325., 7375., 7425., 7475., 7525., 7575., 7625., 7675.,
                  7725., 7775., 7825., 7875., 7925., 7975., 8025., 8075., 8125., 8175.,
                  8225., 8275., 8325., 8375., 8425., 8475., 8525., 8575., 8625., 8675.,
                  8725., 8775., 8825., 8875., 8925., 8975., 9025., 9075., 9125., 9175.,
                  9225., 9275., 9325., 9375., 9425., 9475., 9525., 9575., 9625., 9675.,
                  9725., 9775., 9825., 9875., 9925., 9975., 10025., 10075., 10125.,
                  10175., 10225., 10275., 10325., 10375., 10425., 10475., 10525.,
                  10575., 10625., 10675., 10725., 10775., 10825., 10875., 10925.,
                  10975., 11025., 11075., 11125., 11175., 11225., 11275., 11325.,
                  11375., 11425., 11475., 11525., 11575., 11625., 11675., 11725.,
                  11775., 11825., 11875., 11925., 11975., 12025., 12075., 12125.,
                  12175., 12225., 12275., 12325., 12375., 12425., 12475., 12525.,
                  12575., 12625., 12675., 12725., 12775., 12825., 12875., 12925.,
                  12975., 13025., 13075., 13125., 13175., 13225., 13275., 13325.,
                  13375., 13425., 13475., 13525., 13575., 13625., 13675., 13725.,
                  13775., 13825., 13875., 13925., 13975., 14025., 14075., 14125.,
                  14175., 14225., 14275., 14325., 14375., 14425., 14475., 14525.,
                  14575., 14625., 14675., 14725., 14775., 14825., 14875., 14925.,
                  14975., 15025., 15075., 15125., 15175., 15225., 15275., 15325.,
                  15375., 15425., 15475., 15525., 15575., 15625., 15675., 15725.,
                  15775., 15825., 15875., 15925., 15975., 16025.] * u.kHz,
        'times': np.arange(1440) * u.min,
    }
    array = np.zeros((319, 1440))
    read_dat.return_value = (meta, array)
    file = Path('fake.dat')
    spec = Spectrogram(file)
    assert isinstance(spec, SWAVESSpectrogram)
    assert spec.observatory == 'STEREO A'
    assert spec.instrument == 'SWAVES'
    assert spec.detector == 'HFR'
    assert spec.start_time.datetime == datetime(2020, 11, 28, 0, 0)
    assert spec.end_time.datetime == datetime(2020, 11, 28, 23, 59)
    assert spec.wavelength.min == 125 * u.kHz
    assert spec.wavelength.max == 16025 * u.kHz
