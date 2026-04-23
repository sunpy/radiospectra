from radiospectra.exceptions import SpectraMetaValidationError
from radiospectra.mixins import NonUniformImagePlotMixin, PcolormeshPlotMixin

__all__ = ["GenericSpectrogram"]


class GenericSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin):
    """
    Base spectrogram class all spectrograms inherit.

    Attributes
    ----------
    meta : `dict-like`
        Meta data for the spectrogram.
    data : `numpy.ndarray`
        The spectrogram data itself a 2D array.
    """

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "is_datasource_for"):
            cls._registry[cls] = cls.is_datasource_for

    def __init__(self, data, meta, **kwargs):
        self.data = data
        self.meta = meta
        self._validate_meta()

    @property
    def observatory(self):
        """
        The name of the observatory which recorded the spectrogram.
        """
        return self.meta["observatory"].upper()

    @property
    def instrument(self):
        """
        The name of the instrument which recorded the spectrogram.
        """
        return self.meta["instrument"].upper()

    @property
    def detector(self):
        """
        The detector which recorded the spectrogram.
        """
        return self.meta["detector"].upper()

    @property
    def start_time(self):
        """
        The start time of the spectrogram.
        """
        return self.meta["start_time"]

    @property
    def end_time(self):
        """
        The end time of the spectrogram.
        """
        return self.meta["end_time"]

    @property
    def wavelength(self):
        """
        The wavelength range of the spectrogram.
        """
        return self.meta["wavelength"]

    @property
    def times(self):
        """
        The times of the spectrogram.
        """
        return self.meta["times"]

    @property
    def frequencies(self):
        """
        The frequencies of the spectrogram.
        """
        return self.meta["freqs"]

    def _validate_meta(self):
        """
        Validates the meta-information associated with a Spectrogram.

        This method includes very basic validation checks which apply to
        all of the kinds of files that radiospectra can read.
        Datasource-specific validation should be handled in the relevant
        file in the radiospectra.spectrogram.sources.
        """
        msg = "Spectrogram coordinate units for {} axis not present in metadata."
        err_message = []
        for i, ax in enumerate(["times", "freqs"]):
            if self.meta.get(ax) is None:
                err_message.append(msg.format(ax))
        if err_message:
            raise SpectraMetaValidationError("\n".join(err_message))

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}"
            f" {self.wavelength.min} - {self.wavelength.max},"
            f" {self.start_time.isot} to {self.end_time.isot}>"
        )

    def __eq__(self, other):
        if not isinstance(other, GenericSpectrogram):
            return NotImplemented

        import numpy as np

        if not np.array_equal(self.data, other.data):
            return False

        if set(self.meta.keys()) != set(other.meta.keys()):
            return False

        for k, v in self.meta.items():
            other_v = other.meta[k]
            if isinstance(v, np.ndarray) or hasattr(v, "__array__"):
                if not np.array_equal(v, other_v):
                    return False
            else:
                if v != other_v:
                    return False
        return True

    def __copy__(self):
        import copy

        return self.__class__(data=copy.copy(self.data), meta=copy.copy(self.meta))

    def __deepcopy__(self, memo):
        import copy

        return self.__class__(data=copy.deepcopy(self.data, memo), meta=copy.deepcopy(self.meta, memo))
