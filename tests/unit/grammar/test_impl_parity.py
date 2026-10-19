"""Parity tests: the Rust and Python grammar implementations must agree.

``mixedtape.grammar`` re-exports whichever implementation is available;
these tests pin down that the two implementations are interchangeable by
exercising both explicitly.
"""

import pytest

from mixedtape._mixedtape import grammar_rs
from mixedtape.grammar import _arch as py_impl

SELECTOR_CASES = [
    "on amd64",
    "to riscv64",
    "  on   arm64  ",
    "on loong-arch64",
    "",
    "on",
    "amd64",
    "from amd64",
    "on AMD64",
    "on amd64 extra",
    "on arm_v7",
]


@pytest.mark.parametrize("text", SELECTOR_CASES)
def test_parse_selector_parity(text):
    rust = grammar_rs.parse_selector(text)
    py = py_impl.parse_selector(text)
    assert rust == py


@pytest.mark.parametrize("text", SELECTOR_CASES)
@pytest.mark.parametrize("arch", ["amd64", "arm64"])
@pytest.mark.parametrize("verb", ["on", "to"])
def test_matches_parity(text, arch, verb):
    assert grammar_rs.matches(text, arch, verb=verb) == py_impl.matches(
        text, arch, verb=verb
    )


def test_public_package_prefers_rust():
    """When the extension is built, the public API should use it."""
    import mixedtape.grammar

    assert mixedtape.grammar.parse_selector is grammar_rs.parse_selector
    assert mixedtape.grammar.matches is grammar_rs.matches
