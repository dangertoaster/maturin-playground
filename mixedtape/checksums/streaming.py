"""Streaming checksum hashers.

Thin public shim over the rust-native
``mixedtape._mixedtape.checksums.streaming`` module. The re-exported
symbols are the *same objects* as the rust originals (identical
identity, docstrings, and signatures); this module exists so that static
tooling (type checkers, IDEs) can follow the public dotted path, which a
``sys.modules`` alias alone would hide from them.
"""

from mixedtape._mixedtape.checksums.streaming import ChunkedHasher, digest

__all__ = ["ChunkedHasher", "digest"]
