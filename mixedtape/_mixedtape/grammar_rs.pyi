"""Stubs for ``mixedtape._mixedtape.grammar_rs``.

Rust-accelerated implementations of the pure-Python functions in
``mixedtape.grammar``. Signature- and behaviour-compatible drop-ins.
"""

def parse_selector(text: str) -> tuple[str, str] | None:
    """Parse a selector string into a ``(verb, arch)`` tuple.

    :param text: e.g. ``"on amd64"`` or ``"to riscv64"``.
    :returns: ``("on", "amd64")`` etc., or ``None`` if malformed.
    """
    ...

def matches(selector: str, arch: str, *, verb: str = "on") -> bool:
    """Return True if ``selector`` is a valid selector matching ``arch``.

    :param selector: Raw selector text from a project file.
    :param arch: The architecture to test against.
    :param verb: Which selector verb to require (default ``"on"``).
    """
    ...
