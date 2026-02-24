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
    base_dir = TEST_DATA_DIR.resolve()
    path = (TEST_DATA_DIR / Path(filename)).resolve()
    try:
        path.relative_to(base_dir)
    except ValueError as exc:
        raise ValueError(f"Test data path '{filename}' escapes the test-data directory '{base_dir}'.") from exc
    if not path.is_file():
        raise FileNotFoundError(f"No bundled test data file named '{filename}' in '{TEST_DATA_DIR}'.")
    return path
