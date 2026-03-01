import numpy as np
from sunpy.net import attrs as a
from sunpy.time import parse_time
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

    @property
    def frequencies(self):
        """
        The frequencies of the spectrogram.
        """
        return self.meta["freqs"]

    def slice(self, time=None, freq=None):
        '''
        times = [t0, t1, t2, t3, t4, t5]
        freqs = [f0, f1, f2, f3, f4]

        Before slice method (manual slicing):
        sliced_times = times[1:5]
        sliced_freqs = freqs[1:4]
        sliced_data = data[1:5, 1:4]

        After slice method:
        sliced_data = slice(time=(t1, t4), freq=(f1, f3))
        '''
        times = self.times
        freqs = self.frequencies

        if time is not None:
            t_start, t_end = time
            if not isinstance(t_start, Time):
                t_start = parse_time(t_start)
            if not isinstance(t_end, Time):
                t_end = parse_time(t_end)
            time_mask = (times >= t_start) & (times <= t_end)
        else:
            time_mask = np.ones(len(times), dtype=bool)

        if freq is not None:
            f_min, f_max = freq
            if hasattr(f_min, "unit"):
                f_min = f_min.to(freqs.unit)
            if hasattr(f_max, "unit"):
                f_max = f_max.to(freqs.unit)
            freq_mask = (freqs >= f_min) & (freqs <= f_max)
        else:
            freq_mask = np.ones(len(freqs), dtype=bool)

        sliced_data = self.data[np.ix_(time_mask, freq_mask)]
        sliced_times = times[time_mask]
        sliced_freqs = freqs[freq_mask]

        new_meta = dict(self.meta)
        new_meta["times"] = sliced_times
        new_meta["freqs"] = sliced_freqs
        new_meta["start_time"] = sliced_times[0]
        new_meta["end_time"] = sliced_times[-1]
        new_meta["wavelength"] = a.Wavelength(sliced_freqs.min(), sliced_freqs.max())

        return self.__class__(sliced_data, new_meta)

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
