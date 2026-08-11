import numpy as np

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["SWAVESSpectrogram", "SWAVESMeta"]


class SWAVESMeta(SpectrogramMeta):
    """Metadata for STEREO/SWAVES spectrograms."""

    pass


class SWAVESSpectrogram(GenericSpectrogram):
    """
    STEREO Waves or S/WAVES, SWAVES Spectrogram.

    Examples
    --------
    >>> import radiospectra.net  #doctest: +SKIP
    >>> from sunpy.net import Fido, attrs as a  #doctest: +SKIP
    >>> from radiospectra.spectrogram import Spectrogram  #doctest: +SKIP
    >>> from radiospectra.net import attrs as ra  #doctest: +SKIP
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA +SKIP
    ...                     a.Instrument('SWAVES'))  #doctest: +REMOTE_DATA +SKIP
    >>> downloaded = Fido.fetch(query[1][0])  #doctest: +REMOTE_DATA +SKIP
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA +SKIP
    >>> spec  #doctest: +REMOTE_DATA +SKIP
    <SWAVESSpectrogram STEREO A, SWAVES, LFR 2.6 kHz - 153.4 kHz, 2019-10-05T00:00:00.000 to 2019-10-05T23:59:00.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA +SKIP
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, SWAVESMeta):
            meta = SWAVESMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @classmethod
    def is_datasource_for(cls, header, raw_object, **kwargs):
        return hasattr(header, "get") and header.get("instrument") == "swaves"

    @classmethod
    def from_raw(cls, header, raw_object):
        file = header["file_path"]
        name, prod, date, spacecraft, receiver = file.stem.split("_")
        # frequency range
        freqs = np.genfromtxt(file, max_rows=1) * u.kHz
        # bg which is already subtracted from data
        bg = np.genfromtxt(file, skip_header=1, max_rows=1)
        # data
        data = np.genfromtxt(file, skip_header=2)
        times = data[:, 0] * u.min
        data = data[:, 1:].T
        start_time = Time.strptime(date, "%Y%m%d")
        end_time = start_time + times[-1]
        times = start_time + times
        meta = SWAVESMeta(
            {
                "instrument": name,
                "observatory": f"STEREO {spacecraft.upper()}",
                "product": prod,
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs[0], freqs[-1]),
                "detector": receiver,
                "freqs": freqs,
                "times": times,
                "background": bg,
            }
        )
        return cls(data, meta)
