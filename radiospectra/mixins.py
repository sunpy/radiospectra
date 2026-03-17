import numpy as np
from matplotlib import pyplot as plt
from matplotlib.image import NonUniformImage

from astropy.time import Time
from astropy.visualization import quantity_support, time_support


def _get_axis_converter(axis):
    """
    Safe method to get axis converter for older and newer MPL versions.

    ``axis.get_converter()`` / ``axis.set_converter()`` were added in
    Matplotlib 3.9.  Once the minimum supported Matplotlib version is
    >= 3.9 these helpers can be replaced by direct get/set calls.
    """
    try:
        return axis.get_converter()
    except AttributeError:
        try:
            return axis.converter
        except AttributeError:
            return None


def _set_axis_converter(axis, converter):
    """
    Safe method to set axis converter for older and newer MPL versions.

    See `_get_axis_converter` for version notes.
    """
    try:
        axis.set_converter(converter)
    except AttributeError:
        try:
            axis._set_converter(converter)
            axis._converter_is_explicit = True
        except AttributeError:
            axis.converter = converter


class PcolormeshPlotMixin:
    """
    Class provides plotting functions using `~pcolormesh`.
    """

    @staticmethod
    def _insert_time_gaps(times, data, gap_threshold=None):
        """
        Identify gaps in the time axis and insert NaNs to prevent pcolormesh
        from stretching data across the gaps.

        Parameters
        ----------
        times : `astropy.time.Time`
            The timestamps of the observations.
        data : `numpy.ndarray`
            The intensity data.
        gap_threshold : `float`, optional
            The threshold in seconds above which a time difference is
            considered a gap. If not provided, it defaults to 2.5 times
            the minimum difference between consecutive timestamps.

        Returns
        -------
        new_times : `astropy.time.Time`
            Modified timestamps with gap-fillers.
        new_data : `numpy.ndarray`
            Modified data with NaN rows inserted at gaps.
        """
        times_numeric = times.to_value("unix")
        diffs = np.diff(times_numeric)
        if len(diffs) == 0:
            return times, data

        if gap_threshold is None:
            gap_threshold = 2.5 * np.min(diffs[diffs > 0]) if np.any(diffs > 0) else 1e9

        gap_indices = np.where(diffs > gap_threshold)[0]

        if gap_indices.size == 0:
            return times, data

        if not np.issubdtype(data.dtype, np.floating):
            new_data = data.astype(np.float64)
        else:
            new_data = data.copy()

        new_times_numeric = times_numeric.tolist()
        for idx in reversed(gap_indices):
            gap_time = (times_numeric[idx] + times_numeric[idx + 1]) / 2.0
            new_times_numeric.insert(idx + 1, gap_time)

            null_row = np.full(data.shape[1], np.nan)
            new_data = np.insert(new_data, idx + 1, null_row, axis=0)

        return Time(new_times_numeric, format="unix"), new_data

    def plot(self, axes=None, handle_gaps=True, gap_threshold=None, **kwargs):
        """
        Plot the spectrogram.

        Parameters
        ----------
        axes : `matplotlib.axis.Axes`, optional
            The axes where the plot will be added.
        handle_gaps : `bool`, optional
            If True, automatically detect large time gaps and render
            them as empty space by inserting NaNs. Defaults to True.
        gap_threshold : `float`, optional
            Optional manual threshold in seconds for gap detection.
        kwargs :
            Arguments pass to the plot call `pcolormesh`.

        Returns
        -------
        `matplotlib.collections.QuadMesh`
        """

        if axes is None:
            fig, axes = plt.subplots()
        else:
            fig = axes.get_figure()

        if hasattr(self.data, "value"):
            data = self.data.value
        else:
            data = self.data

        title = f"{self.observatory}, {self.instrument}"
        if self.instrument != self.detector:
            title = f"{title}, {self.detector}"

        axes.set_title(title)

        with time_support(), quantity_support():
            # Pin existing converters to avoid warnings when re-plotting on shared axes.
            converter_y = _get_axis_converter(axes.yaxis)
            if converter_y is not None and not getattr(axes.yaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.yaxis, converter_y)

            converter_x = _get_axis_converter(axes.xaxis)
            if converter_x is not None and not getattr(axes.xaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.xaxis, converter_x)

            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")

            times, data_to_plot = self.times, data
            if handle_gaps:
                times, data_to_plot = self._insert_time_gaps(times, data_to_plot, gap_threshold=gap_threshold)

            if times.shape[0] == data_to_plot.shape[0] and self.frequencies.shape[0] == data_to_plot.shape[1]:
                ret = axes.pcolormesh(times, self.frequencies, data_to_plot, shading="auto", **kwargs)
            else:
                ret = axes.pcolormesh(times, self.frequencies, data_to_plot[:-1, :-1], shading="auto", **kwargs)
            axes.set_xlim(self.times[0], self.times[-1])
            fig.autofmt_xdate()

        # Set current axes/image if pyplot is being used (makes colorbar work)
        for i in plt.get_fignums():
            if axes in plt.figure(i).axes:
                plt.sca(axes)
                plt.sci(ret)
        return ret


class NonUniformImagePlotMixin:
    """
    Class provides plotting functions using `NonUniformImage`.
    """

    def plotim(self, fig=None, axes=None, **kwargs):

        if axes is None:
            fig, axes = plt.subplots()

        with time_support(), quantity_support():
            # Pin existing converters to avoid warnings when re-plotting on shared axes.
            converter_y = _get_axis_converter(axes.yaxis)
            if converter_y is not None and not getattr(axes.yaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.yaxis, converter_y)

            converter_x = _get_axis_converter(axes.xaxis)
            if converter_x is not None and not getattr(axes.xaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.xaxis, converter_x)

            axes.yaxis.update_units(self.frequencies)
            frequencies = axes.yaxis.convert_units(self.frequencies)

            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            im = NonUniformImage(axes, interpolation="none", **kwargs)
            im.set_data(axes.convert_xunits(self.times), frequencies, self.data)
            axes.add_image(im)
            axes.set_xlim(self.times[0], self.times[-1])
            axes.set_ylim(frequencies[0], frequencies[-1])
