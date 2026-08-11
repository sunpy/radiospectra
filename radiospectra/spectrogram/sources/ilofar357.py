import numpy as np

import astropy.units as u
from astropy.time import Time

from sunpy import log
from sunpy.net import attrs as a

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram
from radiospectra.utils import subband_to_freq

__all__ = [
    "ILOFARMode357Spectrogram",
    "ILOFARMeta",
]


class ILOFARMeta(SpectrogramMeta):
    """Metadata for Irish LOFAR Station spectrograms."""

    @property
    def mode(self) -> int | None:
        """The observation mode."""
        return self.get("mode")

    @property
    def polarisation(self) -> str | None:
        """The polarisation of the observation."""
        return self.get("polarisation")


class ILOFARMode357Spectrogram(GenericSpectrogram):
    """
    Irish LOFAR Station mode 357 Spectrogram
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, ILOFARMeta):
            meta = ILOFARMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def mode(self):
        return self.meta.mode

    @property
    def polarisation(self):
        return self.meta.polarisation

    @classmethod
    def is_datasource_for(cls, header, raw_object, **kwargs):
        return hasattr(header, "get") and header.get("instrument") == "ILOFAR"

    @classmethod
    def from_raw(cls, header, raw_object):
        file = header["file_path"]
        subbands = (np.arange(54, 454, 2), np.arange(54, 454, 2), np.arange(54, 230, 2))
        num_subbands = 488

        data = np.fromfile(file)
        polarisation = file.stem[-1]

        num_times = data.shape[0] / num_subbands
        if not num_times.is_integer():
            log.warning("BST file seems incomplete dropping incomplete frequencies")
            num_times = np.floor(num_times).astype(int)
            truncate = num_times * num_subbands
            data = data[:truncate]
        data = data.reshape(-1, num_subbands).T  # (Freq x Time).T = (Time x Freq)
        dt = np.arange(num_times) * 1 * u.s
        start_time = Time.strptime(file.name.split("_bst")[0], "%Y%m%d_%H%M%S")
        times = start_time + dt

        obs_mode = (3, 5, 7)
        freqs = [subband_to_freq(sb, mode) for sb, mode in zip(subbands, obs_mode)]

        # 1st 200 sbs mode 3, next 200 sbs mode 5, last 88 sbs mode 7
        spec = {0: data[:200, :], 1: data[200:400, :], 2: data[400:, :]}
        results = []
        for i in range(3):
            meta = ILOFARMeta(
                {
                    "instrument": "ILOFAR",
                    "observatory": "Birr (IE613)",
                    "start_time": times[0],
                    "mode": obs_mode[i],
                    "wavelength": a.Wavelength(freqs[i][0], freqs[i][-1]),
                    "freqs": freqs[i],
                    "times": times,
                    "end_time": times[-1],
                    "detector": "ILOFAR",
                    "polarisation": polarisation,
                }
            )
            results.append(cls(spec[i], meta))
        return results
