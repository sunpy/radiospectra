"""
Creating a GenericSpectrogram from an unsupported file
======================================================

This example shows how to load data from a NumPy ``.npy`` file and construct
a `~radiospectra.spectrogram.GenericSpectrogram` when the file format is not
read directly by ``radiospectra``.
"""

import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from astropy.time import Time
from sunpy.net import attrs as a

from radiospectra.spectrogram import GenericSpectrogram

###############################################################################
# Here we make a small sample array and save it as a ``.npy`` file so this
# example can run without a separate data file. For your own data, replace this
# block with ``data = np.load("path/to/your_spectrogram.npy")``.

n_times = 120
n_frequencies = 64
sample_data = np.random.default_rng(0).random((n_times, n_frequencies))

with tempfile.TemporaryDirectory() as temp_dir:
    data_path = Path(temp_dir) / "sample_spectrogram.npy"
    np.save(data_path, sample_data)
    data = np.load(data_path)

###############################################################################
# A generic spectrogram needs time and frequency coordinates for its data.
# Here each row is one time and each column is one frequency.

times = Time("2025-01-01T00:00:00") + np.arange(n_times) * u.s
frequencies = np.linspace(20, 1000, n_frequencies) * u.MHz

###############################################################################
# Add the coordinates and descriptive information to the metadata, then pass
# both the data array and metadata dictionary to ``GenericSpectrogram``.

meta = {
    "observatory": "Example Observatory",
    "instrument": "Example Instrument",
    "detector": "Example Detector",
    "start_time": times[0],
    "end_time": times[-1],
    "wavelength": a.Wavelength(frequencies[0], frequencies[-1]),
    "times": times,
    "freqs": frequencies,
}

spectrogram = GenericSpectrogram(data, meta)
print(spectrogram)

###############################################################################
# The resulting object can be plotted with its ``plot`` method.

fig, ax = plt.subplots(figsize=(10, 5))
mesh = spectrogram.plot(axes=ax)
fig.colorbar(mesh, ax=ax, label="Intensity")
ax.set_xlabel("Time")
ax.set_ylabel("Frequency")
fig.tight_layout()
plt.show()
