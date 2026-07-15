import ndcube

import astropy.units as u
from astropy.coordinates import SpectralCoord
from astropy.time import Time

from radiospectra.exceptions import SpectraMetaValidationError
from radiospectra.mixins import NonUniformImagePlotMixin, PcolormeshPlotMixin
from radiospectra.utils import build_spectrogram_wcs

__all__ = ["GenericSpectrogram"]


class GenericSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin, ndcube.NDCube):
    """
    Base spectrogram class backed by `ndcube.NDCube`.

    Attributes
    ----------
    meta : `dict-like`
        Metadata for the spectrogram.
    data : `numpy.ndarray`
        The spectrogram data itself is a 2D array.
    """

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "is_datasource_for"):
            cls._registry[cls] = cls.is_datasource_for

    def __init__(self, data, meta, wcs=None, **kwargs):
        if wcs is None:
            self._validate_meta(meta)
            wcs = build_spectrogram_wcs(self._time_axis_from_meta(meta), meta["freqs"]).wcs
        super().__init__(data=data, wcs=wcs, meta=meta, **kwargs)

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
        return self.axis_world_coords("time")[0]

    @property
    def frequencies(self):
        """
        The frequencies of the spectrogram.
        """
        return self.axis_world_coords("em.freq")[0]

    def _validate_meta(self, meta):
        msg = "Spectrogram coordinate units for {} axis not present in metadata."
        err_message = []
        for ax in ["times", "freqs"]:
            if meta.get(ax) is None:
                err_message.append(msg.format(ax))
        if err_message:
            raise SpectraMetaValidationError("\n".join(err_message))

    @staticmethod
    def _time_axis_from_meta(meta):
        times = meta["times"]
        if isinstance(times, Time):
            return times
        if "start_time" in meta:
            if isinstance(times, u.Quantity):
                return meta["start_time"] + times
            return meta["start_time"] + times * u.s
        return Time(times)

    def crop_time(self, start_time, end_time):
        """
        Crop the spectrogram by time.
        """
        return self.crop((start_time, None), (end_time, None))

    def crop_freq(self, low_freq, high_freq):
        """
        Crop the spectrogram by frequency.
        """
        if not isinstance(low_freq, SpectralCoord):
            low_freq = SpectralCoord(low_freq)
        if not isinstance(high_freq, SpectralCoord):
            high_freq = SpectralCoord(high_freq)

        return self.crop((None, low_freq), (None, high_freq))

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}"
            f" {self.wavelength.min} - {self.wavelength.max},"
            f" {self.start_time.isot} to {self.end_time.isot}>"
        )
