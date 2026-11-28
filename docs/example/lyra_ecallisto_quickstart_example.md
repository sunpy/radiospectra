# lyra_ecallisto_quickstart_example

> Minimal working examples of fetching and plotting solar data (LYRA irradiance + e-Callisto radio spectra) using SunPy and radiospectra — built as part of my GSoC application to OpenAstronomy.

---

## Overview

This repository demonstrates how to download and visualize data from two solar instruments:

- **LYRA** (Lyman Alpha Radiometer) aboard PROBA2 — EUV/UV solar irradiance timeseries, accessed via [SunPy](https://sunpy.org/)
- **e-Callisto** — a global network of solar radio spectrometers for observing radio bursts, accessed via [radiospectra](https://github.com/sunpy/radiospectra)

Along the way I encountered and resolved several real-world environment issues — documented here to help others get started faster.

---

## What This Does

### LYRA (`lyra.py`)
- Searches for LYRA EUV/UV data over a given time range using `Fido`
- Downloads the FITS file using `Fido.fetch`
- Loads it as a `TimeSeries` object
- Plots solar irradiance over time

### e-Callisto (`callisto.py`)
- Searches for radio spectrogram data from an e-Callisto station using `Fido`
- Downloads the FITS file using `Fido.fetch`
- Loads it as a `Spectrogram` object via `radiospectra`
- Plots the dynamic radio spectrum (time vs frequency)

---

## Final Working Code

### `lyra.py` — LYRA Solar Irradiance

```python
from sunpy.net import Fido, attrs as a
import sunpy.timeseries as ts

# Search for LYRA data
result = Fido.search(a.Time('2012/3/4', '2012/3/6'), a.Instrument.lyra)

# Fetch the first result (overwrite=True ensures no truncated files)
files = Fido.fetch(result[0, 0], overwrite=True)

if len(files) > 0:
    try:
        lyra_ts = ts.TimeSeries(files[0])
        lyra_ts.plot()
    except Exception as e:
        print(f"Error loading file: {e}")
else:
    print("No LYRA data found")
```

### `callisto.py` — e-Callisto Radio Spectrogram

```python
from sunpy.net import Fido, attrs as a
from radiospectra import net                        
from radiospectra.spectrogram2 import Spectrogram   
import matplotlib.pyplot as plt

# Search for e-Callisto data from a specific station
result = Fido.search(
    a.Time('2011/09/25 10:30', '2011/09/25 10:45'),
    a.Instrument('eCALLISTO'),                      
    net.Observatory('ALASKA')                       
)

print(result)

files = Fido.fetch(result[0, 0], overwrite=True)

if len(files) > 0:
    try:
        spec = Spectrogram(files[0])                
        spec.plot()
        plt.show()
    except Exception as e:
        print(f"Error loading spectrogram: {e}")
else:
    print("No e-Callisto data found")
```

---

## Installation

```bash
pip install sunpy radiospectra h5netcdf
pip install "numpy<1.24"   # only if you hit the numpy.typeDict error (see below)
```

Or install a fully compatible set:

```bash
pip install "sunpy>=4.1" "numpy>=1.24" h5netcdf radiospectra
```

---

## Errors Encountered & Fixes

This section documents every error I hit during setup, and exactly how I fixed each one. This is the real value of this repo — a clean debugging trail.

### 1. `a.Instrument.lyra` is not a data reader

**Error:** Using `a.Instrument.lyra.get_files(files[0])` raised an `AttributeError`.

**Cause:** `a.Instrument.lyra` is a *search attribute*, not a file loader. It cannot read data files.

**Fix:** Use `sunpy.timeseries.TimeSeries` to load downloaded files:

```python
# Wrong
spec = a.Instrument.lyra.get_files(files[0])

# Correct
import sunpy.timeseries as ts
lyra_ts = ts.TimeSeries(files[0])
```

---

### 2. `ModuleNotFoundError: No module named 'h5netcdf'`

**Error:** Importing `sunpy.timeseries` failed because `h5netcdf` was missing.

**Fix:**
```bash
pip install h5netcdf
```

---

### 3. `AttributeError: module 'numpy' has no attribute 'typeDict'`

**Error:** `numpy.typeDict` was removed in NumPy 1.24, but an older SunPy version still referenced it.

**Fix (Option A):** Downgrade NumPy:
```bash
pip install "numpy<1.24"
```

**Fix (Option B):** Upgrade SunPy to a version that no longer uses `typeDict`:
```bash
pip install --upgrade sunpy
```

---

### 4. `TypeError: buffer is too small for requested array`

**Error:** The downloaded FITS file was truncated (incomplete download), causing NumPy to fail when reading it.

**Warning that appeared:**
```
WARNING: File may have been truncated: actual file length (74793640) is smaller than the expected size (77627520)
```

**Fix:** Force a fresh download using `overwrite=True`:
```python
files = Fido.fetch(result[0, 0], overwrite=True)
```

Also make sure to pass `files[0]` (a single path string) to `TimeSeries`, not the full `files` list.

---

### 5. Fido returns no results for e-Callisto

**Error:** Fido search returns 0 results for `a.Instrument('e-CALLISTO')`.

**Cause:** Two problems at once — wrong import style and wrong instrument string.

**Fix:**
```python
# Wrong
import radiospectra.net
a.Instrument('e-CALLISTO')   # hyphen causes no match
a.Source('BIR')              # wrong attribute for station

# Correct
from radiospectra import net
a.Instrument('eCALLISTO')    # no hyphen
net.Observatory('ALASKA')    # correct station attribute
```

---

### 6. Old code uses `CALLISTOClient` — renamed in newer versions

**Error:** `ImportError: cannot import name 'CALLISTOClient'`

**Cause:** The client was renamed from `CALLISTOClient` to `eCallistoClient` in radiospectra v0.4+.

**Fix:** You don't need to import the client directly at all — just `from radiospectra import net` and use `Fido` normally with `a.Instrument('eCALLISTO')`.

---

### 7. `ImportError: cannot import name 'CallistoSpectrogram' from 'radiospectra.spectrogram'`

**Error:** Trying to import `CallistoSpectrogram` from `radiospectra.spectrogram` fails because it doesn't exist there.

**Cause:** In newer radiospectra, `spectrogram.py` is a legacy single file kept for backwards compatibility. `CallistoSpectrogram` was never part of it — the class was moved to `spectrogram2`.

**Fix:** Don't use `CallistoSpectrogram` at all. Use the `Spectrogram` factory from `spectrogram2` instead:
```python
from radiospectra.spectrogram2 import Spectrogram
spec = Spectrogram(files[0])
```

---

### 8. `TypeError: __init__() missing 4 required positional arguments: 'time_axis', 'freq_axis', 'start', and 'end'`

**Error:** Loading a downloaded FITS file with `Spectrogram(files[0])` raises a `TypeError`.

**Cause:** `radiospectra.spectrogram` (old module) and `radiospectra.spectrogram2` (new module) are two completely different things. The old `Spectrogram` class expects raw array arguments — it is not a file-reading factory. Importing from the wrong module causes this error.

**Fix:** Import from `spectrogram2`, not `spectrogram`:
```python
# Wrong — old module, not a factory
from radiospectra.spectrogram import Spectrogram

# Correct — new module, reads files directly
from radiospectra.spectrogram2 import Spectrogram
```

---

## Environment

| Package       | Tested Version                          |
|---------------|------------------------------------------|
| Python        | 3.8                                      |
| SunPy         | ≥ 4.1                                    |
| radiospectra  | ≥ 0.4                                    |
| NumPy         | < 1.24 or ≥ 1.24 (with updated SunPy)   |
| h5netcdf      | any recent                               |

---

## About

This project is a small contribution made while applying to [Google Summer of Code (GSoC)](https://summerofcode.withgoogle.com/) with [OpenAstronomy](https://openastronomy.org/). The goal was to go beyond tutorials — run real code, break things, fix them, and document the process clearly.

**Relevant GSoC organizations:**
- [SunPy](https://sunpy.org/) — Python library for solar physics
- [OpenAstronomy](https://openastronomy.org/) — umbrella org for open-source astronomy software

---

## Resources

- [SunPy Documentation](https://docs.sunpy.org/)
- [LYRA Instrument Overview](https://proba2.sidc.be/index.html/science/lyra)
- [OpenAstronomy GSoC Projects](https://openastronomy.org/gsoc/)
