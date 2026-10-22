import datetime
import os

# Configuration for the Sphinx documentation builder.
#
# Layout notes for this repository:
#
# * The venv lives at the repo root (``.venv``); the docs Makefile points
#   Sphinx at it via ``DOCS_VENVDIR=../.venv`` (exported by the root
#   Makefile).
# * The native extension must be built (``make build``) before docs will
#   build, because autodoc imports the package to extract docstrings —
#   including those written in Rust, which pyo3 bakes into the compiled
#   module as runtime ``__doc__`` attributes.
# * ``conf.py`` assumes the current working directory is ``docs/`` (the
#   usual ``make -C docs`` invocation), so ``import mixedtape`` resolves
#   to the repo checkout without any path fiddling.

#######################
# Project information #
#######################

project = "mixedtape"
author = "dangertoaster"
_first_year = 2026
_year = datetime.date.today().year
copyright = f"{_first_year}{f'-{_year}' if _year > _first_year else ''}, {author}"

html_context = {
    "product_page": "github.com/dangertoaster/maturin-playground",
    "discourse": "",
    "mattermost": "",
    "matrix": "",
    "github_url": "https://github.com/dangertoaster/maturin-playground",
    "repo_default_branch": "main",
    "repo_folder": "/docs/",
    "display_contributors": False,
    "github_issues": "enabled",
    "author": author,
    "license": {
        "name": "GPL-3.0-only",
        "url": "https://github.com/dangertoaster/maturin-playground/blob/main/LICENSE",
    },
}

html_theme_options = {
    "source_edit_link": "https://github.com/dangertoaster/maturin-playground",
}

# The project slug passed to the sphinx-notfound-page extension
slug = "maturin-playground"


#########################
# Sitemap configuration #
#########################

# Use RTD canonical URL to ensure duplicate pages have a specific canonical URL
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")

# sphinx-sitemap uses html_baseurl to generate the full URL for each page:
sitemap_url_scheme = "{link}"

sitemap_excludes = [
    "404/",
    "genindex/",
    "search/",
]


################################
# Template and asset locations #
################################

templates_path = ["_templates"]


#############
# Redirects #
#############

# Add redirects to the 'redirects.txt' file
# https://sphinxext-rediraffe.readthedocs.io/en/latest/
rediraffe_redirects = "redirects.txt"
rediraffe_dir_only = True

# Empty redirects file for now
import pathlib

redirects_file = pathlib.Path(__file__).parent / "redirects.txt"
if not redirects_file.exists():
    redirects_file.touch()


###########################
# Link checker exceptions #
###########################

linkcheck_ignore = [
    r"^https://github.com",
    r"^https://crates.io/",
    r"^https://([\w-]*\.)?rust-lang.org(/(stable/?)?)?$",
]

linkcheck_retries = 20
linkcheck_report_timeouts_as_broken = False


########################
# Configuration extras #
########################

extensions = [
    "canonical_sphinx",
    "notfound.extension",
    "sphinx_design",
    "sphinx_rerediraffe",
    "sphinxext.opengraph",
    "sphinx_related_links",
    "sphinx_roles",
    "sphinx_terminal",
    "sphinx.ext.intersphinx",
    "sphinx_sitemap",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.doctest",
]

exclude_patterns = [
    "_build",
    "_dev",
    "Thumbs.db",
    ".DS_Store",
]

# autodoc: document members in the order they're defined in the source,
# not alphabetically.
autodoc_member_order = "bysource"

# Type hints configuration
set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = True

# Add configuration for intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Block Intersphinx from looking up external sources with internal references.
intersphinx_disabled_reftypes = ["std:*"]
