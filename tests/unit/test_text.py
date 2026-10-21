"""Tests for mixedtape.text, the partially-oxidized module.

Rust members and python members are exercised through the single public
path; the tests don't care which language wrote which.
"""

import pytest

from mixedtape.text import MAX_RATIO, levenshtein, shingle, similarity_ratio


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
