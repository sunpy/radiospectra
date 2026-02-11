import numpy as np

__all__ = ["Spectrum"]


class Spectrum(np.ndarray):
    """
    Class representing a 1 dimensional spectrum.

    Attributes
    ----------
    freq_axis : `~numpy.ndarray`
        One-dimensional array with the frequency values.
    data : `~numpy.ndarray`
        One-dimensional array which the intensity at a particular frequency at every data-point.

    Examples
    --------
    >>> from radiospectra.spectrum import Spectrum
    >>> import numpy as np
    >>> data = np.linspace(1, 100, 100)
    >>> freq_axis = np.linspace(0, 10, 100)
    >>> spec = Spectrum(data, freq_axis)
    >>> spec.peek()   # doctest: +SKIP
    """

    def __new__(cls, data, *args, **kwargs):
        return np.asarray(data).view(cls)
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        new_inputs = []
        for x in inputs:
            if isinstance(x, Spectrum):
                new_inputs.append(x.view(np.ndarray))
            else:
                new_inputs.append(x)

        result = getattr(ufunc, method)(*new_inputs, **kwargs)

        if isinstance(result, tuple):
            return tuple(self._wrap_result(r) for r in result)

        return self._wrap_result(result)

    def _wrap_result(self, result):
        if isinstance(result, np.ndarray):
            result = result.view(Spectrum)
            if hasattr(self, "freq_axis"):
                result.freq_axis = self.freq_axis.copy()
        return result

    def __init__(self, data, freq_axis):
        if np.shape(data)[0] != np.shape(freq_axis)[0]:
            raise ValueError("Dimensions of data and frequency axis do not match")
        self.freq_axis = freq_axis

    def plot(self, axes=None, **matplot_args):
        """
        Plot spectrum onto current axes.

        Parameters
        ----------
        axes : `~matplotlib.axes.Axes` or `None`
            If provided the spectrum will be plotted on the given axes.
            Else the current `matplotlib` axes will be used.
        **matplot_args : dict
            Any additional plot arguments that should be used
            when plotting.

        Returns
        -------
         `~matplotlib.axes.Axes`
            The plot axes.
        """
        from matplotlib import pyplot as plt

        # Get current axes
        if not axes:
            axes = plt.gca()
        params = {}
        params.update(matplot_args)
        lines = axes.plot(self.freq_axis, self, **params)
        return lines

    def peek(self, **matplot_args):
        """
        Plot spectrum onto a new figure.
        Parameters
        ----------
        **matplot_args : dict
            Any additional plot arguments that should be used when plotting.

        Returns
        -------
        `~matplotlib.Figure`
            A plot figure.

        Examples
        --------
        >>> from radiospectra.spectrum import Spectrum
        >>> import numpy as np
        >>> spec = Spectrum(np.linspace(1, 100, 100), np.linspace(0, 10, 100))
        >>> spec.peek()  # doctest: +SKIP
        """
        from matplotlib import pyplot as plt

        figure = plt.figure()
        self.plot(**matplot_args)
        figure.show()
        return figure
