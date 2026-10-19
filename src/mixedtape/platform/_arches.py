"""Platform and architecture abstractions."""

from __future__ import annotations

from enum import Enum
from typing import Iterable


class Arch(str, Enum):
    """Supported build/run architectures."""

    AMD64 = "amd64"
    ARM64 = "arm64"
    ARMHF = "armhf"
    RISCV64 = "riscv64"
    S390X = "s390x"

    @classmethod
    def from_deb(cls, deb_arch: str) -> "Arch":
        """Look up an :class:`Arch` by its Debian architecture name.

        :param deb_arch: e.g. ``"amd64"``.
        :raises ValueError: if the architecture is unknown.
        """
        try:
            return cls(deb_arch)
        except ValueError:
            raise ValueError(f"unknown architecture: {deb_arch!r}") from None


def filter_arches(arches: Iterable[str], *, supported: set[Arch]) -> list[Arch]:
    """Filter raw arch strings down to the supported subset, preserving order.

    Unknown architectures are dropped silently.

    :param arches: Raw architecture strings (e.g. from a project file).
    :param supported: The set of architectures the caller supports.
    """
    result: list[Arch] = []
    for raw in arches:
        try:
            arch = Arch.from_deb(raw)
        except ValueError:
            continue
        if arch in supported and arch not in result:
            result.append(arch)
    return result
