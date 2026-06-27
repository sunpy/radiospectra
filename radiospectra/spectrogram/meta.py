import abc

from ndcube.meta import NDMeta, NDMetaABC

__all__ = ["SpectrogramMetaABC", "SpectrogramMeta"]


class SpectrogramMetaABC(NDMetaABC):
    """
    Abstract base class for all spectrogram metadata.
    Maps to LC Radio Workshop metadata requirements.
    """

    # Identification
    @property
    @abc.abstractmethod
    def instrument(self):
        pass

    @property
    @abc.abstractmethod
    def observatory(self):
        pass

    @property
    @abc.abstractmethod
    def detector(self):
        pass

    @property
    @abc.abstractmethod
    def processing_level(self):
        """The level to which the data has been processed."""
        pass

    @property
    @abc.abstractmethod
    def version(self):
        """The data version."""
        pass

    @property
    @abc.abstractmethod
    def source_filename(self):
        """The source filename."""
        pass

    # 2.2 Time
    @property
    @abc.abstractmethod
    def date_start(self):
        """The start time of the observation."""
        pass

    @property
    @abc.abstractmethod
    def date_end(self):
        """The end time of the observation."""
        pass

    @property
    @abc.abstractmethod
    def temporal_resolution(self):
        """Temporal resolution, both raw and current."""
        pass

    # Frequency
    @property
    @abc.abstractmethod
    def frequency_range(self):
        """Start and end frequencies of the observation."""
        pass

    @property
    @abc.abstractmethod
    def frequency_resolution(self):
        """Frequency resolution, both raw and current."""
        pass

    # 2.4 Calibration and signal
    @property
    @abc.abstractmethod
    def data_units(self):
        """Units of the data (e.g. arbitrary, V^2/Hz, sfu, dB)."""
        pass

    @property
    @abc.abstractmethod
    def calibration_state(self):
        """Calibration state."""
        pass

    @property
    @abc.abstractmethod
    def polarisation(self):
        """Stokes parameter convention or polarization."""
        pass

    # 2.5 Quality
    @property
    @abc.abstractmethod
    def data_mask(self):
        """Data mask."""
        pass

    # 2.6 Position
    @property
    @abc.abstractmethod
    def observer_location(self):
        """Observer location."""
        pass


class SpectrogramMeta(NDMeta, SpectrogramMetaABC):
    """
    Base class for radio spectrogram metadata.

    Backed by `ndcube.meta.NDMeta` (a `dict` subclass).
    Properties do key lookups with sensible defaults for optional fields.
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
