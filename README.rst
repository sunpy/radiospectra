************
radiospectra
************

.. |Powered by NumFOCUS| image:: https://img.shields.io/badge/powered%20by-NumFOCUS-orange.svg?style=flat&colorA=E1523D&colorB=007D8A
   :target: https://numfocus.org

This package aims to provide support for some type of radiospectra on solar physics.

This uses SunPy underneath, which is an open-source Python library for Solar Physics data analysis and visualization.
Our homepage `SunPy`_ has more information about the project.

.. _SunPy: https://sunpy.org

Installation
============

The recommended way to install radiospectra is with `anaconda <https://www.anaconda.com/distribution/>`__.

.. code:: bash

    $ conda config --append channels conda-forge
    $ conda install radiospectra

You can also use pip:

.. code-block:: bash

   pip install radiospectra

If you are coming here from the ``Warning`` deprecation in SunPy you more probably need to change from::

   from sunpy.spectra.spectrum import Spectrum

to::

   from radiospectra.spectrum import Spectrum

Getting Help
============

For more information or to ask questions about radiospectra (and SunPy), check out:

-  `SunPy Documentation`_
-  `SunPy Matrix Channel`_
-  `SunPy Mailing List`_

.. _SunPy Documentation: https://docs.sunpy.org/en/stable/
.. _SunPy Matrix Channel: https://chat.openastronomy.org/#/room/#sunpy:openastronomy.org
.. _SunPy Mailing List: https://groups.google.com/forum/#!forum/sunpy

Contributing
============

If you would like to get involved, start by joining the `SunPy mailing list`_ and check out the `Developers Guide`_ section of the SunPy docs.
Stop by our chat room `#sunpy:openastronomy.org`_ if you have any questions.
Help is always welcome so let us know what you like to work on, or check out the `issues page`_ for the list of known outstanding items.

For more information on contributing to SunPy, please read our `Newcomers guide`_.

.. _SunPy mailing list: https://groups.google.com/forum/#!forum/sunpy
.. _Developers Guide: http://docs.sunpy.org/en/latest/dev_guide/index.html
.. _`#sunpy:openastronomy.org`: https://chat.openastronomy.org/#/room/#sunpy:openastronomy.org
.. _issues page: https://github.com/sunpy/sunpy/issues
.. _Newcomers guide: https://docs.sunpy.org/en/latest/dev_guide/newcomers.html

Code of Conduct
===============

When you are interacting with the SunPy community you are asked to follow our `Code of Conduct`_.

.. _Code of Conduct: https://docs.sunpy.org/en/latest/coc.html
