Overview
========

radiospectra is a Python package for reading and working with
solar and heliospheric radio spectrogram data. It provides a
common interface for loading dynamic spectra from multiple
radio instruments and representing them as spectrogram objects.

Spectrogram data are represented using a unified object model,
allowing users to inspect metadata, access intensity data,
and generate visualizations in a consistent way across
different instruments.

Supported Instruments
---------------------

radiospectra currently supports spectrogram data from:

- e-CALLISTO
- Expanded Owens Valley Solar Array (EOVSA)
- Parker Solar Probe FIELDS/RFS
- Radio Solar Telescope Network (RSTN)
- STEREO/WAVES
- Wind/WAVES

Quick Start
-----------

The example below demonstrates how to search, download,
and plot e-CALLISTO spectrogram data.

.. code-block:: python

    import radiospectra.net
    from sunpy.net import Fido, attrs as a
    from radiospectra.spectrogram import Spectrogram
    from radiospectra.net import attrs as ra

    # Search for e-CALLISTO data
    query = Fido.search(
        a.Time('2019/10/05 23:00', '2019/10/06 00:59'),
        a.Instrument('eCALLISTO'),
        ra.Observatory('ALASKA')
    )

    # Download the first result
    downloaded = Fido.fetch(query[0][0])

    # Create a spectrogram object
    spec = Spectrogram(downloaded[0])

    # Plot the spectrogram
    spec.plot()

This workflow:

- Searches the e-CALLISTO archive
- Downloads a spectrogram file
- Loads it into a Spectrogram object
- Displays a frequency–time intensity plot
