import astropy.units as u
from astropy.coordinates.earth import EarthLocation

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["CALISTOSpectrogram"]


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
    >>> spec.plot()  #doctest: +SKIP
    """

    def __init__(self, data, meta, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def observatory_location(self):
        lat = self.meta["fits_meta"]["OBS_LAT"] * u.deg * 1.0 if self.meta["fits_meta"]["OBS_LAC"] == "N" else -1.0
        lon = self.meta["fits_meta"]["OBS_LON"] * u.deg * 1.0 if self.meta["fits_meta"]["OBS_LOC"] == "E" else -1.0
        height = self.meta["fits_meta"]["OBS_ALT"] * u.m
        return EarthLocation(lat=lat, lon=lon, height=height)

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "e-CALLISTO" or meta["detector"] == "e-CALLISTO"
