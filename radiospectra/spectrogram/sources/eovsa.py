from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["EOVSASpectrogram"]


class EOVSASpectrogram(GenericSpectrogram):
    """
    Extend Owen Valley Array (EOVSA) Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2021/05/07 00:00', '2021/05/07 23:00'), a.Instrument.eovsa)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <EOVSASpectrogram OWENS VALLEY, EOVSA, EOVSA 1105371.117591858 kHz - 17979686.737060547 kHz, 2021-05-07T13:48:20.999 to 2021-05-08T01:50:59.999>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
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
