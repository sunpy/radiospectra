"""
Cropping a Spectrogram
======================

This example demonstrates how to crop a spectrogram by time and frequency
and how to extract 1D profiles using native `ndcube` methods
(`~ndcube.NDCube.crop` and `~ndcube.NDCube.crop_by_values`).
"""

###############################################################################
# The `~radiospectra.spectrogram.GenericSpectrogram` class inherits from
# `~ndcube.NDCube`, which provides powerful coordinate-aware slicing.
# Two key methods are available:
#
# * `~ndcube.NDCube.crop` — accepts high-level coordinate objects
#   (e.g., `~astropy.time.Time` and `~astropy.coordinates.SpectralCoord`).
# * `~ndcube.NDCube.crop_by_values` — accepts low-level physical values
#   as `~astropy.units.Quantity`.
#
# Let's start by downloading a WIND/WAVES RAD1 spectrogram to use for this example.

import matplotlib.pyplot as plt

import astropy.units as u
from astropy.coordinates import SpectralCoord
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

fig = plt.figure()
ax = fig.add_subplot(111)
spec.plot(axes=ax)
ax.set_title("Full Spectrogram")
plt.show()

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

fig = plt.figure()
ax = fig.add_subplot(111)
time_cropped.plot(axes=ax)
ax.set_title("Time Cropped Spectrogram")
plt.show()

###############################################################################
# Cropping by frequency
# ---------------------
# To crop by frequency we can use `~ndcube.NDCube.crop_by_values`,
# which accepts `~astropy.units.Quantity` values directly.
# Here we pass ``None`` for the time axis and provide the frequency
# bounds as `~astropy.units.Quantity`.

low_freq = 200 * u.kHz
high_freq = 600 * u.kHz

freq_cropped = spec.crop_by_values((None, low_freq), (None, high_freq))

fig = plt.figure()
ax = fig.add_subplot(111)
freq_cropped.plot(axes=ax)
ax.set_title("Frequency Cropped Spectrogram")
plt.show()

###############################################################################
# Cropping by both time and frequency
# -----------------------------------
# We can also crop both axes simultaneously. Here we use `~ndcube.NDCube.crop`
# with both `~astropy.time.Time` and `~astropy.coordinates.SpectralCoord`.

low_freq_coord = SpectralCoord(200 * u.kHz)
high_freq_coord = SpectralCoord(600 * u.kHz)

both_cropped = spec.crop((start_time, low_freq_coord), (end_time, high_freq_coord))

fig = plt.figure()
ax = fig.add_subplot(111)
both_cropped.plot(axes=ax)
ax.set_title("Time and Frequency Cropped Spectrogram")
plt.show()

###############################################################################
# Extracting 1D profiles
# ----------------------
# A 1D profile can be extracted by setting the lower and upper bounds to the
# same value. `ndcube` automatically collapses that dimension.
# Let's extract a time profile at a specific frequency and a frequency profile
# at a specific time.

target_freq = 250 * u.kHz
time_profile = spec.crop_by_values((None, target_freq), (None, target_freq))

target_time = Time("2017-09-02T16:00:00")
freq_profile = spec.crop((target_time, None), (target_time, None))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(time_profile.times.datetime, time_profile.data)
ax1.set_xlabel("Time")
ax1.set_ylabel("Intensity")
ax1.set_title(f"Time Profile at {target_freq}")

ax2.plot(freq_profile.frequencies, freq_profile.data)
ax2.set_xlabel("Frequency (kHz)")
ax2.set_ylabel("Intensity")
ax2.set_title(f"Freq Profile at {target_time.strftime('%H:%M:%S')}")

plt.show()
