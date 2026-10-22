mixedtape
=========

A feasibility playground for mixed Python/Rust packaging with
`maturin <https://www.maturin.rs/>`_, in the shape of a small library of
string-similarity and checksum helpers.

The interesting part is the *packaging*: a single wheel containing both
a pure-Python package and a compiled Rust extension, with hot paths
oxidized one member at a time and the public import surface unchanged.
See the `project repository`_ for the full story.

.. _project repository: https://github.com/dangertoaster/maturin-playground

.. toctree::
   :hidden:

   reference/index
