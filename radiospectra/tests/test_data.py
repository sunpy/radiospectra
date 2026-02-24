from pathlib import Path

import pytest

from radiospectra.data import TEST_DATA_DIR, get_test_data_filepath


def test_get_test_data_filepath_returns_packaged_file():
    path = get_test_data_filepath("ecallisto_resp1.html.gz")
    assert path.is_file()
    assert path.is_relative_to(TEST_DATA_DIR.resolve())


def test_get_test_data_filepath_rejects_path_traversal():
    escape_path = str(Path("..") / ".." / "README.rst")
    with pytest.raises(ValueError, match="escapes the test-data directory"):
        get_test_data_filepath(escape_path)
