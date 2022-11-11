from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RPWSpectrogram"]


class RPWSpectrogram(GenericSpectrogram):
    """
    Solar Orbiter Radio and Plasma Waves (RPW) RPW-HFR-SURV spectrogram.

    For more information on the instrument see `<https://rpw.lesia.obspm.fr>`__.

    Examples
    --------
    >>> import sunpy_soar
    >>> from sunpy_soar.attrs import Identifier
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2020-07-11', '2020-07-11 23:59'), a.Instrument('RPW'),
    ...             a.Level(2), a.soar.Product('RPW-HFR-SURV')) #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RSTNSpectrogram LEARMONTH, RSTN, RSTN 25000.0 kHz - 180000.0 kHz, 2017-09-06T22:31:51.000 to 2017-09-07T10:06:36.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "RPW"
