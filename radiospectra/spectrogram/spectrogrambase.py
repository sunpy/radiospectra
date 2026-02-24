import numpy as np

import astropy.units as u
from astropy.time import Time
from astropy.wcs import WCS
from ndcube import NDCube

from radiospectra.exceptions import SpectraMetaValidationError
from radiospectra.mixins import NonUniformImagePlotMixin, PcolormeshPlotMixin

__all__ = ["GenericSpectrogram"]


def _is_wcs_like(value):
    return hasattr(value, "pixel_n_dim") and hasattr(value, "world_n_dim")


def _build_pixel_index_wcs(data):
    ndim = getattr(data, "ndim", np.ndim(data))
    wcs = WCS(naxis=ndim)
    wcs.wcs.crpix = [1.0] * ndim
    wcs.wcs.cdelt = [1.0] * ndim
    wcs.wcs.crval = [0.0] * ndim
    wcs.wcs.ctype = ["PIXEL"] * ndim
    return wcs


def _coerce_extra_coord_values(name, values, meta):
    if isinstance(values, (Time, u.Quantity)):
        return values

    if isinstance(values, (list, tuple, np.ndarray)):
        arr = np.asarray(values)
        if np.issubdtype(arr.dtype, np.number):
            if name == "time":
                if hasattr(meta, "get") and isinstance(meta.get("start_time"), Time):
                    return meta["start_time"] + arr * u.s
                return None
            return arr * u.one

    return None


class GenericSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin, NDCube):
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

    def __init__(
        self,
        data,
        wcs=None,
        uncertainty=None,
        mask=None,
        meta=None,
        unit=None,
        copy=False,
        **kwargs,
    ):
        # Backward compatibility: historically this class accepted (data, meta).
        if meta is None and wcs is not None and not _is_wcs_like(wcs):
            meta = wcs
            wcs = None

        # Accept and process the same keyword names used by newer NDCube APIs
        # without passing unknown keywords to older NDData constructors.
        extra_coords = kwargs.pop("extra_coords", None)
        kwargs.pop("global_coords", None)
        kwargs.pop("psf", None)

        if wcs is None:
            # Coordinate lookup tables are held in extra_coords, so this WCS only
            # provides a stable pixel-index backbone required by NDCube.
            wcs = _build_pixel_index_wcs(data)

        if meta is None:
            meta = {}

        if extra_coords is None and hasattr(meta, "get"):
            extra_coords = []
            times = meta.get("times")
            freqs = meta.get("freqs")
            if times is not None:
                extra_coords.append(("time", 0, times))
            if freqs is not None:
                extra_coords.append(("frequency", 1, freqs))
            if not extra_coords:
                extra_coords = None

        super().__init__(
            data,
            wcs=wcs,
            uncertainty=uncertainty,
            mask=mask,
            meta=meta,
            unit=unit,
            copy=copy,
            **kwargs,
        )

        if extra_coords is not None:
            existing = set(self.extra_coords.keys() or ())
            for name, axis, values in extra_coords:
                if name in existing:
                    continue
                values = _coerce_extra_coord_values(name, values, self.meta)
                if values is None:
                    continue
                self.extra_coords.add(name, axis, values)
                existing.add(name)

        if hasattr(self.meta, "get") and self.meta:
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
        for ax in ["times", "freqs"]:
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
