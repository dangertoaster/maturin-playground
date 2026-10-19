//! Native extension module for mixedtape.
//!
//! Compiled to `mixedtape._mixedtape`. The public Python API re-exports
//! selected pieces of this module; submodules (currently just
//! `grammar_rs`) provide Rust-accelerated implementations that their
//! pure-Python counterparts in `mixedtape` fall back from.

use pyo3::prelude::*;

mod grammar_rs;
mod text;

/// Register a nested pymodule so it behaves like a real submodule.
///
/// `add_wrapped(wrap_pymodule!(...))` attaches a pymodule to its parent
/// only as an *attribute*; `import a.b.c` and `from a.b.c import x`
/// consult `sys.modules` instead. This helper bridges the gap and also
/// fully qualifies each member's `__module__` so introspection (IDEs,
/// `help()`, sphinx) reports the real path rather than the bare Rust
/// module name.
///
/// New submodules only need `register_submodule(m, "<name>")` — no
/// per-member bookkeeping.
fn register_submodule(m: &Bound<'_, PyModule>, name: &str) -> PyResult<()> {
    let py = m.py();
    let package = concat!(env!("CARGO_PKG_NAME"), "._mixedtape");
    let full_name = format!("{package}.{name}");

    let sub = m.getattr(name)?;
    sub.setattr("__package__", package)?;
    for member in sub.dir()? {
        let member: String = member.extract()?;
        // Skip dunders and anything that refuses a __module__ assignment
        // (e.g. module-level constants); only functions/classes matter.
        if member.starts_with("__") {
            continue;
        }
        let _ = sub.getattr(member)?.setattr("__module__", &full_name);
    }

    py.import("sys")?.getattr("modules")?.set_item(full_name, sub)?;
    Ok(())
}

/// The mixedtape native extension.
///
/// This module is private; import from ``mixedtape`` or
/// ``mixedtape.grammar`` instead of using it directly.
#[pymodule]
mod _mixedtape {
    use super::*;

    #[pymodule_export]
    use text::levenshtein;

    #[pymodule_export]
    use text::shingle;

    /// The package version, derived from `git describe` at compile time.
    ///
    /// :returns: PEP 440 version string, e.g. ``"0.2.0"`` or
    ///     ``"0.2.0.dev3+gdeadbee"`` between tags.
    #[pyfunction]
    fn version() -> &'static str {
        env!("MIXEDTAPE_VERSION")
    }

    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add("__version__", env!("MIXEDTAPE_VERSION"))?;

        m.add_wrapped(pyo3::wrap_pymodule!(grammar_rs::grammar_rs))?;
        register_submodule(m, "grammar_rs")?;

        Ok(())
    }
}
