def _times_utc_datetime(times):
    """
    Convert time values to UTC before exposing datetimes, when supported.
    """
    if hasattr(times, "utc"):
        times = times.utc
    return times.datetime


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
        import matplotlib.dates as mdates
        from matplotlib import pyplot as plt

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

        times = _times_utc_datetime(self.times)
        axes.set_title(title)
        axes.plot(times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
        if self.times.shape[0] == self.data.shape[0] and self.frequencies.shape[0] == self.data.shape[1]:
            ret = axes.pcolormesh(times, self.frequencies.value, data, shading="auto", **kwargs)
        else:
            ret = axes.pcolormesh(times, self.frequencies.value, data[:-1, :-1], shading="auto", **kwargs)
        axes.set_xlim(times[0], times[-1])
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        axes.xaxis.set_major_locator(locator)
        axes.xaxis.set_major_formatter(formatter)
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
        import matplotlib.dates as mdates
        from matplotlib import pyplot as plt
        from matplotlib.image import NonUniformImage

        if axes is None:
            fig, axes = plt.subplots()

        times = _times_utc_datetime(self.times)
        im = NonUniformImage(axes, interpolation="none", **kwargs)
        im.set_data(mdates.date2num(times), self.frequencies.value, self.data)
        axes.add_image(im)
