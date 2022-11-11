0.5.0 (2022-10-15)
==================

Breaking Changes
----------------

- The old ``Spectrogram`` class has been removed. (`#76 <https://github.com/sunpy/radiospectra/pull/76>`__)
- The new ``Spectrogram2`` class has been renamed to ``Spectrogram``. (`#76 <https://github.com/sunpy/radiospectra/pull/76>`__)
- Adding colorbar functionality to ``plot`` (`#80 <https://github.com/sunpy/radiospectra/pull/80>`__)

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
- Add STEREO WAVES (SWAVES) Fido client `radiospectra.net.SWAVESClient`. (`#35 <https://github.com/sunpy/radiospectra/pull/35>`__)
