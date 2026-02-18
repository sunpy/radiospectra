Developer Guide: Running CI and Tests Locally
=============================================

This guide explains how contributors can replicate the CI checks locally
before submitting a pull request. Running these checks locally reduces
review friction and prevents common CI failures.

Setting Up a Development Environment
-------------------------------------

Create and activate a virtual environment:

.. code-block:: bash

    python -m venv .venv
    source .venv/bin/activate

Install development dependencies:

.. code-block:: bash

    pip install -e .[dev]

Running Tests
-------------

Run the full test suite:

.. code-block:: bash

    pytest

Run a specific test file:

.. code-block:: bash

    pytest radiospectra/tests/test_example.py

Running Linting and Formatting Checks
--------------------------------------

Run ruff to check for lint issues:

.. code-block:: bash

    ruff check .

Format code:

.. code-block:: bash

    ruff format .

If pre-commit is used:

.. code-block:: bash

    pre-commit install
    pre-commit run --all-files

Before Opening a Pull Request
-----------------------------

- Ensure tests pass locally
- Ensure lint checks pass
- Add a changelog entry if required
- Link an existing issue

Following these steps helps maintain CI stability and reduces review cycles.

