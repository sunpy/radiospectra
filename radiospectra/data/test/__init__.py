"""
Access bundled test data files.
"""

from pathlib import Path

__all__ = ["TEST_DATA_DIR", "get_test_data_filepath"]

TEST_DATA_DIR = Path(__file__).parent


def get_test_data_filepath(filename):
    """
    Return the absolute path to a bundled test-data file.

    Parameters
    ----------
    filename : `str`
        Name of the file in ``radiospectra.data.test``.
    """
    path = TEST_DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"No bundled test data file named '{filename}' in '{TEST_DATA_DIR}'.")
    return path
