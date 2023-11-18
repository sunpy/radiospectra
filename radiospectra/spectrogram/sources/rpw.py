from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RPWSpectrogram"]


class RPWSpectrogram(GenericSpectrogram):
    """
    Solar Orbiter Radio and Plasma Waves (RPW) RPW-HFR-SURV spectrogram.

    For more information on the instrument see `<https://rpw.lesia.obspm.fr>`__.

    Examples
    --------
    >>> import sunpy_soar
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2020-07-11', '2020-07-11 23:59'), a.Instrument('RPW'),
    ...             a.Level(2), a.soar.Product('RPW-HFR-SURV')) #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    [<RPWSpectrogram SOLO, RPW, RPW-AGC1 375.0 kHz - 16375.0 kHz, 2020-07-11T00:00:39.352 to 2020-07-12T00:00:55.715>, <RPWSpectrogram SOLO, RPW, RPW-AGC2 375.0 kHz - 16375.0 kHz, 2020-07-11T00:00:39.352 to 2020-07-12T00:00:55.715>]
    >>> spec[0] .plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "RPW"
