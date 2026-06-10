"""
Searching for and plotting a WIND/WAVES spectrogram
===================================================

This example demonstrates how to download and plot a WIND/WAVES spectrogram
using `sunpy.net.Fido` and the `~radiospectra.spectrogram.Spectrogram` class.
# WAVES is the radio and plasma wave instrument on the WIND spacecraft. Its two
# radio receivers, RAD1 (20-1040 kHz) and RAD2 (1.075-13.825 MHz)

"""

import matplotlib.pyplot as plt

from sunpy.net import Fido
from sunpy.net import attrs as a

from radiospectra import net  # noqa: F401
from radiospectra.spectrogram import Spectrogram

###############################################################################
# First, let's search for some WIND/WAVES data during a known event.
# We will search for data on 2017-09-02 between 15:00 and 18:00.
# With no `~sunpy.net.attrs.Wavelength` specified, the search
# returns one file per receiver (RAD1 and RAD2).

query = Fido.search(a.Time("2017-09-02T15:00", "2017-09-02T18:00"), a.Instrument.waves)
print(query)

###############################################################################
# Now we fetch the files using `sunpy.net.Fido` and load them into a
# `~radiospectra.spectrogram.Spectrogram` object.
# As the search matched both receivers, ``waves_spec`` is a list with one spectrogram per receiver.
# Sorting the files by name places the RAD1 (lower-frequency) spectrogram first and RAD2
# (higher-frequency) second.

waves_files = Fido.fetch(query["waves"])
waves_spec = Spectrogram(sorted(waves_files))

###############################################################################
# We can print a string representation of the downloaded spectrograms.
# `waves_spec` is a list of spectrograms, one for each frequency band (RAD1, RAD2).

print(waves_spec)

###############################################################################
# Finally, let's plot the first spectrogram (RAD1) using matplotlib.
# The :func:`~radiospectra.spectrogram.GenericSpectrogram.plot` method automatically formats the axes.

fig, ax = plt.subplots(figsize=(10, 5))
mesh = waves_spec[0].plot(axes=ax)
fig.colorbar(mesh, ax=ax, label="Intensity")
ax.set_title("WIND/WAVES RAD1 Spectrogram")
fig.tight_layout()
plt.show()
