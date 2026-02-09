import astropy.units as u
from astropy.time import Time

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

    @times.setter
    def times(self, value):
        """
        Update the times of the spectrogram.

        Parameters
        ----------
        value : `~astropy.time.Time` or `~astropy.units.Quantity`
            New time coordinates.

        Raises
        ------
        `TypeError`
            If ``value`` is not a `~astropy.time.Time` or `~astropy.units.Quantity`.
        `ValueError`
            If the new coordinate length does not match the current one or if units
            are not compatible with time.
        """
        current_times = self.meta["times"]
        old_start = self.meta.get("start_time")
        old_end = self.meta.get("end_time")

        if not isinstance(value, (Time, u.Quantity)):
            raise TypeError("times must be an astropy.time.Time or astropy.units.Quantity object.")

        if isinstance(value, u.Quantity) and not value.unit.is_equivalent(u.s):
            raise ValueError("times must have units compatible with time.")

        try:
            current_length = len(current_times)
            new_length = len(value)
        except TypeError as err:
            raise ValueError("times must be an array-like object.") from err

        if new_length != current_length:
            raise ValueError(f"times length must match existing times length ({current_length}), got {new_length}.")

        # If the current coordinates are absolute Time values, interpret quantity
        # inputs as offsets and convert to absolute times anchored to the first sample.
        if isinstance(value, u.Quantity) and isinstance(current_times, Time):
            value = current_times[0] + (value - value[0])

        self.meta["times"] = value

        if isinstance(value, Time):
            self.meta["start_time"] = value[0]
            self.meta["end_time"] = value[-1]
        elif isinstance(current_times, u.Quantity) and isinstance(old_start, Time) and isinstance(old_end, Time):
            self.meta["start_time"] = old_start + (value[0] - current_times[0])
            self.meta["end_time"] = old_end + (value[-1] - current_times[-1])
        else:
            self.meta["start_time"] = value[0]
            self.meta["end_time"] = value[-1]

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
