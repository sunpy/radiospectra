from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RFSSpectrogram", "RFSMeta"]


class RFSMeta(SpectrogramMeta):
    """Metadata for PSP FIELDS/RFS spectrograms."""

    @property
    def level(self) -> str | None:
        """The data processing level."""
        cdf_globals = self.get("cdf_globals")
        if cdf_globals:
            data_type = cdf_globals.get("Data_type")
            if data_type is None:
                return None
            if isinstance(data_type, list) or hasattr(data_type, "tolist"):
                data_type = data_type[0]
            return data_type.split(">")[0]
        return None

    @property
    def version(self) -> int | None:
        """The data version."""
        cdf_globals = self.get("cdf_globals")
        if cdf_globals:
            data_version = cdf_globals.get("Data_version")
            if data_version is None:
                return None
            if isinstance(data_version, list) or hasattr(data_version, "tolist"):
                data_version = data_version[0]
            return int(data_version)
        return None


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
        if not isinstance(meta, RFSMeta):
            meta = RFSMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def level(self):
        return self.meta.level

    @property
    def version(self):
        return self.meta.version

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return (
            meta["observatory"] == "PSP" and meta["instrument"] == "FIELDS/RFS" and meta["detector"] in ("lfr", "hfr")
        )
