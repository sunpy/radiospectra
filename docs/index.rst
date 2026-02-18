**************************
radiospectra Documentation
**************************

``radiospectra`` is a Python software package that provides support for some type of radio spectra in solar physics.

.. warning::

    ``radiospectra`` is currently undergoing a transition.
    We have replaced the old spectragram class with a new one which is lacking in some features.

    We also have to decide on the fututre of the ``radiospectra`` package.
    This package does not see heavy development and is not used by many people.
    It is also not clear what the future of radio spectra within the SunPy Project is going to be.
    In addition, ``xarray`` or similar packages could offer a better data handling solution than the current ``radiospectra`` package.
    We need and want users (of radio data in general) to chime in and to help us decide the future of this package.

Installation
============
The recommended way to install ``radiospectra`` is with `miniforge <https://github.com/conda-forge/miniforge#miniforge3>`__.
To install ``radiospectra`` once miniforge is installed run the following command:

.. code:: bash

    $ conda install radiospectra

For detailed installation instructions, see the `installation guide <https://docs.sunpy.org/en/stable/guide/installation.html>`__ in the ``sunpy`` docs.

Getting Help
============
For more information or to ask questions about ``radiospectra`` or any other SunPy library, check out:

-  `radiospectra documentation <https://docs.sunpy.org/projects/radiospectra/>`__
-  `SunPy Chat`_
-  `SunPy mailing list <https://groups.google.com/forum/#!forum/sunpy>`__

Contributing
============
If you would like to get involved, start by joining the `SunPy Chat`_ and check out our `Newcomers' guide <https://docs.sunpy.org/en/latest/dev_guide/contents/newcomers.html>`__.
This will walk you through getting set up for contributing.

Code of Conduct
===============

When you are interacting with the SunPy community you are asked to follow our `Code of Conduct <https://sunpy.org/coc>`__.

.. _SunPy Chat: https://openastronomy.element.io/#/room/#sunpy:openastronomy.org

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   code_ref/index
   whatsnew/index
   dev_guide
