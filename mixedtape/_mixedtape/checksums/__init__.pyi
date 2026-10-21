"""Stubs for ``mixedtape._mixedtape.checksums``."""

from . import streaming as streaming

__all__ = ["sha256_data", "streaming", "xxh3_data"]

def sha256_data(data: bytes) -> str:
    """Compute the SHA-256-style digest of a byte string.

    .. note::
       Placeholder (FNV-1a) for the prototype; swap in a real
       SHA-256 before relying on it.

    :param data: The bytes to hash.
    :returns: Lowercase hex digest.
    """

def xxh3_data(data: bytes) -> int:
    """Compute a 64-bit XXH3-style hash of a byte string.

    .. note::
       Placeholder (SipHash); swap in real XXH3 before relying on it.

    :param data: The bytes to hash.
    :returns: The hash as an unsigned 64-bit integer.
    """
