import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a
from sunpy.time import parse_time

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["EOVSASpectrogram", "EOVSAMeta"]


class EOVSAMeta(SpectrogramMeta):
    """Metadata for EOVSA spectrograms."""

    @property
    def polarisation(self) -> str | None:
        """The polarisation of the observation."""
        fits_meta = self.get("fits_meta")
        if fits_meta:
            return fits_meta.get("POLARIZA")
        return None


class EOVSASpectrogram(GenericSpectrogram):
    """
    Extend Owen Valley Array (EOVSA) Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2021/05/07 00:00', '2021/05/07 23:00'), a.Instrument.eovsa)  #doctest: +REMOTE_DATA +SKIP
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA +SKIP
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA +SKIP
    >>> spec  #doctest: +REMOTE_DATA +SKIP
    <EOVSASpectrogram OWENS VALLEY, EOVSA, EOVSA 1105371.117591858 kHz - 17979686.737060547 kHz, 2021-05-07T13:48:20.999 to 2021-05-08T01:50:59.999>
    >>> spec.plot()  #doctest: +REMOTE_DATA +SKIP
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, EOVSAMeta):
            meta = EOVSAMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def polarisation(self):
        return self.meta.polarisation

    @classmethod
    def is_datasource_for(cls, header, raw_object, **kwargs):
        return header.get("TELESCOP", "") == "EOVSA"

    @classmethod
    def from_raw(cls, header, raw_object):
        hd_pairs = raw_object
        times = Time(hd_pairs[2].data["mjd"] + hd_pairs[2].data["time"] / 1000.0 / 86400.0, format="mjd")
        freqs = hd_pairs[1].data["sfreq"] * u.GHz
        data = hd_pairs[0].data
        start_time = parse_time(hd_pairs[0].header["DATE_OBS"])
        end_time = parse_time(hd_pairs[0].header["DATE_END"])
        meta = EOVSAMeta(
            {
                "fits_meta": hd_pairs[0].header,
                "detector": "EOVSA",
                "instrument": "EOVSA",
                "observatory": "Owens Valley",
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                "times": times,
                "freqs": freqs,
            }
        )
        return cls(data, meta)
