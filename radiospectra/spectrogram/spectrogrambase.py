import copy

import numpy as np

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
    @classmethod
    def join_many(cls, spectrograms, maxgap=None, fill_gaps=True):
        """
        Join a sequence of spectrograms along the time axis.

        Parameters
        ----------
        spectrograms : sequence of GenericSpectrogram
            The spectrograms to join.
        maxgap : None or `astropy.time.TimeDelta` or `astropy.units.Quantity`
            Maximum allowed gap between spectrograms. If None, any gap is allowed.
            If 0, gaps are not allowed.
        fill_gaps : bool
            If True, fill gaps by repeating the last time column (historic behavior).

        Returns
        -------
        GenericSpectrogram
            A new spectrogram with concatenated data and updated metadata.

        Raises
        ------
        ValueError
            If frequency axes mismatch or if a gap exceeds maxgap.
        """
        import astropy.units as u
        from astropy.time import Time, TimeDelta

        specs = list(spectrograms)
        if len(specs) == 0:
            raise ValueError("No spectrograms provided.")
        if len(specs) == 1:
            return specs[0]

        # Sort by start time
        specs = sort_spectrograms(specs)

        # Normalize maxgap
        if maxgap is None:
            maxgap_td = None
        elif maxgap == 0:
            maxgap_td = TimeDelta(0 * u.s)
        else:
            # Accept TimeDelta or Quantity
            if isinstance(maxgap, TimeDelta):
                maxgap_td = maxgap
            else:
                maxgap_td = TimeDelta(maxgap)

        base = specs[0]
        out_data = np.array(base.data, copy=True)
        out_times = base.times
        out_freqs = base.frequencies

        def _freqs_equal(a, b):
            # robust compare for arrays/quantities
            try:
                # Convert to MHz for strict comparison if units differ but are compatible
                if hasattr(a, "unit") and hasattr(b, "unit"):
                    return (len(a) == len(b)) and np.allclose(
                        a.to_value(u.MHz), b.to_value(u.MHz)
                    )
                return (len(a) == len(b)) and np.all(a == b)
            except Exception:
                return False

        for nxt in specs[1:]:
            if not _freqs_equal(out_freqs, nxt.frequencies):
                raise ValueError("Cannot join spectrograms with different frequency axes.")

            # Determine cadence from current output timeline
            if len(out_times) < 2:
                raise ValueError("Not enough time samples to infer cadence.")

            # Calculate cadence carefully
            try:
                # Use value directly if possible for speed
                diffs = out_times[1:] - out_times[:-1]
                if hasattr(diffs, "to_value"):
                     dt_sec = np.median(diffs.to_value(u.s))
                else:
                     dt_sec = np.median(diffs)
                dt_td = TimeDelta(dt_sec * u.s)
            except Exception:
                # Fallback
                t_unix = out_times.to_value("unix")
                dt_sec = np.median(np.diff(t_unix))
                dt_td = TimeDelta(dt_sec * u.s)

            # Compute gap between expected next sample and nxt start
            expected_next = out_times[-1] + dt_td
            gap = nxt.times[0] - expected_next

            # Handle overlap
            if gap <= TimeDelta(0 * u.s):
                mask = nxt.times > out_times[-1]
                nxt_times = nxt.times[mask]
                nxt_data = nxt.data[:, mask]
            else:
                if maxgap_td is not None and gap > maxgap_td:
                    raise ValueError(f"Too large gap. {gap} > {maxgap_td}")

                if fill_gaps:
                    n_missing = int(np.round((gap / dt_td).to_value(u.one)))
                    if n_missing > 0:
                        fill_times = out_times[-1] + dt_td * np.arange(1, n_missing + 1)

                        last_col = out_data[:, [-1]]
                        fill_block = np.repeat(last_col, n_missing, axis=1)
                        out_data = np.concatenate([out_data, fill_block], axis=1)

                        # Concatenate times via list to be robust
                        if not isinstance(fill_times, Time):
                             fill_times = Time(fill_times)
                        out_times = Time(list(out_times) + list(fill_times))

                nxt_times = nxt.times
                nxt_data = nxt.data

            # Append nxt
            if len(nxt_times) > 0:
                out_data = np.concatenate([out_data, nxt_data], axis=1)

                if not isinstance(nxt_times, Time):
                     nxt_times = Time(nxt_times)
                out_times = Time(list(out_times) + list(nxt_times))

        # Build new meta (copy base meta and update time-related fields)
        new_meta = copy.deepcopy(base.meta)
        new_meta["times"] = out_times
        new_meta["start_time"] = out_times[0]
        new_meta["end_time"] = out_times[-1]
        # freqs kept from base

        return base.__class__(out_data, new_meta)


def sort_spectrograms(specs):
    return sorted(specs, key=lambda s: s.meta["start_time"])
