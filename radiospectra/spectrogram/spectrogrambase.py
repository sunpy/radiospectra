import ndcube
import numpy as np

import astropy.units as u
from astropy.coordinates import SpectralCoord
from astropy.time import Time

from radiospectra.exceptions import SpectraMetaValidationError
from radiospectra.mixins import NonUniformImagePlotMixin, PcolormeshPlotMixin
from radiospectra.spectrogram.meta import SpectrogramMeta
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
        if not isinstance(meta, SpectrogramMeta):
            meta = SpectrogramMeta(meta)

        if wcs is None:
            self._validate_meta(meta)
            wcs = build_spectrogram_wcs(self._time_axis_from_meta(meta), meta["freqs"]).wcs
        super().__init__(data=data, wcs=wcs, meta=meta, **kwargs)

    @property
    def observatory(self):
        """
        The name of the observatory which recorded the spectrogram.
        """
        val = self.meta.get("observatory")
        return val.upper() if val else None

    @property
    def instrument(self):
        """
        The name of the instrument which recorded the spectrogram.
        """
        val = self.meta.get("instrument")
        return val.upper() if val else None

    @property
    def detector(self):
        """
        The detector which recorded the spectrogram.
        """
        val = self.meta.get("detector")
        return val.upper() if val else None

    @property
    def receiver(self):
        """
        The receiver which recorded the spectrogram.
        """
        val = self.meta.get("receiver")
        return val.upper() if val else None

    @property
    def background(self):
        """
        The background subtracted from the data.
        """
        return self.meta.get("background")

    @property
    def start_time(self):
        """
        The start time of the spectrogram.
        """
        return self.meta.get("start_time")

    @property
    def end_time(self):
        """
        The end time of the spectrogram.
        """
        return self.meta.get("end_time")

    @property
    def wavelength(self):
        """
        The wavelength range of the spectrogram.
        """
        return self.meta.get("wavelength")

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

        Parameters
        ----------
        start_time : `astropy.time.Time`
            The start time of the crop.
        end_time : `astropy.time.Time`
            The end time of the crop.

        Returns
        -------
        `radiospectra.spectrogram.GenericSpectrogram`
            The cropped spectrogram.
        """
        start_time = Time(start_time)
        end_time = Time(end_time)
        return self.crop((start_time, None), (end_time, None))

    def crop_freq(self, low_freq, high_freq):
        """
        Crop the spectrogram by frequency.

        Parameters
        ----------
        low_freq : `astropy.units.Quantity` or `astropy.coordinates.SpectralCoord`
            The low frequency of the crop.
        high_freq : `astropy.units.Quantity` or `astropy.coordinates.SpectralCoord`
            The high frequency of the crop.

        Returns
        -------
        `radiospectra.spectrogram.GenericSpectrogram`
            The cropped spectrogram.
        """
        if not isinstance(low_freq, SpectralCoord):
            low_freq = SpectralCoord(low_freq)
        if not isinstance(high_freq, SpectralCoord):
            high_freq = SpectralCoord(high_freq)

        return self.crop((None, low_freq), (None, high_freq))

    def time_profile(self, frequency):
        """
        Extract a time profile (intensity vs time) at a given frequency.

        Parameters
        ----------
        frequency : `astropy.units.Quantity`
            The frequency to extract the time profile at.

        Returns
        -------
        `radiospectra.spectrogram.GenericSpectrogram`
            The 1D time profile.
        """

        for i, axis_types in enumerate(self.array_axis_physical_types):
            if "em.freq" in axis_types:
                freqs = self.frequencies
                if len(freqs) == 0:
                    idx = 0
                elif freqs[0] < freqs[-1]:
                    idx = np.searchsorted(freqs, frequency)
                else:
                    idx = len(freqs) - np.searchsorted(freqs[::-1], frequency)
                idx = int(np.clip(idx, 0, len(freqs) - 1))
                item = [slice(None)] * len(self.shape)
                item[i] = idx
                return self[tuple(item)]
        raise ValueError("Spectrogram does not have a frequency axis")

    def line_profile(self, time):
        """
        Extract a line profile (intensity vs frequency) at a given time.

        Parameters
        ----------
        time : `astropy.time.Time` or `str`
            The time to extract the line profile at.

        Returns
        -------
        `radiospectra.spectrogram.GenericSpectrogram`
            The 1D line profile.
        """
        if isinstance(time, str):
            time = Time(time)
        for i, axis_types in enumerate(self.array_axis_physical_types):
            if "time" in axis_types:
                times = self.times
                if len(times) == 0:
                    idx = 0
                else:
                    idx = np.searchsorted(times, time)
                idx = int(np.clip(idx, 0, len(times) - 1))
                item = [slice(None)] * len(self.shape)
                item[i] = idx
                return self[tuple(item)]
        raise ValueError("Spectrogram does not have a time axis")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}"
            f" {self.wavelength.min} - {self.wavelength.max},"
            f" {self.start_time.isot} to {self.end_time.isot}>"
        )
