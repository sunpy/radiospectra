from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["SWAVESSpectrogram"]


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
