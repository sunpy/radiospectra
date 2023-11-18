from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = [
    "ILOFARMode357Spectrogram",
]


class ILOFARMode357Spectrogram(GenericSpectrogram):
    """
    Irish LOFAR Station mode 357 Spectrogram
    """

    @property
    def mode(self):
        return self.meta.get("mode")

    @property
    def polarisation(self):
        return self.meta.get("polarisation")

    @classmethod
    def is_datasource_for(cls, data, meta, **kwargs):
        return meta["instrument"] == "ILOFAR"
