from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = [
    "ILOFARMode357Spectrogram",
    "ILOFARMeta",
]


class ILOFARMeta(SpectrogramMeta):
    """Metadata for Irish LOFAR Station spectrograms."""

    @property
    def mode(self) -> int | None:
        """The observation mode."""
        return self.get("mode")

    @property
    def polarisation(self) -> str | None:
        """The polarisation of the observation."""
        return self.get("polarisation")


class ILOFARMode357Spectrogram(GenericSpectrogram):
    """
    Irish LOFAR Station mode 357 Spectrogram
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, ILOFARMeta):
            meta = ILOFARMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def mode(self):
        return self.meta.mode

    @property
    def polarisation(self):
        return self.meta.polarisation

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "ILOFAR"
