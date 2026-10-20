"""Stubs for ``mixedtape._mixedtape.checksums.streaming``."""

__all__ = ["ChunkedHasher", "digest"]

class ChunkedHasher:
    """A hasher that accepts data incrementally."""

    def __init__(self) -> None:
        """Create an empty hasher."""
        ...

    def update(self, data: bytes) -> None:
        """Feed a chunk of data into the hasher.

        :param data: The next chunk of bytes.
        """
        ...

    def hexdigest(self) -> str:
        """Return the hex digest of all data fed so far.

        :returns: Lowercase hex digest.
        """
        ...

def digest(data: bytes) -> str:
    """One-shot helper: digest of ``data`` in a single call.

    :param data: The bytes to hash.
    :returns: Lowercase hex digest.
    """
    ...
