import numpy as np

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["WAVESSpectrogram", "WAVESMeta"]


class WAVESMeta(SpectrogramMeta):
    """Metadata for WIND/WAVES spectrograms."""

    pass


class WAVESSpectrogram(GenericSpectrogram):
    """
    Wind Waves Spectrogram.

    Examples
    --------
    >>> import radiospectra.net  #doctest: +SKIP
    >>> from sunpy.net import Fido, attrs as a  #doctest: +SKIP
    >>> from radiospectra.spectrogram import Spectrogram  #doctest: +SKIP
    >>> from radiospectra.net import attrs as ra  #doctest: +SKIP
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA +SKIP
    ...                     a.Instrument('WAVES'))  #doctest: +REMOTE_DATA +SKIP
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA +SKIP
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA +SKIP
    >>> spec  #doctest: +REMOTE_DATA +SKIP
    <WAVESSpectrogram WIND, WAVES, RAD1 20.0 kHz - 1040.0 kHz, 2019-10-05T00:00:00.000 to 2019-10-05T23:59:59.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA +SKIP
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, WAVESMeta):
            meta = WAVESMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @classmethod
    def is_datasource_for(cls, header, raw_object, **kwargs):
        if hasattr(header, "get") and header.get("instrument") == "WAVES":
            return True
        return hasattr(header, "get") and header.get("file_type") == "idl_sav" and header.get("instrument") == "waves"

    @classmethod
    def from_raw(cls, header, raw_object):
        file = header.get("file_path")
        data = raw_object
        data_array = data["arrayb"]
        if file.suffix == ".R1":
            freqs = np.linspace(20, 1040, 256) * u.kHz
            receiver = "RAD1"
        elif file.suffix == ".R2":
            freqs = np.linspace(1.075, 13.825, 256) * u.MHz
            receiver = "RAD2"
        else:
            raise ValueError(f"Unknown WIND/WAVES file type: {file.suffix}")

        bg = data_array[:, -1]
        data_vals = data_array[:, :-1]
        start_time = Time.strptime(file.stem.split("_")[-1], "%Y%m%d")
        end_time = start_time + 86399 * u.s
        times = start_time + (np.arange(1440) * 60 + 30) * u.s
        meta = WAVESMeta(
            {
                "instrument": "WAVES",
                "observatory": "WIND",
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs[0], freqs[-1]),
                "detector": receiver,
                "freqs": freqs,
                "times": times,
                "background": bg,
            }
        )
        return cls(data_vals, meta)
