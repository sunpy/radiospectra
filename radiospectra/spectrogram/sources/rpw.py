from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RPWSpectrogram"]


class RPWSpectrogram(GenericSpectrogram):
    """
    Solar Orbiter Radio and Plasma Waves (RPW) spectrogram.

    For more information on the instrument see `<https://rpw-datacenter.obspm.fr>`__.

    Examples for accessing Level 2 HFR and Level 3 TNR/HFR (calibrated) data products.

    **HFR Level 2 Example:**

    >>> import sunpy_soar
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2020-07-11', '2020-07-11 23:59'), a.Instrument('RPW'),
    ...             a.Level(2), a.soar.Product('RPW-HFR-SURV')) #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0])  #doctest: +SKIP
    >>> spec = Spectrogram(downloaded[0])  #doctest: +SKIP
    >>> spec  #doctest: +SKIP
    [<RPWSpectrogram SOLO, RPW, RPW-AGC1 375.0 kHz - 16375.0 kHz, 2020-07-11T00:00:39.352 to 2020-07-12T00:00:55.715>, <RPWSpectrogram SOLO, RPW, RPW-AGC2 375.0 kHz - 16375.0 kHz, 2020-07-11T00:00:39.352 to 2020-07-12T00:00:55.715>]
    >>> spec[0] .plot()  #doctest: +SKIP
    <matplotlib.collections.QuadMesh object at ...>

    **TNR Level 3 Example:**

    >>> import sunpy_soar  #doctest: +REMOTE_DATA
    >>> from sunpy.net import Fido, attrs as a  #doctest: +REMOTE_DATA
    >>> from radiospectra.spectrogram import Spectrogram  #doctest: +REMOTE_DATA
    >>> query = Fido.search(a.Time('2024/03/23 00:00', '2024/03/23 23:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rpw, a.Level(3), a.Provider.soar)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][query[0]["Data product"]=='rpw-tnr-surv-flux'][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RPWSpectrogram SOLO, RPW, RPW-TNR 3.992000102996826 kHz - 978.572021484375 kHz, 2024-03-23T00:04:32.873 to 2024-03-24T00:04:46.381>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>

    **HFR Level 3 Example:**

    >>> import sunpy_soar  #doctest: +REMOTE_DATA
    >>> from sunpy.net import Fido, attrs as a  #doctest: +REMOTE_DATA
    >>> from radiospectra.spectrogram import Spectrogram  #doctest: +REMOTE_DATA
    >>> query = Fido.search(a.Time('2024/03/23 00:00', '2024/03/23 23:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rpw, a.Level(3), a.Provider.soar)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][query[0]["Data product"]=='rpw-hfr-surv-flux'][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RPWSpectrogram SOLO, RPW, RPW-HFR 425.0000305175781 kHz - 16325.0009765625 kHz, 2024-03-23T00:04:14.063 to 2024-03-24T00:04:07.571>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "RPW"
