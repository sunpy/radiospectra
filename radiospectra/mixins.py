from contextlib import contextmanager

import matplotlib.units as munits
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, DateConverter
from matplotlib.image import NonUniformImage

from astropy.time import Time
from astropy.visualization import quantity_support


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


class ConciseAstropyConverter(munits.ConversionInterface):
    """
    Matplotlib unit converter for `astropy.time.Time` that uses concise date formatting.

    Notes
    -----
    This converter turns times into Matplotlib internal date floats. It does
    not handle leap seconds or nanosecond precision for the entire age of
    the universe.
    """

    @staticmethod
    def axisinfo(unit, axis):
        locator = AutoDateLocator()
        formatter = ConciseDateFormatter(locator)
        return munits.AxisInfo(majloc=locator, majfmt=formatter, label=f"Time ({unit})")

    @staticmethod
    def convert(value, unit, axis):
        if isinstance(value, Time):
            return value.plot_date

        if isinstance(value, (list, tuple, np.ndarray)):
            # If it's already a Time object (could be array-valued), use its plot_date
            if isinstance(value, Time):
                return value.plot_date
            # Otherwise iterate over the sequence
            converted = [v.plot_date if isinstance(v, Time) else v for v in np.asarray(value, dtype=object).flat]

            # Matplotlib dates are floats; let DateConverter handle any remaining datetimes
            converted_val = np.asarray(converted).reshape(np.shape(value))
            return DateConverter.convert(converted_val, unit, axis)

        return DateConverter.convert(value, unit, axis)

    @staticmethod
    def default_units(x, axis):
        if isinstance(x, Time):
            return x.scale.upper()
        return None


@contextmanager
def concise_time_support():
    """
    Context manager to enable concise time formatting for `astropy.time.Time` objects.
    """
    original_converter = munits.registry.get(Time)
    munits.registry[Time] = ConciseAstropyConverter()
    try:
        yield
    finally:
        if original_converter is None:
            del munits.registry[Time]
        else:
            munits.registry[Time] = original_converter


class PcolormeshPlotMixin:
    """
    Class provides plotting functions using `~pcolormesh`.
    """

    def plot(self, axes=None, **kwargs):
        """
        Plot the spectrogram.

        Parameters
        ----------
        axes : `matplotlib.axis.Axes`, optional
            The axes where the plot will be added.
        kwargs :
            Arguments pass to the plot call `pcolormesh`.

        Returns
        -------
        `matplotlib.collections.QuadMesh`
        """

        if axes is None:
            _, axes = plt.subplots()

        if hasattr(self.data, "value"):
            data = self.data.value
        else:
            data = self.data

        title = f"{self.observatory}, {self.instrument}"
        if self.instrument != self.detector:
            title = f"{title}, {self.detector}"

        axes.set_title(title)

        with concise_time_support(), quantity_support():
            # Pin existing converters to avoid warnings when re-plotting on shared axes.
            converter_y = _get_axis_converter(axes.yaxis)
            if converter_y is not None and not getattr(axes.yaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.yaxis, converter_y)

            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            if self.times.shape[0] == self.data.shape[0] and self.frequencies.shape[0] == self.data.shape[1]:
                ret = axes.pcolormesh(self.times, self.frequencies, data, shading="auto", **kwargs)
            else:
                ret = axes.pcolormesh(self.times, self.frequencies, data[:-1, :-1], shading="auto", **kwargs)
            axes.set_xlim(self.times[0], self.times[-1])

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

        with concise_time_support(), quantity_support():
            # Pin existing converters to avoid warnings when re-plotting on shared axes.
            converter_y = _get_axis_converter(axes.yaxis)
            if converter_y is not None and not getattr(axes.yaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.yaxis, converter_y)

            axes.yaxis.update_units(self.frequencies)
            frequencies = axes.yaxis.convert_units(self.frequencies)

            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            im = NonUniformImage(axes, interpolation="none", **kwargs)
            # NonUniformImage does not use the axis converter itself,
            # so we manually convert the explicit input times down to floats.
            times_numeric = axes.xaxis.convert_units(self.times)
            im.set_data(times_numeric, frequencies, self.data)
            axes.add_image(im)
            axes.set_xlim(self.times[0], self.times[-1])
            axes.set_ylim(frequencies[0], frequencies[-1])
