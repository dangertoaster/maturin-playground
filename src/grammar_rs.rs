//! Rust acceleration for `mixedtape.grammar`.
//!
//! Provides drop-in fast paths for the hottest pure-Python functions in
//! `mixedtape.grammar`. The Python package imports this module privately
//! and falls back to its own implementations when the extension is absent
//! (e.g. running from an unbuilt source tree).

use pyo3::prelude::*;

/// Fast grammar primitives.
///
/// Every public function here is signature- and behaviour-compatible with
/// its pure-Python counterpart in :mod:`mixedtape.grammar`.
#[pymodule(submodule)]
pub mod grammar_rs {
    use pyo3::prelude::*;

    /// Parse a selector string into a ``(verb, arch)`` tuple.
    ///
    /// Identical to the pure-Python
    /// :func:`mixedtape.grammar.parse_selector`, but implemented in Rust.
    ///
    /// :param text: e.g. ``"on amd64"`` or ``"to riscv64"``.
    /// :returns: ``("on", "amd64")`` etc., or ``None`` if malformed.
    ///
    /// >>> parse_selector("on amd64")
    /// ('on', 'amd64')
    #[pyfunction]
    fn parse_selector(text: &str) -> Option<(String, String)> {
        super::parse_selector_impl(text)
    }

    /// Return True if ``selector`` is a valid selector matching ``arch``.
    ///
    /// :param selector: Raw selector text from a project file.
    /// :param arch: The architecture to test against.
    /// :param verb: Which selector verb to require (default ``"on"``).
    #[pyfunction]
    #[pyo3(signature = (selector, arch, *, verb = "on"))]
    fn matches(selector: &str, arch: &str, verb: &str) -> bool {
        super::parse_selector_impl(selector)
            .map(|(v, a)| v == verb && a == arch)
            .unwrap_or(false)
    }
}

/// Core selector parser, testable without a Python runtime.
pub(crate) fn parse_selector_impl(text: &str) -> Option<(String, String)> {
    let mut parts = text.split_whitespace();
    let verb = parts.next()?;
    let arch = parts.next()?;
    if parts.next().is_some() {
        return None; // trailing tokens
    }
    if verb != "on" && verb != "to" {
        return None;
    }
    if arch.is_empty()
        || !arch
            .chars()
            .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_' || c == '-')
    {
        return None;
    }
    Some((verb.to_string(), arch.to_string()))
}

#[cfg(test)]
mod tests {
    use super::parse_selector_impl as parse;

    #[test]
    fn parses_valid_selectors() {
        assert_eq!(parse("on amd64"), Some(("on".into(), "amd64".into())));
        assert_eq!(parse("to riscv64"), Some(("to".into(), "riscv64".into())));
        assert_eq!(parse("  on   arm64  "), Some(("on".into(), "arm64".into())));
        assert_eq!(parse("on loong-arch64"), Some(("on".into(), "loong-arch64".into())));
    }

    #[test]
    fn rejects_malformed() {
        assert_eq!(parse(""), None);
        assert_eq!(parse("on"), None);
        assert_eq!(parse("amd64"), None);
        assert_eq!(parse("from amd64"), None);
        assert_eq!(parse("on AMD64"), None);
        assert_eq!(parse("on amd64 extra"), None);
    }
}
