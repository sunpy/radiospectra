from typing import Any

from astropy.units.typing import QuantityLike

from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = [
    "ILOFARMode357Spectrogram",
]


class ILOFARMode357Spectrogram(GenericSpectrogram):
    """
    Irish LOFAR Station mode 357 Spectrogram
    """

    @property
    def mode(self) -> str:
        return str(self.meta.get("mode"))

    @property
    def polarisation(self) -> str:
        return str(self.meta.get("polarisation"))

    @classmethod
    def is_datasource_for(cls, data: QuantityLike, meta: dict[str, Any], **kwargs: Any) -> bool:
        return bool(meta["instrument"] == "ILOFAR")
