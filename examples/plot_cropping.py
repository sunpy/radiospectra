"""
Cropping a WIND/WAVES spectrogram
=================================

This example demonstrates how to crop a spectrogram by time and frequency
using native `ndcube` methods (`~ndcube.NDCube.crop` and `~ndcube.NDCube.crop_by_values`).
"""

###############################################################################
# The `~radiospectra.spectrogram.GenericSpectrogram` class inherits from
# `~ndcube.NDCube`, which provides powerful coordinate-aware slicing.
# Two key methods are available:
#
# * `~ndcube.NDCube.crop` — accepts high-level coordinate objects
#   (e.g. `~astropy.time.Time`).
# * `~ndcube.NDCube.crop_by_values` — accepts low-level physical values
#   as `~astropy.units.Quantity`.
#
# Let's start by downloading a WIND/WAVES RAD1 spectrogram.

import matplotlib.pyplot as plt

import astropy.units as u
from astropy.time import Time

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra import net  # noqa: F401
from radiospectra.spectrogram import Spectrogram

###############################################################################
# Search for WIND/WAVES data during a known event on 2017-09-02
# and load the RAD1 receiver (the first file when sorted by name).

query = Fido.search(
    a.Time("2017-09-02T15:00", "2017-09-02T18:00"),
    a.Instrument.waves,
)

waves_files = Fido.fetch(query["waves"])
waves_specs = Spectrogram(sorted(waves_files))
spec = waves_specs[0]

###############################################################################
# Cropping by time
# ----------------
# To crop the spectrogram to a specific time range we use
# `~ndcube.NDCube.crop`. Each argument is a tuple of world-coordinate
# values - one per WCS world axis. We supply a `~astropy.time.Time` for
# the time axis and ``None`` for the frequency axis to leave it unchanged.

start_time = Time("2017-09-02T15:30:00")
end_time = Time("2017-09-02T17:00:00")

time_cropped = spec.crop((start_time, None), (end_time, None))

###############################################################################
# Cropping by frequency
# ---------------------
# To crop by frequency we use `~ndcube.NDCube.crop_by_values`,
# which accepts `~astropy.units.Quantity` values directly.
# Here we pass ``None`` for the time axis and provide the frequency
# bounds as `~astropy.units.Quantity`.

low_freq = 200 * u.kHz
high_freq = 600 * u.kHz

freq_cropped = spec.crop_by_values((None, low_freq), (None, high_freq))

###############################################################################
# Plotting the results
# --------------------
# Finally, let's visualise the original spectrogram alongside the cropped
# versions.

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

spec.plot(axes=axes[0])
axes[0].set_title("Full Spectrogram")

time_cropped.plot(axes=axes[1])
axes[1].set_title("Time Cropped")

freq_cropped.plot(axes=axes[2])
axes[2].set_title("Freq Cropped")

fig.tight_layout()
plt.show()
