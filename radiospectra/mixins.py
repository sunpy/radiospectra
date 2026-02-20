from matplotlib import pyplot as plt
from matplotlib.image import NonUniformImage

from astropy import units as u
from astropy.visualization import time_support


def _get_axis_converter(axis):
    """Safe method to get axis converter for older and newer MPL versions."""
    try:
        return axis.get_converter()
    except AttributeError:
        try:
            return axis.converter
        except AttributeError:
            return None


def _frequency_values_for_axes(axes, frequencies):
    """
    Convert frequencies to the unit already used on the axes when available.
    """
    if not hasattr(frequencies, "unit"):
        return frequencies, None

    target_unit = None
    if axes.has_data():
        target_unit = getattr(axes, "_radiospectra_frequency_unit", None)
        if target_unit is None:
            target_unit = axes.yaxis.get_units()
        if target_unit is not None:
            try:
                target_unit = u.Unit(target_unit)
            except (TypeError, ValueError):
                target_unit = None

    if target_unit is None:
        target_unit = frequencies.unit
    try:
        frequency_values = frequencies.to_value(target_unit)
    except u.UnitConversionError:
        target_unit = frequencies.unit
        frequency_values = frequencies.value
    return frequency_values, target_unit


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

        plot_frequencies, plot_frequency_unit = _frequency_values_for_axes(axes, self.frequencies)
        if plot_frequency_unit is not None:
            axes._radiospectra_frequency_unit = plot_frequency_unit
            axes.set_ylabel(f"Frequency [{plot_frequency_unit.to_string()}]")

        axes.set_title(title)
        with time_support():
            # Pin existing converter to avoid warnings when re-plotting with different units
            converter = _get_axis_converter(axes.xaxis)
            if converter is not None:
                axes.xaxis.set_converter(converter)

            axes.plot(self.times[[0, -1]], [plot_frequencies[0], plot_frequencies[-1]], linestyle="None", marker="None")
            if self.times.shape[0] == self.data.shape[0] and self.frequencies.shape[0] == self.data.shape[1]:
                ret = axes.pcolormesh(self.times, plot_frequencies, data, shading="auto", **kwargs)
            else:
                ret = axes.pcolormesh(self.times, plot_frequencies, data[:-1, :-1], shading="auto", **kwargs)
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

        plot_frequencies, plot_frequency_unit = _frequency_values_for_axes(axes, self.frequencies)
        if plot_frequency_unit is not None:
            axes._radiospectra_frequency_unit = plot_frequency_unit
            axes.set_ylabel(f"Frequency [{plot_frequency_unit.to_string()}]")

        with time_support():
            # Pin existing converter to avoid warnings when re-plotting with different units
            converter = _get_axis_converter(axes.xaxis)
            if converter is not None:
                axes.xaxis.set_converter(converter)

            axes.plot(self.times[[0, -1]], [plot_frequencies[0], plot_frequencies[-1]], linestyle="None", marker="None")
            im = NonUniformImage(axes, interpolation="none", **kwargs)
            im.set_data(axes.convert_xunits(self.times), plot_frequencies, self.data)
            axes.add_image(im)
            axes.set_xlim(self.times[0], self.times[-1])
            axes.set_ylim(plot_frequencies[0], plot_frequencies[-1])
