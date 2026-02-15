*****************
Development Setup
*****************

``radiospectra`` requires Python 3.12 or newer.

Conda Workflow
==============

.. code:: bash

    conda create -n radiospectra-dev python=3.12 -y
    conda activate radiospectra-dev
    git clone https://github.com/sunpy/radiospectra.git
    cd radiospectra
    python -m pip install -U pip
    python -m pip install -e ".[dev]"

pip/venv Workflow
=================

.. code:: bash

    git clone https://github.com/sunpy/radiospectra.git
    cd radiospectra
    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install -U pip
    python -m pip install -e ".[dev]"

Run Tests
=========

Quick local run with ``pytest``:

.. code:: bash

    python -m pytest --pyargs radiospectra

Run the tox environment used in CI for Python 3.12:

.. code:: bash

    python -m pip install tox tox-pypi-filter
    tox -e py312

Code Style / pre-commit
=======================

Install and run the same checks as ``tox -e codestyle``:

.. code:: bash

    python -m pip install pre-commit
    pre-commit install
    pre-commit run --all-files

You can also run the tox wrapper directly:

.. code:: bash

    tox -e codestyle

Build Docs (Optional)
=====================

Build HTML docs with the tox environment used in CI:

.. code:: bash

    python -m pip install tox tox-pypi-filter
    tox -e build_docs

The built docs are in ``docs/_build/html``.
