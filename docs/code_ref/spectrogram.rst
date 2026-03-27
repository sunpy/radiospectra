`radiospectra.spectrogram`
==========================

The `radiospectra.spectrogram` module provides classes and utilities for working with dynamic solar radio spectrograms.

Visualizing Spectrograms
------------------------

All spectrogram objects in ``radiospectra`` inherit from :class:`~radiospectra.spectrogram.GenericSpectrogram`, which provides a :meth:`~radiospectra.spectrogram.GenericSpectrogram.peek` method for quick-look visualization.

The ``peek()`` method creates a new figure and plots the spectrogram with sensible defaults, including an optional colorbar.

.. plot::
    :include-source:

    from radiospectra.spectrogram import Spectrogram
    import radiospectra.net
    from sunpy.net import Fido, attrs as a

    # Search and download data
    query = Fido.search(a.Time('2021/05/07 00:00', '2021/05/07 01:00'), a.Instrument.eovsa)
    files = Fido.fetch(query)

    # Create spectrogram and peek
    spec = Spectrogram(files[0])
    spec.peek()

.. automodapi:: radiospectra.spectrogram
