Test Data
=========

This directory contains small test fixtures used by the radiospectra test suite.

- HTML/GZIP fixtures are used by ``radiospectra.net`` client tests.
- ``BIR_20110607_062400_10.fit`` is a packaged FITS example file.

Keeping these files under ``radiospectra.data`` allows tests to load bundled data
without relying on external ``sunpy.data`` test/sample directories.
