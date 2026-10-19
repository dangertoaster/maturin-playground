"""Type stubs for the ``mixedtape._mixedtape`` native extension.

This module is private; downstream consumers should import from
``mixedtape`` or ``mixedtape.grammar`` instead.
"""

__version__: str

def version() -> str:
    """The package version, derived from ``git describe`` at compile time.

    :returns: PEP 440 version string, e.g. ``"0.2.0"`` or
        ``"0.2.0.dev3+gdeadbee"`` between tags.
    """
    ...

def levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between two strings.

    The distance is the minimum number of single-character insertions,
    deletions, and substitutions required to turn ``a`` into ``b``.

    :param a: First string.
    :param b: Second string.
    :returns: The edit distance as a non-negative integer.
    """
    ...

def shingle(text: str, n: int) -> list[str]:
    """Split text into word ``n``-gram *shingles* for similarity comparison.

    Words are lowercased and split on whitespace. The result is a sorted
    list of unique shingles, each a space-joined ``n``-gram of words.

    :param text: The input text.
    :param n: Shingle size (must be at least 1).
    :returns: Sorted list of unique shingles.
    :raises ValueError: if ``n`` is 0.
    """
    ...
