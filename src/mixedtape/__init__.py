"""mixedtape: a feasibility playground for mixed Python/Rust packaging."""

try:
    from mixedtape._version import version as __version__
except ImportError:  # pragma: no cover - not built/installed
    __version__ = "0.0.0.dev0+unknown"

__all__ = ["__version__"]
