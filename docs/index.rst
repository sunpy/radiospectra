**************************
radiospectra Documentation
**************************

``radiospectra`` is a Python package for reading, storing, and visualising dynamic radio spectra in heliophysics, from both ground- and space-based instruments.

.. warning::

    ``radiospectra`` is under active redevelopment, with more functionality and instrument support coming soon.
    The package is moving to build on `ndcube <https://docs.sunpy.org/projects/ndcube/>`__ under the hood, giving a coordinate-aware container for dynamic spectra that is consistent across instruments and with the wider SunPy ecosystem.
    We welcome feedback from anyone working with radio data, if you use dynamic spectra, please get in touch via the `SunPy Chat <https://openastronomy.element.io/#/room/#sunpy:openastronomy.org>`_.

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

Citing radiospectra
===================
If you use ``radiospectra`` in your scientific work, we would appreciate it if you cite it.
See the :ref:`citation page <radiospectra-citation>` for details.

Code of Conduct
===============

When you are interacting with the SunPy community you are asked to follow our `Code of Conduct <https://sunpy.org/coc>`__.

.. _SunPy Chat: https://openastronomy.element.io/#/room/#sunpy:openastronomy.org

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   generated/gallery/index
   code_ref/index
   citation
   whatsnew/index
