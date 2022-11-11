from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RSTNSpectrogram"]


class RSTNSpectrogram(GenericSpectrogram):
    """
    Radio Solar Telescope Network.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
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
