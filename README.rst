sunpyspectra
-------

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge
.. image:: https://secure.travis-ci.org/sunpy/spectra.svg
    :target: http://travis-ci.org/sunpy/spectra
    :alt: Build status
.. image:: https://ci.appveyor.com/api/projects/status/rf1pg72fiifnxlxl?svg=true
    :target: https://ci.appveyor.com/project/sunpy/spectra
    :alt: Build status
.. image:: https://coveralls.io/repos/github/sunpy/spectra/badge.svg?branch=master
    :target: https://coveralls.io/github/sunpy/spectra?branch=master
    :alt: Coverage status

.. image:: https://landscape.io/github/sunpy/spectra/master/landscape.svg?style=flat
   :target: https://landscape.io/github/sunpy/spectra/master
   :alt: Code Health
.. image:: https://www.codefactor.io/repository/github/sunpy/spectra/badge
   :target: https://www.codefactor.io/repository/github/sunpy/spectra
   :alt: CodeFactor
.. image:: https://codeclimate.com/github/sunpy/spectra/badges/gpa.svg
   :target: https://codeclimate.com/github/sunpy/spectra
   :alt: Code Climate
.. image:: https://api.codacy.com/project/badge/Grade/cac252271b9943d78158be6a967d05fa
   :target: https://www.codacy.com/app/sunpy/spectra
   :alt: Code grade

This package aims to provide all the support needed for any type of spectra on solar physics.

If you are coming here from the `Warning` deprecation in sunpy you more probably need to change
from

.. code-block:: python

   from sunpy.spectra.spectrum import Spectrum

to

.. code-block:: python
   from sunpyspectra.spectrum import Spectrum

after installing it as:

.. code-block:: bash
   pip install git+https://github.com/sunpy/spectra.git


License
-------

This project is Copyright (c) SunPy Developers and licensed under the terms of the BSD 3-Clause license. See the licenses folder for more information.
