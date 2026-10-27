from matplotlib import pyplot as plt
from matplotlib.image import NonUniformImage

from astropy.visualization import quantity_support, time_support

__all__ = ["PcolormeshPlotMixin", "NonUniformImagePlotMixin"]


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


def _shared_x_limits(axes):
    """
    Return the current shared x limits if any shared sibling has plotted data.
    """
    siblings = axes.get_shared_x_axes().get_siblings(axes)
    if any(sibling.has_data() for sibling in siblings):
        return axes.get_xlim()
    return None


def _set_x_limits(axes, x_values, previous_limits):
    """
    Set x limits, expanding previous shared-axis limits when present.
    """
    if previous_limits is None:
        axes.set_xlim(x_values[0], x_values[-1])
        return

    converted_limits = axes.convert_xunits(x_values)
    lower = min(previous_limits[0], previous_limits[1], converted_limits[0], converted_limits[-1])
    upper = max(previous_limits[0], previous_limits[1], converted_limits[0], converted_limits[-1])
    if previous_limits[0] > previous_limits[1]:
        lower, upper = upper, lower
    axes.set_xlim(lower, upper)


class PcolormeshPlotMixin:
    """
    Class provides plotting functions using `~matplotlib.pyplot.pcolormesh`.
    """

    def plot(self, axes=None, **kwargs):
        """
        Plot the spectrogram.

        Parameters
        ----------
        axes : `matplotlib.axes.Axes`, optional
            The axes where the plot will be added.
        kwargs :
            Arguments pass to the plot call `~matplotlib.pyplot.pcolormesh`.

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

            previous_x_limits = _shared_x_limits(axes)

            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            if self.times.shape[0] == self.data.shape[0] and self.frequencies.shape[0] == self.data.shape[1]:
                ret = axes.pcolormesh(self.times, self.frequencies, data, shading="auto", **kwargs)
            else:
                ret = axes.pcolormesh(self.times, self.frequencies, data[:-1, :-1], shading="auto", **kwargs)
            _set_x_limits(axes, self.times[[0, -1]], previous_x_limits)
            fig.autofmt_xdate()

        # Set current axes/image if pyplot is being used (makes colorbar work)
        for i in plt.get_fignums():
            if axes in plt.figure(i).axes:
                plt.sca(axes)
                plt.sci(ret)
        return ret


class NonUniformImagePlotMixin:
    """
    Class provides plotting functions using `~matplotlib.image.NonUniformImage`.

    Parameters
    ----------
    axes : `matplotlib.axes.Axes`, optional
        The axes where the plot will be added.
    kwargs :
        Arguments pass to the plot call `~matplotlib.image.NonUniformImage`.
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

            previous_x_limits = _shared_x_limits(axes)

            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            im = NonUniformImage(axes, interpolation="none", **kwargs)
            im.set_data(axes.convert_xunits(self.times), frequencies, self.data)
            axes.add_image(im)
            _set_x_limits(axes, self.times[[0, -1]], previous_x_limits)
            axes.set_ylim(frequencies[0], frequencies[-1])
