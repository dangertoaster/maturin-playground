"""Text-similarity helpers.

A partially-oxidized module: the hot paths (``levenshtein``,
``levenshtein_batch``, ``shingle``) are implemented in Rust in
``mixedtape._mixedtape``, while derived conveniences
(``similarity_ratio``) remain plain python. The split is an
implementation detail — everything is imported from ``mixedtape.text``
regardless of which language wrote it.
"""

from mixedtape._mixedtape import levenshtein, levenshtein_batch, shingle

__all__ = [
    "MAX_RATIO",
    "levenshtein",
    "levenshtein_batch",
    "shingle",
    "similarity_ratio",
]

#: Upper bound of :func:`similarity_ratio` scores.
MAX_RATIO = 1.0


def similarity_ratio(a: str, b: str) -> float:
    """Similarity of two strings as a 0.0–1.0 ratio.

    Defined as ``1 - dist / max(len(a), len(b))`` where ``dist`` is the
    Levenshtein distance; identical strings score :data:`MAX_RATIO`.

    :param a: First string.
    :param b: Second string.
    :returns: Similarity ratio in ``[0.0, 1.0]``.
    """
    longest = max(len(a), len(b))
    if longest == 0:
        return MAX_RATIO
    return 1.0 - levenshtein(a, b) / longest
