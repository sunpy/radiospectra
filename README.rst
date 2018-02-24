radiospectra
------------

.. image:: https://readthedocs.org/projects/radiospectra/badge/?version=latest
    :target: http://radiospectra.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://secure.travis-ci.org/sunpy/radiospectra.svg
    :target: http://travis-ci.org/sunpy/radiospectra
    :alt: Build status
.. image:: https://ci.appveyor.com/api/projects/status/9fh7gffk06dnrubh?svg=true
    :target: https://ci.appveyor.com/project/sunpy/radiospectra
    :alt: Build status
.. image:: https://coveralls.io/repos/github/sunpy/radiospectra/badge.svg?branch=master
    :target: https://coveralls.io/github/sunpy/radiospectra?branch=master
    :alt: Coverage status

.. image:: https://landscape.io/github/sunpy/radiospectra/master/landscape.svg?style=flat
   :target: https://landscape.io/github/sunpy/radiospectra/master
   :alt: Code Health
.. image:: https://www.codefactor.io/repository/github/sunpy/radiospectra/badge
   :target: https://www.codefactor.io/repository/github/sunpy/radiospectra
   :alt: CodeFactor
.. image:: https://codeclimate.com/github/sunpy/radiospectra/badges/gpa.svg
   :target: https://codeclimate.com/github/sunpy/radiospectra
   :alt: Code Climate
.. image:: https://api.codacy.com/project/badge/Grade/cac252271b9943d78158be6a967d05fa
   :target: https://www.codacy.com/app/sunpy/radiospectra
   :alt: Code grade

This package aims to provide support for some type of radiospectra on solar physics.

If you are coming here from the `Warning` deprecation in sunpy you more probably need to change
from

.. code-block:: python

   from sunpy.spectra.spectrum import Spectrum

to

.. code-block:: python
   from radiospectra.spectrum import Spectrum

after installing it as:

.. code-block:: bash
   pip install radiospectra

Development
-----------

Note that this package may change a lot in the future! After the 0.1 release radiospectra will
only support python 3.6+ and sunpy 1.0.

If you wish to test the latest development versions you should install it directly from the
git repository as:

.. code-block:: bash
   pip install git+https://github.com/sunpy/radiospectra.git


License
-------

This project is Copyright (c) SunPy Developers and licensed under the terms of the BSD 2-Clause license. See the licenses folder for more information.

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge
