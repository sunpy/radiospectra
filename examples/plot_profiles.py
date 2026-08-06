"""
Extracting 1D profiles from a WIND/WAVES spectrogram
====================================================

This example demonstrates how to extract 1D time and frequency profiles
from a spectrogram using native `ndcube` methods.
"""

###############################################################################
# The `~radiospectra.spectrogram.GenericSpectrogram` class inherits from
# `~ndcube.NDCube`, which provides coordinate-aware slicing. By supplying
# the exact same upper and lower bound to a cropping method, `ndcube`
# will drop that dimension entirely, returning a 1D slice (profile).
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
# and load the RAD1 receiver.

query = Fido.search(
    a.Time("2017-09-02T15:00", "2017-09-02T18:00"),
    a.Instrument.waves,
)

waves_files = Fido.fetch(query["waves"])
waves_specs = Spectrogram(sorted(waves_files))
spec = waves_specs[0]

###############################################################################
# Extracting a time profile
# -------------------------
# A 1D time profile (intensity vs time at a single frequency) can be
# extracted by setting the lower and upper frequency bounds to the same
# value using `~ndcube.NDCube.crop_by_values`.

target_freq = 250 * u.kHz
time_profile = spec.crop_by_values((None, target_freq), (None, target_freq))

###############################################################################
# Extracting a frequency profile
# ------------------------------
# Similarly, a 1D frequency profile (intensity vs frequency at a single
# time) can be obtained with `~ndcube.NDCube.crop` by passing the same
# `~astropy.time.Time` as both bounds.

target_time = Time("2017-09-02T16:00:00")
freq_profile = spec.crop((target_time, None), (target_time, None))

###############################################################################
# Plotting the results
# --------------------

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(time_profile.times.datetime, time_profile.data)
axes[0].set_xlabel("Time")
axes[0].set_ylabel("Intensity")
axes[0].set_title(f"Time Profile at {target_freq}")

axes[1].plot(freq_profile.frequencies, freq_profile.data)
axes[1].set_xlabel("Frequency (kHz)")
axes[1].set_ylabel("Intensity")
axes[1].set_title(f"Freq Profile at {target_time.strftime('%H:%M:%S')}")

fig.tight_layout()
plt.show()
