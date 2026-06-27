import astropy.units as u
from astropy.coordinates.earth import EarthLocation

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["CALISTOSpectrogram", "CALISTOMeta"]


class CALISTOMeta(SpectrogramMeta):
    """Metadata for e-CALLISTO spectrograms."""

    @property
    def observer_location(self):
        """The location of the observatory."""
        fits_meta = self.get("fits_meta")
        if fits_meta:
            lat = fits_meta.get("OBS_LAT", 0) * u.deg * (1.0 if fits_meta.get("OBS_LAC") == "N" else -1.0)
            lon = fits_meta.get("OBS_LON", 0) * u.deg * (1.0 if fits_meta.get("OBS_LOC") == "E" else -1.0)
            height = fits_meta.get("OBS_ALT", 0) * u.m
            return EarthLocation(lat=lat, lon=lon, height=height)
        return None


class CALISTOSpectrogram(GenericSpectrogram):
    """
    CALISTO Spectrogram from the e-CALISTO network.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument('eCALLISTO'), ra.Observatory('ALASKA'))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <CALISTOSpectrogram ALASKA, E-CALLISTO, E-CALLISTO 215000.0 kHz - 418937.98828125 kHz, 2019-10-05T23:00:00.757 to 2019-10-05T23:15:00.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, CALISTOMeta):
            meta = CALISTOMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def observatory_location(self):
        if hasattr(self.meta, "observer_location") and self.meta.observer_location is not None:
            return self.meta.observer_location
        lat = self.meta["fits_meta"]["OBS_LAT"] * u.deg * (1.0 if self.meta["fits_meta"]["OBS_LAC"] == "N" else -1.0)
        lon = self.meta["fits_meta"]["OBS_LON"] * u.deg * (1.0 if self.meta["fits_meta"]["OBS_LOC"] == "E" else -1.0)
        height = self.meta["fits_meta"]["OBS_ALT"] * u.m
        return EarthLocation(lat=lat, lon=lon, height=height)

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "e-CALLISTO" or meta["detector"] == "e-CALLISTO"
