from pathlib import Path
from functools import wraps

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import astropy

__all__ = ["figure_test"]


def get_hash_library_name():
    """
    Generate the hash library name for this env.
    """
    mpl_version = (
        "dev" if (("dev" in mpl.__version__) or ("rc" in mpl.__version__)) else mpl.__version__.replace(".", "")
    )
    astropy_version = (
        "dev"
        if (("dev" in astropy.__version__) or ("rc" in astropy.__version__))
        else astropy.__version__.replace(".", "")
    )
    return f"figure_hashes_mpl_{mpl_version}_astropy_{astropy_version}.json"


def figure_test(test_function):
    """
    All such decorated tests are marked with `pytest.mark.mpl_image_compare`
    for convenient filtering.

    Examples
    --------
    @figure_test
    def test_simple_plot():
        plt.plot([0, 1])
    """
    hash_library_name = get_hash_library_name()
    hash_library_file = Path(__file__).parent / hash_library_name

    @pytest.mark.mpl_image_compare(
        hash_library=hash_library_file,
        savefig_kwargs={"metadata": {"Software": None}},
        style="default",
    )
    @wraps(test_function)
    def test_wrapper(*args, **kwargs):
        ret = test_function(*args, **kwargs)
        if ret is None:
            ret = plt.gcf()
        return ret

    return test_wrapper
