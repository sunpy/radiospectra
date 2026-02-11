Fix #56: Correct Callisto client and observatory fallback

- spectrogram_factory.py: added a fallback for the observatory field to use "e-CALLISTO" if INSTRUME is missing in the FITS header.
- ecallisto.py: updated post_search_hook to ensure Observatory is always set to "e-CALLISTO" if missing.

Tested locally: verified that fallback works correctly for missing INSTRUME values and eCALLISTOClient returns correct "Observatory" field.
