"""Grammar processing primitives.

A *processor* is a callable applied to grammar-aware values. This module
provides a small composable framework for walking and transforming nested
grammar statements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Union

#: A grammar value is either a scalar, a list of grammar values, or a
#: dict mapping selectors to grammar values.
GrammarValue = Union[str, int, float, bool, None, list, dict]

ScalarProcessor = Callable[[Union[str, int, float, bool, None]], Any]


@dataclass(frozen=True)
class Statement:
    """A single conditional grammar statement.

    :param selector: The condition under which ``body`` applies
        (e.g. ``"on amd64"``).
    :param body: The value that applies when the selector matches.
    """

    selector: str
    body: GrammarValue

    def applies_to(self, arch: str) -> bool:
        """Return True if this statement's selector matches ``arch``."""
        tokens = self.selector.split()
        return len(tokens) == 2 and tokens[0] == "on" and tokens[1] == arch


def walk(value: GrammarValue, processor: ScalarProcessor) -> list[Any]:
    """Walk a nested grammar value, applying ``processor`` to each scalar.

    Lists are traversed in order; dicts are traversed in insertion order
    of their values. The results are returned as a flat list in traversal
    order.

    :param value: The (possibly nested) grammar value to walk.
    :param processor: Callable applied to every scalar leaf.
    :returns: Flat list of processor results, in traversal order.
    """
    results: list[Any] = []
    if isinstance(value, dict):
        for sub in value.values():
            results.extend(walk(sub, processor))
    elif isinstance(value, list):
        for sub in value:
            results.extend(walk(sub, processor))
    else:
        results.append(processor(value))
    return results


def apply_statements(statements: Iterable[Statement], arch: str) -> list[GrammarValue]:
    """Return the bodies of all statements whose selector matches ``arch``."""
    return [s.body for s in statements if s.applies_to(arch)]
