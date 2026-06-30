import abc

from ndcube.meta import NDMeta, NDMetaABC

from astropy.time import Time
from astropy.units import Quantity, Unit

__all__ = ["SpectrogramMetaABC", "SpectrogramMeta"]


class SpectrogramMetaABC(NDMetaABC):
    """
    Abstract base class for all spectrogram metadata.
    """

    # Identification
    @property
    @abc.abstractmethod
    def instrument(self) -> str:
        """Name of the instrument."""
        pass

    @property
    @abc.abstractmethod
    def observatory(self) -> str:
        """Name of the observatory."""
        pass

    @property
    @abc.abstractmethod
    def detector(self) -> str:
        """Name of the detector."""
        pass

    @property
    @abc.abstractmethod
    def processing_level(self) -> str | None:
        """The level to which the data has been processed."""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str | None:
        """The data version."""
        pass

    @property
    @abc.abstractmethod
    def source_filename(self) -> str | None:
        """The source filename."""
        pass

    # Time
    @property
    @abc.abstractmethod
    def date_start(self) -> Time:
        """Start of the observation"""
        pass

    @property
    @abc.abstractmethod
    def date_end(self) -> Time:
        """End of the observation"""
        pass

    @property
    @abc.abstractmethod
    def temporal_resolution(self) -> Quantity:
        pass

    # Frequency
    @property
    @abc.abstractmethod
    def frequency_range(self) -> Quantity:
        """Frequency range of observation"""
        pass

    @property
    @abc.abstractmethod
    def frequency_resolution(self) -> Quantity:
        pass

    # Calibration and signal
    @property
    @abc.abstractmethod
    def data_units(self) -> Unit:
        """Unit for the data"""
        pass

    @property
    @abc.abstractmethod
    def calibration_state(self) -> str | None:
        """Calibration state."""
        pass

    @property
    @abc.abstractmethod
    def polarisation(self) -> str | None:
        """Stokes parameter convention or polarization."""
        pass

    # Quality
    @property
    @abc.abstractmethod
    def data_mask(self):
        """Data mask."""
        pass

    # Position
    @property
    @abc.abstractmethod
    def observer_location(self):
        """Observer location."""
        pass


class SpectrogramMeta(NDMeta, SpectrogramMetaABC):
    """
    Base class for radio spectrogram metadata.

    Backed by `ndcube.meta.NDMeta` (a `dict` subclass).
    """

    @property
    def instrument(self):
        return self["instrument"]

    @property
    def observatory(self):
        return self["observatory"]

    @property
    def detector(self):
        return self["detector"]

    @property
    def date_start(self):
        return self["start_time"]

    @property
    def date_end(self):
        return self["end_time"]

    @property
    def processing_level(self):
        return self.get("processing_level")

    @property
    def version(self):
        return self.get("version")

    @property
    def source_filename(self):
        return self.get("source_filename")

    @property
    def temporal_resolution(self):
        return self.get("temporal_resolution")

    @property
    def frequency_range(self):
        return self.get("wavelength")

    @property
    def frequency_resolution(self):
        return self.get("frequency_resolution")

    @property
    def data_units(self):
        return self.get("data_units")

    @property
    def calibration_state(self):
        return self.get("calibration_state")

    @property
    def polarisation(self):
        return self.get("polarisation")

    @property
    def data_mask(self):
        return self.get("data_mask")

    @property
    def observer_location(self):
        return self.get("observer_location")
