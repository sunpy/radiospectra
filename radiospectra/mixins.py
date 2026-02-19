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
        from matplotlib import pyplot as plt

        from astropy.visualization import time_support

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
        with time_support():
            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            if self.times.shape[0] == self.data.shape[0] and self.frequencies.shape[0] == self.data.shape[1]:
                ret = axes.pcolormesh(self.times, self.frequencies.value, data, shading="auto", **kwargs)
            else:
                ret = axes.pcolormesh(self.times, self.frequencies.value, data[:-1, :-1], shading="auto", **kwargs)
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
        from matplotlib import pyplot as plt
        from matplotlib.image import NonUniformImage

        from astropy.visualization import time_support

        if axes is None:
            fig, axes = plt.subplots()

        with time_support():
            axes.plot(self.times[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
            im = NonUniformImage(axes, interpolation="none", **kwargs)
            im.set_data(axes.convert_xunits(self.times), self.frequencies.value, self.data)
            axes.add_image(im)
            axes.set_xlim(self.times[0], self.times[-1])
            axes.set_ylim(self.frequencies.value[0], self.frequencies.value[-1])
