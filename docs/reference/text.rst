``mixedtape.text``
==================

Text-similarity helpers. This module is partially oxidized: the hot
paths are implemented in Rust (in ``mixedtape._mixedtape``), while
derived conveniences remain plain Python. Everything below is imported
from the same public module regardless of which language wrote it —
autodoc picks up the Rust-backed members from their pyo3-embedded
docstrings.

.. automodule:: mixedtape.text
   :members:
   :undoc-members:
   :show-inheritance:
