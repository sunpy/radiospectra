from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RFSSpectrogram"]


class RFSSpectrogram(GenericSpectrogram):
    """
    Parker Solar Probe FIELDS/Radio Frequency Spectrometer (RFS) Spectrogram.

    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rfs)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RFSSpectrogram PSP, FIELDS/RFS, LFR 10.546879882812501 kHz - 1687.5 kHz, 2019-10-05T00:01:32.395 to 2019-10-05T22:16:30.493>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def level(self):
        data_type = self.meta["cdf_meta"]["Data_type"]
        if isinstance(data_type, list) or hasattr(data_type, "tolist"):
            data_type = data_type[0]
        return data_type.split(">")[0]

    @property
    def version(self):
        data_version = self.meta["cdf_meta"]["Data_version"]
        if isinstance(data_version, list) or hasattr(data_version, "tolist"):
            data_version = data_version[0]
        return int(data_version)

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return (
            meta["observatory"] == "PSP" and meta["instrument"] == "FIELDS/RFS" and meta["detector"] in ("lfr", "hfr")
        )
