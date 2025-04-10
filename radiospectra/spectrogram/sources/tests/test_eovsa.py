from pathlib import Path
from datetime import datetime
from unittest import mock

import numpy as np
import pytest

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram import Spectrogram
from radiospectra.spectrogram.sources import EOVSASpectrogram


@pytest.fixture
def eovsa_data():
    start_time = Time("2021-02-13 15:41:20.999")
    end_time = Time("2021-02-13 20:43:18.999")
    meta = {
        "fits_meta": {"POLARIZA": "I"},
        "detector": "EOVSA",
        "instrument": "EOVSA",
        "observatory": "Owens Valley",
        "start_time": start_time,
        "end_time": end_time,
        "wavelength": a.Wavelength(1105371.117591858 * u.kHz, 17979686.737060547 * u.kHz),
        "times": np.linspace(0, (end_time - start_time).to_value("s"), 15463),
        "freqs": [
            1.1053711,
            1.1161133,
            1.1268555,
            1.1375977,
            1.1483399,
            1.159082,
            1.1698242,
            1.1805664,
            1.1913086,
            1.2020508,
            1.212793,
            1.2235352,
            1.2342774,
            1.2450196,
            1.2557617,
            1.2665039,
            1.2772461,
            1.2879883,
            1.2987305,
            1.3094727,
            1.3202149,
            1.330957,
            1.3416992,
            1.3524414,
            1.3631836,
            1.3739258,
            1.384668,
            1.3954102,
            1.4061524,
            1.4168946,
            1.432373,
            1.4471191,
            1.4618652,
            1.4766114,
            1.4913574,
            1.5061035,
            1.5208496,
            1.5355957,
            1.5503418,
            1.5650879,
            1.579834,
            1.59458,
            1.6093261,
            1.6240723,
            1.6388184,
            1.6535645,
            1.6683105,
            1.6830566,
            1.6978028,
            1.7125489,
            1.7272949,
            1.742041,
            2.4125,
            2.4375,
            2.4625,
            2.4875,
            2.5125,
            2.5375,
            2.5625,
            2.5875,
            2.6125,
            2.6375,
            2.6625,
            2.6875,
            2.7125,
            2.7385254,
            2.7655761,
            2.7926269,
            2.8196778,
            2.8467286,
            2.8737793,
            2.90083,
            2.9278808,
            2.9549317,
            2.9819825,
            3.0090332,
            3.036084,
            3.0647461,
            3.0942383,
            3.1237304,
            3.1532226,
            3.182715,
            3.212207,
            3.2416992,
            3.2711914,
            3.3006835,
            3.3301759,
            3.359668,
            3.391211,
            3.4236329,
            3.4560547,
            3.4884765,
            3.5208983,
            3.5533204,
            3.5857422,
            3.618164,
            3.650586,
            3.6830077,
            3.7180176,
            3.7540526,
            3.790088,
            3.826123,
            3.8621583,
            3.8981934,
            3.9342284,
            3.9702637,
            4.006299,
            4.0453124,
            4.0859375,
            4.1265626,
            4.1671877,
            4.2078123,
            4.2484374,
            4.2890625,
            4.3296876,
            4.3703127,
            4.4109373,
            4.4515624,
            4.4921875,
            4.5328126,
            4.5734377,
            4.6140623,
            4.6546874,
            4.6953125,
            4.7359376,
            4.7765627,
            4.8171873,
            4.8578124,
            4.8984375,
            4.9390626,
            4.9796877,
            5.0203123,
            5.0609374,
            5.1015625,
            5.1421876,
            5.1828127,
            5.2234373,
            5.2640624,
            5.3046875,
            5.3453126,
            5.3859377,
            5.4265623,
            5.4671874,
            5.5078125,
            5.5484376,
            5.5890627,
            5.6296873,
            5.6703124,
            5.7109375,
            5.7515626,
            5.7921877,
            5.8328123,
            5.8734374,
            5.9140625,
            5.9546876,
            5.9953127,
            6.0359373,
            6.0765624,
            6.1171875,
            6.1578126,
            6.1984377,
            6.2390623,
            6.2796874,
            6.3203125,
            6.3609376,
            6.4015627,
            6.4421873,
            6.4828124,
            6.5234375,
            6.5640626,
            6.6046877,
            6.6453123,
            6.6859374,
            6.7265625,
            6.7671876,
            6.8078127,
            6.8484373,
            6.8890624,
            6.9296875,
            6.9703126,
            7.0109377,
            7.0515623,
            7.0921874,
            7.1328125,
            7.1734376,
            7.2140627,
            7.2546873,
            7.2953124,
            7.3359375,
            7.3765626,
            7.4171877,
            7.4578123,
            7.4984374,
            7.5390625,
            7.5796876,
            7.6203127,
            7.6609373,
            7.7015624,
            7.7421875,
            7.7828126,
            7.8234377,
            7.8640623,
            7.9046874,
            7.9453125,
            7.9859376,
            8.026563,
            8.067187,
            8.107813,
            8.1484375,
            8.189062,
            8.229688,
            8.270312,
            8.310938,
            8.3515625,
            8.392187,
            8.432813,
            8.473437,
            8.514063,
            8.5546875,
            8.595312,
            8.635938,
            8.676562,
            8.717188,
            8.7578125,
            8.798437,
            8.839063,
            8.879687,
            8.920313,
            8.9609375,
            9.001562,
            9.042188,
            9.082812,
            9.123438,
            9.1640625,
            9.204687,
            9.245313,
            9.285937,
            9.326563,
            9.3671875,
            9.407812,
            9.448438,
            9.489062,
            9.529688,
            9.5703125,
            9.610937,
            9.651563,
            9.692187,
            9.732813,
            9.7734375,
            9.814062,
            9.854688,
            9.895312,
            9.935938,
            9.9765625,
            10.017187,
            10.057813,
            10.098437,
            10.139063,
            10.1796875,
            10.220312,
            10.260938,
            10.301562,
            10.342188,
            10.3828125,
            10.423437,
            10.464063,
            10.504687,
            10.545313,
            10.5859375,
            10.626562,
            10.667188,
            10.707812,
            10.748438,
            10.7890625,
            10.829687,
            10.870313,
            10.910937,
            10.951563,
            10.9921875,
            11.032812,
            11.073438,
            11.114062,
            11.154688,
            11.1953125,
            11.235937,
            11.276563,
            11.317187,
            11.357813,
            11.3984375,
            11.439062,
            11.479688,
            11.520312,
            11.560938,
            11.6015625,
            11.642187,
            11.682813,
            11.723437,
            11.764063,
            11.8046875,
            11.845312,
            11.885938,
            11.926562,
            11.967188,
            12.0078125,
            12.048437,
            12.089063,
            12.129687,
            12.170313,
            12.2109375,
            12.251562,
            12.292188,
            12.332812,
            12.373438,
            12.4140625,
            12.454687,
            12.495313,
            12.535937,
            12.576563,
            12.6171875,
            12.657812,
            12.698438,
            12.739062,
            12.779688,
            12.8203125,
            12.860937,
            12.901563,
            12.942187,
            12.982813,
            13.0234375,
            13.064062,
            13.104688,
            13.145312,
            13.185938,
            13.2265625,
            13.267187,
            13.307813,
            13.348437,
            13.389063,
            13.4296875,
            13.470312,
            13.510938,
            13.551562,
            13.592188,
            13.6328125,
            13.673437,
            13.714063,
            13.754687,
            13.795313,
            13.8359375,
            13.876562,
            13.917188,
            13.957812,
            13.998438,
            14.0390625,
            14.079687,
            14.120313,
            14.160937,
            14.201563,
            14.2421875,
            14.282812,
            14.323438,
            14.364062,
            14.404688,
            14.4453125,
            14.485937,
            14.526563,
            14.567187,
            14.607813,
            14.6484375,
            14.689062,
            14.729688,
            14.770312,
            14.810938,
            14.8515625,
            14.892187,
            14.932813,
            14.973437,
            15.014063,
            15.0546875,
            15.095312,
            15.135938,
            15.176562,
            15.217188,
            15.2578125,
            15.298437,
            15.339063,
            15.379687,
            15.420313,
            15.4609375,
            15.501562,
            15.542188,
            15.582812,
            15.623438,
            15.6640625,
            15.704687,
            15.745313,
            15.785937,
            15.826563,
            15.8671875,
            15.907812,
            15.948438,
            15.989062,
            16.029688,
            16.070312,
            16.110937,
            16.151562,
            16.192188,
            16.232813,
            16.273438,
            16.314062,
            16.354687,
            16.395313,
            16.435938,
            16.476562,
            16.517187,
            16.557812,
            16.598438,
            16.639063,
            16.679688,
            16.720312,
            16.760937,
            16.801563,
            16.842188,
            16.882812,
            16.923437,
            16.964062,
            17.004688,
            17.045313,
            17.085938,
            17.126562,
            17.167187,
            17.207813,
            17.248438,
            17.289062,
            17.329687,
            17.370312,
            17.410938,
            17.451563,
            17.492188,
            17.532812,
            17.573437,
            17.614063,
            17.654688,
            17.695312,
            17.735937,
            17.776562,
            17.817188,
            17.857813,
            17.898438,
            17.939062,
            17.979687,
        ]
        * u.GHz,
    }
    array = np.zeros((451, 15463))
    return meta, array


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_eovsa_xpall(parse_path_moc, eovsa_data):
    meta, array = eovsa_data
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.fts")
    spec = Spectrogram(file)
    assert isinstance(spec, EOVSASpectrogram)
    assert spec.observatory == "OWENS VALLEY"
    assert spec.instrument == "EOVSA"
    assert spec.detector == "EOVSA"
    assert spec.start_time.datetime == datetime(2021, 2, 13, 15, 41, 20, 999000)
    assert spec.end_time.datetime == datetime(2021, 2, 13, 20, 43, 18, 999000)
    assert spec.wavelength.min.to(u.GHz) == 1.105371117591858 * u.GHz
    assert spec.wavelength.max.to(u.GHz) == 17.979686737060547 * u.GHz
    assert spec.polarisation == "I"


@mock.patch("radiospectra.spectrogram.spectrogram_factory.parse_path")
def test_eovsa_tpall(parse_path_moc, eovsa_data):
    meta, array = eovsa_data
    meta["fits_meta"]["POLARIZA"] = "I"
    parse_path_moc.return_value = [(array, meta)]
    file = Path("fake.fts")
    spec = Spectrogram(file)
    assert isinstance(spec, EOVSASpectrogram)
    assert spec.observatory == "OWENS VALLEY"
    assert spec.instrument == "EOVSA"
    assert spec.detector == "EOVSA"
    assert spec.start_time.datetime == datetime(2021, 2, 13, 15, 41, 20, 999000)
    assert spec.end_time.datetime == datetime(2021, 2, 13, 20, 43, 18, 999000)
    assert spec.wavelength.min.to(u.GHz) == 1.105371117591858 * u.GHz
    assert spec.wavelength.max.to(u.GHz) == 17.979686737060547 * u.GHz
    assert spec.polarisation == "I"
