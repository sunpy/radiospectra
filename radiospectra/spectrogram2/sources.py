import astropy.units as u
from astropy.coordinates.earth import EarthLocation

from radiospectra.spectrogram2.spectrogram import GenericSpectrogram

__all__ = ["SWAVESSpectrogram", "RFSSpectrogram", "CALISTOSpectrogram", "EOVSASpectrogram", "RSTNSpectrogram"]


class SWAVESSpectrogram(GenericSpectrogram):
    """
    STEREO Waves or S/WAVES, SWAVES Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram2 import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument('SWAVES'))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[1][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <SWAVESSpectrogram STEREO A, SWAVES, LFR 2.6 kHz - 153.4 kHz, 2019-10-05T00:00:00.000 to 2019-10-05T23:59:00.000>
    >>> spec.plot() #doctest: +REMOTE_DATA
    """

    def __init__(self, data, meta, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def receiver(self):
        """
        The name of the receiver.
        """
        return self.meta["receiver"]

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "swaves"


class WAVESSpectrogram(GenericSpectrogram):
    """
    Wind Waves Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram2 import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument('WAVES'))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <WAVESSpectrogram WIND, WAVES, RAD1 20.0 kHz - 1040.0 kHz, 2019-10-05T00:00:00.000 to 2019-10-05T23:59:59.000>
    >>> spec.plot() #doctest: +REMOTE_DATA
    """

    def __init__(self, data, meta, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def receiver(self):
        """
        The name of the receiver.
        """
        return self.meta["receiver"]

    @property
    def background(self):
        """
        The background subtracted from the data.
        """
        return self.meta.bg

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta.get("instrument", None) == "WAVES"


class RFSSpectrogram(GenericSpectrogram):
    """
    Parker Solar Probe FIELDS/Radio Frequency Spectrometer (RFS) Spectrogram.

    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram2 import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rfs)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RFSSpectrogram PSP, FIELDS/RFS, LFR 10.546879882812501 kHz - 1687.5 kHz, 2019-10-05T00:01:32.395 to 2019-10-05T22:16:30.493>
    >>> spec.plot() #doctest: +REMOTE_DATA
    """

    def __init__(self, data, meta, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def level(self):
        return self.meta["cdf_meta"]["Data_type"].split(">")[0]

    @property
    def version(self):
        return int(self.meta["cdf_meta"]["Data_version"])

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return (
            meta["observatory"] == "PSP" and meta["instrument"] == "FIELDS/RFS" and meta["detector"] in ("lfr", "hfr")
        )


class CALISTOSpectrogram(GenericSpectrogram):
    """
    CALISTO Spectrogram from the e-CALISTO network.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram2 import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument('eCALLISTO'), ra.Observatory('ALASKA'))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <CALISTOSpectrogram ALASKA, E-CALLISTO, E-CALLISTO 215000.0 kHz - 418937.98828125 kHz, 2019-10-05T23:00:00.757 to 2019-10-05T23:15:00.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
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


class EOVSASpectrogram(GenericSpectrogram):
    """
    Extend Owen Valley Array (EOVSA) Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram2 import Spectrogram
    >>> query = Fido.search(a.Time('2021/05/07 00:00', '2021/05/07 23:00'), a.Instrument.eovsa)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <EOVSASpectrogram OWENS VALLEY, EOVSA, EOVSA 1105371.117591858 kHz - 17979686.737060547 kHz, 2021-05-07T13:48:20.999 to 2021-05-08T01:50:59.999>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    """

    def __init__(self, data, meta, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def polarisation(self):
        return self.meta["fits_meta"]["POLARIZA"]

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "EOVSA" or meta["detector"] == "EOVSA"

    # TODO fix time gaps for plots need to render them as gaps
    # can prob do when generateing proper pcolormesh gird but then prob doesn't belong here


class RSTNSpectrogram(GenericSpectrogram):
    """
    Radio Solar Telescope Network.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram2 import Spectrogram
    >>> query = Fido.search(a.Time('2017/09/07 00:00', '2017/09/07 23:00'), a.Instrument.rstn)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RSTNSpectrogram LEARMONTH, RSTN, RSTN 25000.0 kHz - 180000.0 kHz, 2017-09-06T22:31:51.000 to 2017-09-07T10:06:36.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    """

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "RSTN"
