"""Checksum helpers, implemented in Rust.

Net-new native functionality (unlike :mod:`mixedtape.grammar`, there is
no pure-Python fallback — the extension is required).

Whether a given module is oxidized is an implementation detail: every
import form that would work for a pure-python package works here,
including addressing the (rust-backed) submodule directly::

    from mixedtape.checksums import sha256_data, streaming
    import mixedtape.checksums.streaming
    from mixedtape.checksums.streaming import ChunkedHasher
"""

from mixedtape._mixedtape.checksums import sha256_data, streaming, xxh3_data

__all__ = ["sha256_data", "streaming", "xxh3_data"]
