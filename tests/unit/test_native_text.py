"""Tests for the Rust-native text helpers in ``mixedtape._mixedtape``.

These exercise the extension directly. Behavioural equivalence of the
oxidized ``grammar`` functions against their Python fallbacks is covered
in ``tests/unit/grammar/test_impl_parity.py``.
"""

import pytest

from mixedtape._mixedtape import levenshtein, shingle, version


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


class TestVersion:
    def test_matches_package_version(self):
        import mixedtape

        assert version() == mixedtape.__version__
