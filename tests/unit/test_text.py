"""Tests for mixedtape.text, the partially-oxidized module.

Rust members and python members are exercised through the single public
path; the tests don't care which language wrote which.
"""

import threading
import time

import pytest

from mixedtape.text import (
    MAX_RATIO,
    levenshtein,
    levenshtein_batch,
    shingle,
    similarity_ratio,
)


class TestLevenshtein:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            ("", "", 0),
            ("abc", "abc", 0),
            ("kitten", "sitting", 3),
            ("", "abc", 3),
            ("abc", "", 3),
            ("café", "cafe", 1),
        ],
    )
    def test_distances(self, a, b, expected):
        assert levenshtein(a, b) == expected

    def test_symmetry(self):
        assert levenshtein("flaw", "lawn") == levenshtein("lawn", "flaw")


class TestShingle:
    def test_bigrams_sorted_unique(self):
        assert shingle("the quick brown fox", 2) == [
            "brown fox",
            "quick brown",
            "the quick",
        ]

    def test_unigrams(self):
        assert shingle("b a b", 1) == ["a", "b"]

    def test_lowercases(self):
        assert shingle("The THE", 1) == ["the"]

    def test_too_short(self):
        assert shingle("one", 2) == []

    def test_zero_n_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            shingle("text", 0)


class TestLevenshteinBatch:
    def test_matches_scalar(self):
        pairs = [("kitten", "sitting"), ("abc", "abc"), ("", "abc"), ("café", "cafe")]
        assert levenshtein_batch(pairs) == [levenshtein(a, b) for a, b in pairs]

    def test_empty(self):
        assert levenshtein_batch([]) == []

    def test_order_preserved(self):
        # parallelism must not reorder results
        pairs = [("a" * i, "a" * (5 - i)) for i in range(6)]
        assert levenshtein_batch(pairs) == [abs(5 - 2 * i) for i in range(6)]

    def test_releases_gil(self):
        # A background thread's batch call must be able to *complete* —
        # returning from rust into python requires reacquiring the GIL —
        # while another thread is still deep inside a much larger batch.
        # That handover is only possible if the large call released the
        # GIL via py.detach.
        #
        # (Two traps this avoids: a pure-python spinner creeps forward
        # even without detach because of CPython's GIL switch interval;
        # and the ordering must be forced — the small call has to enter
        # rust *after* the big call has started, or it finishes before
        # the contention exists.)
        big = [("x" * 400, "y" * 400)] * 4000  # ~1.5s of rust work
        finished: list[str] = []  # completion order, appended under the GIL

        def big_worker():
            levenshtein_batch(big)
            finished.append("big")

        def small_worker():
            levenshtein_batch([("a", "b")])
            finished.append("small")

        big_t = threading.Thread(target=big_worker)
        big_t.start()
        time.sleep(0.05)  # big call is now inside the rust work
        small_t = threading.Thread(target=small_worker)
        small_t.start()

        small_t.join(timeout=30)
        big_t.join(timeout=30)

        assert finished == ["small", "big"], (
            f"completion order was {finished} — the small call could not "
            "return while the big call ran; is the GIL released (py.detach) "
            "during rust work?"
        )


class TestSimilarityRatio:
    """The still-python member of the module."""

    def test_identical(self):
        assert similarity_ratio("abc", "abc") == MAX_RATIO

    def test_completely_different(self):
        assert similarity_ratio("abc", "xyz") == 0.0

    def test_empty(self):
        assert similarity_ratio("", "") == MAX_RATIO

    def test_partial(self):
        assert similarity_ratio("kitten", "sitting") == pytest.approx(1 - 3 / 7)

    def test_bounds(self):
        assert 0.0 <= similarity_ratio("hello", "world") <= MAX_RATIO


class TestModuleShape:
    def test_mixed_provenance_single_namespace(self):
        # python-side member and rust-side members share one namespace
        from mixedtape import text

        assert text.similarity_ratio.__module__ == "mixedtape.text"
        assert text.levenshtein.__module__ == "mixedtape._mixedtape"
        assert text.MAX_RATIO == 1.0
