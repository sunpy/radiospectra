0.7.0 (2026-06-16)
==================

Breaking Changes
----------------

- Increased minimum version of:

  - Python >= 3.12.
  - NumPy >= 1.26.0.
  - Matplotlib >= 3.8.0.
  - SciPy >= 1.12.0.
  - Sunpy >= 7.0.0. (`#127 <https://github.com//pull/127>`__)


New Features
------------

- Added support for Solar Orbiter RPW Level 3 TNR and HFR survey data products. (`#148 <https://github.com//pull/148>`__)
- Restored the WIND/WAVES ``Fido`` client `~radiospectra.net.sources.wind.WAVESClient` and updated it to use NASA SPDF server and altered paths and filenames. (`#158 <https://github.com//pull/158>`__)
- Added end-to-end online integration tests for all 6 radiospectra data sources (eCallisto, EOVSA, I-LOFAR, PSP/RFS, RSTN, WIND/WAVES) to verify search, fetch and spectrogram reading. (`#202 <https://github.com//pull/202>`__)
- Add Learmonth Solar Observatory Fido client `~radiospectra.net.sources.learmonth.ASWSClient` for accessing RSTN Learmonth data from the Australian Bureau of Meteorology Space Weather Services World Data Centre archive (not available from RSTN newwork post 2019.) (`#213 <https://github.com//pull/213>`__)
- Add Nançay Decameter Array (NDA) Fido client `radiospectra.net.sources.nda.NDAClient`. (`#220 <https://github.com//pull/220>`__)
- Added support for reading and parsing Nançay Decameter Array (NDA) solar radio burst observations. This introduces the `radiospectra.spectrogram.sources.nda.NDASpectrogram` subclass. (`#231 <https://github.com//pull/231>`__)


Bug Fixes
---------

- Migrated network clients to the unified ``sunpy.net.scraper.Scraper`` format, fixing scraper-based searches with newer ``sunpy`` releases. (`#142 <https://github.com//pull/142>`__)
- Fixed an issue where plotting spectrograms with non-UTC time scales (e.g., 'tt') would result in time offsets by ensuring conversion to UTC before plotting. (`#144 <https://github.com//pull/144>`__)
- Fixed mixed frequency unit plotting on shared axes to correctly convert units when multiple spectrograms with different frequency units are plotted together. (`#151 <https://github.com//pull/151>`__)
- Fix `~radiospectra.spectrogram.sources.callisto.CALISTOSpectrogram` observatory location logic bug and improve docstrings. (`#169 <https://github.com//pull/169>`__)
- Fixed a ``KeyError`` raised when accessing the ``level`` and ``version`` properties of an ``RFSSpectrogram`` constructed from a real Parker Solar Probe RFS CDF file via `~radiospectra.spectrogram.spectrogram_factory.SpectrogramFactory`. (`#187 <https://github.com//pull/187>`__)
- Remove legacy sunpy version check and fallback scraper pattern in `~radiospectra.net.sources.eovsa.EOVSAClient` since `sunpy[net]>=7.0` is now mandated. (`#237 <https://github.com//pull/237>`__)
- Update `~radiospectra.net.sources.ilofar.ILOFARMode357Client` client to search additional directory for data. (`#239 <https://github.com//pull/239>`__)


Documentation
-------------

- Created docstring examples for ``RPWSpectrogram`` data. (`#173 <https://github.com//pull/173>`__)
- Added a new Example Gallery to the documentation using `sphinx-gallery`, including an example that demonstrates how to search, download, load and plot WIND/WAVES data using `~sunpy.net.Fido` and `~radiospectra.spectrogram.Spectrogram`. (`#227 <https://github.com//pull/227>`__)
- Fix docs configuration so the change log is included. (`#229 <https://github.com//pull/229>`__)
- Add missing python files to autogenerate API reference. (`#235 <https://github.com//pull/235>`__)
- Added a ``CITATION.cff`` file, a Zenodo DOI badge and citation section to the README, and a citation page to the documentation. (`#236 <https://github.com//pull/236>`__)


Internal Changes
----------------

- Update test configuration to run tests marked with `remote_data` and fail tests that access the network without the mark. (`#233 <https://github.com//pull/233>`__)
- Add retry and backoff config to online tests and remove duplicate online test run from CI (`#235 <https://github.com//pull/235>`__)

0.6.0 (2024-07-23)
==================

