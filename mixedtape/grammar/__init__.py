"""Grammar-aware conditional values.

The hot paths (selector parsing and matching) are implemented in Rust in
the private ``mixedtape._mixedtape.grammar_rs`` extension module and
re-exported here under their canonical names. When the extension is not
available — for instance when running directly from an unbuilt source
tree — the pure-Python implementations are used instead, so behaviour is
identical either way.
"""

from mixedtape.grammar._processor import GrammarValue, Statement, apply_statements, walk

try:
    # Rust-accelerated implementations (preferred).
    from mixedtape._mixedtape.grammar_rs import matches, parse_selector
except ImportError:  # pragma: no cover - extension not built
    # Pure-Python fallback.
    from mixedtape.grammar._arch import matches, parse_selector

__all__ = [
    "GrammarValue",
    "Statement",
    "apply_statements",
    "matches",
    "parse_selector",
    "walk",
]
