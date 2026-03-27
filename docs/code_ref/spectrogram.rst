`radiospectra.spectrogram`
==========================

The `radiospectra.spectrogram` module provides classes and utilities for working with dynamic solar radio spectrograms.

Visualizing Spectrograms
------------------------

All spectrogram objects in ``radiospectra`` inherit from :class:`~radiospectra.spectrogram.GenericSpectrogram`, which provides a :meth:`~radiospectra.spectrogram.GenericSpectrogram.peek` method for quick-look visualization.

The ``peek()`` method creates a new figure and plots the spectrogram with sensible defaults, including an optional colorbar.

.. plot::
    :include-source:

    import numpy as np
    import astropy.units as u
    from astropy.time import Time
    from radiospectra.spectrogram import GenericSpectrogram

    # Create artificial spectrogram data
    times = Time("2021-01-01T00:00:00") + np.arange(100) * u.min
    freqs = np.linspace(10, 100, 50) * u.MHz
    data = np.random.rand(50, 100)

    # Define minimal metadata
    meta = {
        "observatory": "Example Data",
        "instrument": "Mock Instrument",
        "detector": "Mock Detector",
        "start_time": times[0],
        "end_time": times[-1],
        "wavelength": u.Quantity([1, 10], unit=u.m),
        "times": times,
        "freqs": freqs,
    }

    # Instantiate and peek
    spec = GenericSpectrogram(data, meta)
    spec.peek()

.. automodapi:: radiospectra.spectrogram
