"""Architecture and platform conditionals, craft-grammar style.

Provides helpers for evaluating "on <arch>" / "to <arch>" style
conditionals found in project files.
"""

from __future__ import annotations

import re

_SELECTOR_RE = re.compile(r"^(on|to)\s+([a-z0-9_-]+)$")


def parse_selector(text: str) -> tuple[str, str] | None:
    """Parse a selector string into a (verb, arch) tuple.

    :param text: e.g. ``"on amd64"`` or ``"to riscv64"``.
    :returns: ``("on", "amd64")`` etc., or ``None`` if malformed.
    """
    match = _SELECTOR_RE.match(text.strip())
    if match is None:
        return None
    return match.group(1), match.group(2)


def matches(selector: str, arch: str, *, verb: str = "on") -> bool:
    """Return True if ``selector`` is a valid selector matching ``arch``.

    :param selector: Raw selector text from a project file.
    :param arch: The architecture to test against.
    :param verb: Which selector verb to require (default ``"on"``).
    """
    parsed = parse_selector(selector)
    return parsed is not None and parsed == (verb, arch)
