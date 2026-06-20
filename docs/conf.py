import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "sql-executor"
copyright = "2026, Bhavesh"
author = "Bhavesh"

# Pull version from the installed package so docs/conf.py never goes
# stale when you bump pyproject.toml.
try:
    from importlib.metadata import version as _pkg_version
    release = _pkg_version("sql-executor")
except Exception:
    release = "0.1.0"
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",   # lets autodoc parse Google/NumPy-style docstrings
    "sphinx.ext.viewcode",   # adds "[source]" links next to each class/function
]

autodoc_member_order = "bysource"
autodoc_typehints = "description"

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
