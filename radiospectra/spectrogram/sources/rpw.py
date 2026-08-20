import numpy as np

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a
from sunpy.sun.constants import sfu

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RPWSpectrogram", "RPWMeta"]


class RPWMeta(SpectrogramMeta):
    """Metadata for Solar Orbiter RPW spectrograms."""

    pass


class RPWSpectrogram(GenericSpectrogram):
    """
    Solar Orbiter Radio and Plasma Waves (RPW) spectrogram.

    For more information on the instrument see `<https://rpw-datacenter.obspm.fr>`__.

    Examples for accessing Level 2 HFR and Level 3 TNR/HFR (calibrated) data products.

    **HFR Level 2 Example:**

    >>> import sunpy_soar
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2020-07-11', '2020-07-11 23:59'), a.Instrument('RPW'),
    ...             a.Level(2), a.soar.Product('RPW-HFR-SURV')) #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0])  #doctest: +SKIP
    >>> spec = Spectrogram(downloaded[0])  #doctest: +SKIP
    >>> spec  #doctest: +SKIP
    [<RPWSpectrogram SOLO, RPW, RPW-AGC1 375.0 kHz - 16375.0 kHz, 2020-07-11T00:00:39.352 to 2020-07-12T00:00:55.715>, <RPWSpectrogram SOLO, RPW, RPW-AGC2 375.0 kHz - 16375.0 kHz, 2020-07-11T00:00:39.352 to 2020-07-12T00:00:55.715>]
    >>> spec[0] .plot()  #doctest: +SKIP
    <matplotlib.collections.QuadMesh object at ...>

    **TNR Level 3 Example:**

    >>> import sunpy_soar  #doctest: +REMOTE_DATA
    >>> from sunpy.net import Fido, attrs as a  #doctest: +REMOTE_DATA
    >>> from radiospectra.spectrogram import Spectrogram  #doctest: +REMOTE_DATA
    >>> query = Fido.search(a.Time('2024/03/23 00:00', '2024/03/23 23:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rpw, a.Level(3), a.Provider.soar)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][query[0]["Data product"]=='rpw-tnr-surv-flux'][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RPWSpectrogram SOLO, RPW, RPW-TNR 3.992000102996826 kHz - 978.572021484375 kHz, 2024-03-23T00:04:32.873 to 2024-03-24T00:04:46.381>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>

    **HFR Level 3 Example:**

    >>> import sunpy_soar  #doctest: +REMOTE_DATA
    >>> from sunpy.net import Fido, attrs as a  #doctest: +REMOTE_DATA
    >>> from radiospectra.spectrogram import Spectrogram  #doctest: +REMOTE_DATA
    >>> query = Fido.search(a.Time('2024/03/23 00:00', '2024/03/23 23:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rpw, a.Level(3), a.Provider.soar)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][query[0]["Data product"]=='rpw-hfr-surv-flux'][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RPWSpectrogram SOLO, RPW, RPW-HFR 425.0000305175781 kHz - 16325.0009765625 kHz, 2024-03-23T00:04:14.063 to 2024-03-24T00:04:07.571>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, RPWMeta):
            meta = RPWMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @classmethod
    def is_datasource_for(cls, data_or_header, meta_or_raw, **kwargs):
        meta = data_or_header if hasattr(data_or_header, "get") else meta_or_raw
        if not hasattr(meta, "get"):
            return False
        if meta.get("instrument") == "RPW":
            return True
        cdf_globals = meta.get("cdf_globals")
        if not cdf_globals:
            return False
        return "SOLO" in cdf_globals.get("Project", "")[0]

    @classmethod
    def from_raw(cls, header, raw_object):
        cdf = raw_object
        cdf_globals = header["cdf_globals"]
        data_type = cdf_globals.get("Data_type", [""])[0]
        data_descriptor = cdf_globals.get("Descriptor", "")[0]
        if "RPW-HFR-SURV" not in data_descriptor and "RPW-TNR-SURV-FLUX" not in data_descriptor:
            raise ValueError(
                f"Currently radiospectra supports Level 2 HFR survey data "
                "and Level 3 HFR, TNR survey data the file is "
                f"{cdf_globals.get('Logical_source_description', [''])[0]}"
            )
        if "L3" in data_type:
            epoch = cdf.varget("Epoch")
            times = Time("J2000.0") + epoch * u.ns
            freqs = cdf.varget("FREQUENCY") << u.Unit(cdf.varattsget("FREQUENCY")["UNITS"])
            data = cdf.varget("PSD_SFU")
            data = np.squeeze(data).T << sfu
            detector = cdf_globals.get("Instrument", [""])[0].split(">")[0]
            meta = RPWMeta(
                {
                    "cdf_globals": cdf_globals,
                    "detector": detector,
                    "instrument": "RPW",
                    "observatory": "SOLO",
                    "start_time": times[0],
                    "end_time": times[-1],
                    "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                    "times": times,
                    "freqs": freqs,
                }
            )
            return cls(data, meta)
        elif "L2" in data_type:
            # FREQUENCY_BAND_LABELS = ["HF1", "HF2"]
            # SURVEY_MODE_LABELS = ["SURVEY_NORMAL", "SURVEY_BURST"]
            # CHANNEL_LABELS = ["1", "2"]
            SENSOR_MAPPING = {
                1: "V1",
                2: "V2",
                3: "V3",
                4: "V1-V2",
                5: "V2-V3",
                6: "V3-V1",
                7: "B_MF",
                9: "HF_V1-V2",
                10: "HF_V2-V3",
                11: "HF_V3-V1",
            }

            # Extract variables
            all_times = Time("J2000.0") + cdf.varget("EPOCH") * u.Unit(cdf.varattsget("EPOCH")["UNITS"])
            all_freqs = cdf.varget("FREQUENCY") << u.Unit(cdf.varattsget("FREQUENCY")["UNITS"])

            sweep_start_indices = np.asarray(np.diff(cdf.varget("SWEEP_NUM")) != 0).nonzero()
            sweep_start_indices = np.insert((sweep_start_indices[0] + 1), 0, 0)
            times = all_times[sweep_start_indices]

            sensor = cdf.varget("SENSOR_CONFIG")
            np.unique(cdf.varget("FREQUENCY"))
            band = cdf.varget("HFR_BAND")

            u.Unit(cdf.varattsget("AGC1").get("UNIT", "V^2/Hz"))
            agc1 = cdf.varget("AGC1")
            agc2 = cdf.varget("AGC2")

            # Define number of records
            n_rec = band.shape[0]
            # Get Epoch times of first sample of each sweep in the file
            sweep_times = times
            nt = len(sweep_times)
            # Get complete list of HFR frequency values
            hfr_frequency = 375 + 50 * np.arange(321)  # This is a guess something between 320 and 324
            nf = len(hfr_frequency)

            # Initialize output 2D array containing voltage spectral power values in V^2/Hz
            # Dims = (channels[2], time of the first sweep sample[len(time)], frequency[192])
            specs = np.empty((2, nt, nf))
            # Fill 2D array with NaN for HRF frequencies not actually measured in the file
            specs[:] = np.nan

            # Get list of first index of sweeps
            isweep = sweep_start_indices[:]
            # Get number of sweeps
            n_sweeps = len(isweep)
            # Insert an element in the end of the isweep list
            # containing the end of the latest sweep
            # (required for the loop below, in order to have
            # a start/end index range for each sweep)
            isweep = np.insert(isweep, n_sweeps, n_rec)

            # Initialize sensor_config
            sensor_config = np.zeros((2, nt), dtype=object)
            tm = []
            # Perform a loop on each sweep
            for i in range(n_sweeps):
                # Get first and last index of the sweep
                i0 = isweep[i]
                i1 = isweep[i + 1]

                ts = all_times[i0]
                te = all_times[i1 - 1]
                tt = (te - ts) * 0.5 + ts
                tm.append(tt)

                # Get indices of the actual frequency channels in the frequency vector
                freq_indices = ((all_freqs[i0:i1].value - 375) / 50).astype(int)

                # fill output 2D array
                specs[0, i, freq_indices] = agc1[i0:i1]
                specs[1, i, freq_indices] = agc2[i0:i1]

                # Fill sensor config
                sensor_config[0, i] = SENSOR_MAPPING[sensor[i0, 0]]
                sensor_config[1, i] = SENSOR_MAPPING[sensor[i0, 1]]

            # Define hfr bands
            hfc = np.array(["HF1", "HF2"])
            hfc[band[:100] - 1]

            hfr_frequency = hfr_frequency << u.kHz

            res = []
            if np.any(agc1):
                meta1 = RPWMeta(
                    {
                        "cdf_globals": cdf_globals,
                        "detector": "RPW-AGC1",
                        "instrument": "RPW",
                        "observatory": "SOLO",
                        "start_time": times[0],
                        "end_time": times[-1],
                        "wavelength": a.Wavelength(hfr_frequency.min(), hfr_frequency.max()),
                        "times": times,
                        "freqs": hfr_frequency,
                    }
                )
                res.append(cls(specs[0].T, meta1))
            if np.any(agc2):
                meta2 = RPWMeta(
                    {
                        "cdf_globals": cdf_globals,
                        "detector": "RPW-AGC2",
                        "instrument": "RPW",
                        "observatory": "SOLO",
                        "start_time": times[0],
                        "end_time": times[-1],
                        "wavelength": a.Wavelength(hfr_frequency.min(), hfr_frequency.max()),
                        "times": times,
                        "freqs": hfr_frequency,
                    }
                )
                res.append(cls(specs[1].T, meta2))
            return res
