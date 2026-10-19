"""mixedtape: a feasibility playground for mixed Python/Rust packaging."""

try:
    from mixedtape._mixedtape import __version__
except ImportError:  # pragma: no cover - running from an unbuilt tree
    __version__ = "0.0.0.dev0+unknown"

__all__ = ["__version__"]
