"""Type stubs for the ``mixedtape._mixedtape`` native extension.

This module is private; downstream consumers should import from
``mixedtape.text`` or ``mixedtape.checksums`` instead.
"""

from collections.abc import Sequence

__version__: str

def version() -> str:
    """The package version, derived from ``git describe`` at compile time.

    :returns: PEP 440 version string, e.g. ``"0.2.0"`` or
        ``"0.2.0.dev3+gdeadbee"`` between tags.
    """

def levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between two strings.

    The distance is the minimum number of single-character insertions,
    deletions, and substitutions required to turn ``a`` into ``b``.

    :param a: First string.
    :param b: Second string.
    :returns: The edit distance as a non-negative integer.
    """

def levenshtein_batch(pairs: Sequence[tuple[str, str]]) -> list[int]:
    """Compute Levenshtein distances for many string pairs in parallel.

    Pairs are processed on a rayon thread pool; the GIL is released for
    the duration, so python threads (and other native calls) keep running
    while this works. Pool size follows the ``RAYON_NUM_THREADS``
    environment variable, defaulting to the number of CPUs.

    :param pairs: A list of ``(a, b)`` string tuples.
    :returns: Distances as a list of ints, in the same order as ``pairs``.
    """

def shingle(text: str, n: int) -> list[str]:
    """Split text into word ``n``-gram *shingles* for similarity comparison.

    Words are lowercased and split on whitespace. The result is a sorted
    list of unique shingles, each a space-joined ``n``-gram of words.

    :param text: The input text.
    :param n: Shingle size (must be at least 1).
    :returns: Sorted list of unique shingles.
    :raises ValueError: if ``n`` is 0.
    """
