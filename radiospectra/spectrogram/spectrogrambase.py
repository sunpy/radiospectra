from typing import Any, ClassVar
from collections.abc import Mapping, Callable

from astropy.time import Time
from astropy.units import Quantity
from astropy.units.typing import QuantityLike

from sunpy.net._attrs import Wavelength

from radiospectra.exceptions import SpectraMetaValidationError
from radiospectra.mixins import NonUniformImagePlotMixin, PcolormeshPlotMixin

__all__ = ["GenericSpectrogram"]


class GenericSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin):
    """
    Base spectrogram class all spectrograms inherit.

    Attributes
    ----------
    meta : `dict-like`
        Metadata for the spectrogram.
    data : `numpy.ndarray`
        The spectrogram data itself is a 2D array.
    """

    _registry: ClassVar[dict[type["GenericSpectrogram"], Callable[..., bool]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "is_datasource_for"):
            cls._registry[cls] = cls.is_datasource_for

    def __init__(self, data: QuantityLike, meta: Mapping[str, Any], **kwargs: Any) -> None:
        self.data = data
        self.meta = meta
        self._validate_meta()

    @property
    def observatory(self) -> str:
        """
        The name of the observatory which recorded the spectrogram.
        """
        return str(self.meta["observatory"].upper())

    @property
    def instrument(self) -> str:
        """
        The name of the instrument which recorded the spectrogram.
        """
        return str(self.meta["instrument"].upper())

    @property
    def detector(self) -> str:
        """
        The detector which recorded the spectrogram.
        """
        return str(self.meta["detector"].upper())

    @property
    def start_time(self) -> Time:
        """
        The start time of the spectrogram.
        """
        return Time(self.meta["start_time"])

    @property
    def end_time(self) -> Time:
        """
        The end time of the spectrogram.
        """
        return Time(self.meta["end_time"])

    @property
    def wavelength(self) -> Wavelength:
        """
        The wavelength range of the spectrogram.
        """
        return self.meta["wavelength"]

    @property
    def times(self) -> Time:
        """
        The times of the spectrogram.
        """
        return self.meta["times"]

    @property
    def frequencies(self) -> Quantity:
        """
        The frequencies of the spectrogram.
        """
        return self.meta["freqs"]

    def _validate_meta(self) -> None:
        """
        Validates the meta-information associated with a Spectrogram.

        This method includes very basic validation checks which apply to
        all of the kinds of files that radiospectra can read.
        Datasource-specific validation should be handled in the relevant
        file in radiospectra.spectrogram.sources.
        """
        msg = "Spectrogram coordinate units for {} axis not present in metadata."
        err_message = []
        for i, ax in enumerate(["times", "freqs"]):
            if self.meta.get(ax) is None:
                err_message.append(msg.format(ax))
        if err_message:
            raise SpectraMetaValidationError("\n".join(err_message))

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}"
            f" {self.wavelength.min} - {self.wavelength.max},"
            f" {self.start_time.isot} to {self.end_time.isot}>"
        )