Backwards Incompatible Changes
------------------------------

- Dropped support for Python 3.9 (`#111 <https://github.com/sunpy/radiospectra/pull/111>`__)
- Increased the minimum required version of ``sunpy``  to v6.0.0. (`#112 <https://github.com/sunpy/radiospectra/pull/112>`__)


0.5.0 (2024-03-01)
==================

Breaking Changes
----------------

- The old ``Spectrogram`` class has been removed. (`#76 <https://github.com/sunpy/radiospectra/pull/76>`__)
- The new ``Spectrogram2`` class has been renamed to ``Spectrogram``. (`#76 <https://github.com/sunpy/radiospectra/pull/76>`__)
- Adding colorbar functionality to ``plot`` (`#80 <https://github.com/sunpy/radiospectra/pull/80>`__)
- Renamed ``CALLISTOClient`` to ``eCallistoClient`` (`#61 <https://github.com/sunpy/radiospectra/pull/61>`__)
- ``eCallistoClient`` now does not return endtimes. (`#61 <https://github.com/sunpy/radiospectra/pull/61>`__)
- Removed the ``SWAVESClient`` and ``WAVESClient`` as the old URLS have gone offline. (`#105 <https://github.com/sunpy/radiospectra/pull/105>`__)

Features
--------
- Added support to second ``eCallisto`` file format. (`#61 <https://github.com/sunpy/radiospectra/pull/61>`__)
- Add support for SOLO RPW data. (`#62 <https://github.com/sunpy/radiospectra/pull/62>`__)

- Add `sunpy.net.Fido` client `~radiospectra.net.sources.ilofar.ILOFARMode357` and spectrogram class `~radiospectra.spectrogram2.sources.ILOFARMode357` for ILOFAR mode 357 observations. (`#57 <https://github.com/sunpy/radiospectra/pull/57>`__)

Bug Fixes
---------

- Fix a bug where incorrectly formatted dates were not handled by the `radiospectra.spectrogram.Spectrogram`. (`#84 <https://github.com/sunpy/radiospectra/pull/84>`__)

Trivial/Internal Changes
------------------------

- Moved to Github Actions. (`#105 <https://github.com/sunpy/radiospectra/pull/105>`__)

0.4.0 (2022-05-24)
==================

Breaking Changes
----------------

- Minimum supported version of Python is now 3.8
- Minimum supported version of ``sunpy`` is now 4.0.0 (LTS)

Features
--------

- Add a new spectrogram class `radiospectra.spectrogram.spectrogram.BaseSpectrogram` and factory `radiospectra.spectrogram.spectrogram.SpectrogramFactory` with sources for `~radiospectra.spectrogram.sources.SWAVESSpectrogram`, `~radiospectra.spectrogram.sources.RFSSpectrogram`, `~radiospectra.spectrogram.sources.CALISTOSpectrogram`, `~radiospectra.spectrogram.sources.EOVSASpectrogram` and `~radiospectra.spectrogram.sources.RSTNSpectrogram`. (`#44 <https://github.com/sunpy/radiospectra/pull/44>`__)
- Add `sunpy.net.Fido` clients for `~radiospectra.net.sources.callisto.CALLISTOClient`, `~radiospectra.net.sources.eovsa.EOVSAClient` and `~radiospectra.net.sources.rstn.RSTNClient`. (`#44 <https://github.com/sunpy/radiospectra/pull/44>`__)
- Improve `~radiospectra.spectrogram.spectrogram.SpectrogramFactory` input handling more inputs formats data header pairs, files, urls. (`#54 <https://github.com/sunpy/radiospectra/pull/54>`__)
- Add `sunpy.net.Fido` client `~radiospectra.net.sources.wind.Waves` and spectrogram class `~radiospectra.spectrogram.sources.WAVESSpectrogram` for WIND/WAVES. (`#54 <https://github.com/sunpy/radiospectra/pull/54>`__)

0.3.0 (2021-04-01)
==================

Features
--------

- Add Parker Solar Probe (PSP) Radio Frequency Receiver (RFS) Fido client `radiospectra.net.sources.psp.RFSClient`. (`#34 <https://github.com/sunpy/radiospectra/pull/34>`__)
- Add STEREO WAVES (SWAVES) Fido client ``radiospectra.net.SWAVESClient``. (`#35 <https://github.com/sunpy/radiospectra/pull/35>`__)
