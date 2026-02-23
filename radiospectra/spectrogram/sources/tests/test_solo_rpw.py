from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.sources import RPWSpectrogram


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_solo_rpw_tnr(parse_path_moc):
    start_time = Time("2024-03-23 00:00:00.000")
    end_time = Time("2024-03-24 00:00:00.000")

    meta = {
        "cdf_meta": {
            "Project": "SOLO>Solar Orbiter",
            "Source_name": "SOLO>Solar Orbiter",
            "Descriptor": "RPW-TNR-SURV-FLUX>Radio and Plasma Waves, Thermal Noise Receiver, Survey mode, spectral data in physical units",
            "Data_type": "L3>Level 3 Data",
            "Data_version": "01",
            "Logical_file_id": "solo_L3_rpw-tnr-surv-flux_20240323_V01",
            "Instrument": "RPW",
        },
        "detector": "RPW-TNR",
        "instrument": "RPW",
        "observatory": "SOLO",
        "start_time": start_time,
        "end_time": end_time,
        "wavelength": a.Wavelength(3.992000102996826 * u.kHz, 978.572021484375 * u.kHz),
        "times": start_time + np.linspace(0, (end_time - start_time).to_value("s"), 7322) * u.s,
        "freqs": np.array([  3992,   4169,   4353,   4546,   4747,   4957,   5177,   5406,   5645,
            5895,   6156,   6429,   6713,   7011,   7321,   7645,   7984,   8337,
            8706,   9092,   9494,   9914,  10353,  10812,  11290,  11790,  12312,
            12857,  13427,  14021,  14642,  15290,  15967,  16674,  17412,  18183,
            18988,  19829,  20707,  21624,  22581,  23581,  24625,  25715,  26853,
            28042,  29284,  30580,  31934,  33348,  34825,  36366,  37976,  39658,
            41414,  43247,  45162,  47161,  49249,  51430,  53707,  56085,  58568,
            61161,  63869,  66696,  69649,  72733,  75953,  79316,  82827,  86494,
            90324,  94323,  98499, 102860, 107414, 112169, 117135, 122322, 127737,
            133393, 139298, 145466, 151906, 158631, 165655, 172989, 180648, 188646,
            196998, 205719, 214827, 224339, 234271, 244643, 255474, 266785, 278597,
            290931, 303812, 317263, 331309, 345977, 361295, 377291, 393995, 411439,
            429655, 448677, 468542, 489286, 510949, 533570, 557193, 581862, 607624,
            634525, 662618, 691955, 722590, 754582, 787990, 822878, 859310, 897355,
            937084, 978572]) * u.Hz,
                }


    array = np.zeros((128, 7322))
    parse_path_moc.return_value = [(array, meta)]

    file = Path("solo_L3_rpw-tnr-surv-flux_20240323_V01.cdf")
    spec = Spectrogram(file)

    assert isinstance(spec, RPWSpectrogram)
    assert spec.observatory == "SOLO"
    assert spec.instrument == "RPW"
    assert spec.detector == "RPW-TNR"
    assert spec.start_time.datetime == datetime(2024, 3, 23, 0, 0, 0, 0)
    assert spec.end_time.datetime == datetime(2024, 3, 24, 0, 0, 0, 0)
    assert spec.wavelength.min == 3.992000102996826 * u.kHz
    assert spec.wavelength.max == 978.572021484375 * u.kHz


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_solo_rpw_hfr(parse_path_moc):
    start_time = Time("2024-03-23 00:00:00.000")
    end_time = Time("2024-03-24 00:00:00.000")

    meta = {
        "cdf_meta": {
            "Project": "SOLO>Solar Orbiter",
            "Source_name": "SOLO>Solar Orbiter",
            "Descriptor": "RPW-HFR-SURV-FLUX>Radio and Plasma Waves,High Frequency Receiver, Survey mode, spectral data in physical units",
            "Data_type": "L3>Level 3 Data",
            "Data_version": "01",
            "Logical_file_id": "solo_L3_rpw-hfr-surv-flux_20240323_V01",
            "Instrument": "RPW",
        },
        "detector": "RPW-HFR",
        "instrument": "RPW",
        "observatory": "SOLO",
        "start_time": start_time,
        "end_time": end_time,
        "wavelength": a.Wavelength(425 * u.kHz, 16325 * u.kHz),
        "times": start_time + np.linspace(0, (end_time - start_time).to_value("s"), 16499) * u.s,
        "freqs": np.array([425000, 525000, 625000, 675000, 775000, 875000, 975000, 1025000,
            1225000, 1375000, 1475000, 1725000, 1825000, 2075000, 2425000,
            2675000, 3225000, 3325000, 3525000, 3825000, 3925000, 4125000,
            4525000, 4875000, 5225000, 5475000, 5825000, 6175000, 6525000,
            6875000, 7375000, 7625000, 7975000, 8225000, 8575000, 9175000,
            10025000, 10125000, 11025000, 11375000, 12225000, 12475000,
            13375000, 13725000, 14375000, 14925000, 15275000, 15625000,
            16075000, 16325000]) * u.Hz,
    }


    array = np.zeros((50, 16499))
    parse_path_moc.return_value = [(array, meta)]

    file = Path("solo_L3_rpw-hfr-surv-flux_20240323_V01.cdf")
    spec = Spectrogram(file)

    assert isinstance(spec, RPWSpectrogram)
    assert spec.observatory == "SOLO"
    assert spec.instrument == "RPW"
    assert spec.detector == "RPW-HFR"
    assert spec.start_time.datetime == datetime(2024, 3, 23, 0, 0, 0, 0)
    assert spec.end_time.datetime == datetime(2024, 3, 24, 0, 0, 0, 0)
    assert spec.wavelength.min == 425 * u.kHz
    assert spec.wavelength.max == 16325 * u.kHz
