from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["WAVESSpectrogram"]


class WAVESSpectrogram(GenericSpectrogram):
    """
    Wind Waves Spectrogram.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument('WAVES'))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <WAVESSpectrogram WIND, WAVES, RAD1 20.0 kHz - 1040.0 kHz, 2019-10-05T00:00:00.000 to 2019-10-05T23:59:59.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
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
