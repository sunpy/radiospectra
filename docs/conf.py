# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# https://www.sphinx-doc.org/en/master/config

# flake8: NOQA: E402

# -- stdlib imports ------------------------------------------------------------
import os
import datetime
from packaging.version import Version

# -- Read the Docs Specific Configuration --------------------------------------

# This needs to be done before radiospectra is imported
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if on_rtd:
    os.environ["SUNPY_CONFIGDIR"] = "/home/docs/"
    os.environ["HOME"] = "/home/docs/"
    os.environ["LANG"] = "C"
    os.environ["LC_ALL"] = "C"
    os.environ["HIDE_PARFIVE_PROGRESS"] = "True"


# -- Project information -----------------------------------------------------
# The full version, including alpha/beta/rc tags
from radiospectra import __version__  # NOQA

_version = Version(__version__)
version = release = str(_version)
# Avoid "post" appearing in version string in rendered docs
if _version.is_postrelease:
    version = release = _version.base_version
# Avoid long githashes in rendered Sphinx docs
elif _version.is_devrelease:
    version = release = f"{_version.base_version}.dev{_version.dev}"
is_development = _version.is_devrelease
is_release = not (_version.is_prerelease or _version.is_devrelease)

project = "radiospectra"
author = "The SunPy Community"
copyright = f"{datetime.datetime.now().year}, {author}"  # noqa: A001

# -- General configuration ---------------------------------------------------

# Wrap large function/method signatures
maximum_signature_line_length = 80

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "matplotlib.sphinxext.plot_directive",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
    "sphinx_changelog",
    "sphinx_gallery.gen_gallery",
]

# Set automodapi to generate files inside the generated directory
automodapi_toctreedirnm = "generated/api"

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
html_extra_path = ["robots.txt"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
source_suffix = {".rst": "restructuredtext"}

# The master toctree document.
master_doc = "index"

# Treat everything in single ` as a Python reference.
default_role = "py:obj"

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": (
        "https://docs.python.org/3/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/python3.inv"),
    ),
    "numpy": (
        "https://numpy.org/doc/stable/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/numpy.inv"),
    ),
    "scipy": (
        "https://docs.scipy.org/doc/scipy/reference/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/scipy.inv"),
    ),
    "astropy": ("https://docs.astropy.org/en/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "mpl_animators": ("https://docs.sunpy.org/projects/mpl-animators/en/stable/", None),
    "ndcube": ("https://docs.sunpy.org/projects/ndcube/en/stable/", None),
    "sunpy": ("https://docs.sunpy.org/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sunpy"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# Render inheritance diagrams in SVG
graphviz_output_format = "svg"

graphviz_dot_args = [
    "-Nfontsize=10",
    "-Nfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Efontsize=10",
    "-Efontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Gfontsize=10",
    "-Gfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
]

# By default, when rendering docstrings for classes, sphinx.ext.autodoc will
# make docs with the class-level docstring and the class-method docstrings,
# but not the __init__ docstring, which often contains the parameters to
# class constructors across the scientific Python ecosystem. The option below
# will append the __init__ docstring to the class-level docstring when rendering
# the docs. For more options, see:
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autoclass_content
autoclass_content = "both"

# -- Sphinx Gallery ----------------------------------------------------------

sphinx_gallery_conf = {
    "backreferences_dir": os.path.join("generated", "modules"),
    "filename_pattern": "^((?!skip_).)*$",
    "examples_dirs": os.path.join("..", "examples"),
    "gallery_dirs": os.path.join("generated", "gallery"),
    "abort_on_example_error": False,
    "plot_gallery": "True",
    "remove_config_comments": True,
    "doc_module": "radiospectra",
    "only_warn_on_example_error": True,
}
