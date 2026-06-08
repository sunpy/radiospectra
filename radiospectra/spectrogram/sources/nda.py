import astropy.units as u
from astropy.coordinates.earth import EarthLocation

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["NDASpectrogram"]


class NDASpectrogram(GenericSpectrogram):
    """
    Nançay Decameter Array (NDA) Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time("2025-03-26", "2025-03-27"), a.Instrument("NDA"))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <NDASpectrogram NDA, newroutine, ORN 10.010000228881836 MHz - 87.98999786376953 MHz, ...>
    """

    @property
    def observatory_location(self):
        lat = self.meta["fits_meta"].get("OBSGEO-B")
        lon = self.meta["fits_meta"].get("OBSGEO-L")
        height = self.meta["fits_meta"].get("OBSGEO-H")
        if lat is not None and lon is not None and height is not None:
            return EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=height * u.m)
        return None

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        telescope = meta.get("fits_meta", {}).get("TELESCOP", "")
        instrument = meta.get("instrument", "")
        return telescope == "NDA" or instrument == "NDA"
