from matplotlib import pyplot as plt
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, date2num
from matplotlib.image import NonUniformImage

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


class _TimeAxisMixin:
    def _setup_time_axis(self, axes):
        """
        Apply `~matplotlib.dates.ConciseDateFormatter` to the x-axis.
        """
        locator = AutoDateLocator()
        formatter = ConciseDateFormatter(locator)
        axes.xaxis.set_major_locator(locator)
        axes.xaxis.set_major_formatter(formatter)
        axes.set_xlabel(f"Time ({self.times.scale})")


class PcolormeshPlotMixin(_TimeAxisMixin):
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

        with time_support(), quantity_support():
            # Pin existing converters to avoid warnings when re-plotting on shared axes.
            converter_y = _get_axis_converter(axes.yaxis)
            if converter_y is not None and not getattr(axes.yaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.yaxis, converter_y)

            converter_x = _get_axis_converter(axes.xaxis)
            if converter_x is not None and not getattr(axes.xaxis, "_converter_is_explicit", False):
                _set_axis_converter(axes.xaxis, converter_x)

            times_datetime = self.times.datetime
            axes.plot(times_datetime[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            if self.times.shape[0] == self.data.shape[0] and self.frequencies.shape[0] == self.data.shape[1]:
                ret = axes.pcolormesh(times_datetime, self.frequencies, data, shading="auto", **kwargs)
            else:
                ret = axes.pcolormesh(times_datetime, self.frequencies, data[:-1, :-1], shading="auto", **kwargs)
            axes.set_xlim(times_datetime[0], times_datetime[-1])

        self._setup_time_axis(axes)

        # Set current axes/image if pyplot is being used (makes colorbar work)
        for i in plt.get_fignums():
            if axes in plt.figure(i).axes:
                plt.sca(axes)
                plt.sci(ret)
        return ret


class NonUniformImagePlotMixin(_TimeAxisMixin):
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

            times_datetime = self.times.datetime
            times_num = date2num(times_datetime)
            axes.plot(times_datetime[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            im = NonUniformImage(axes, interpolation="none", **kwargs)
            im.set_data(times_num, frequencies, self.data)
            axes.add_image(im)
            axes.set_xlim(times_datetime[0], times_datetime[-1])
            axes.set_ylim(frequencies[0], frequencies[-1])

        self._setup_time_axis(axes)
