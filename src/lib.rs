//! Native extension module for mixedtape.
//!
//! Compiled to `mixedtape._mixedtape`. The public Python API re-exports
//! selected pieces of this module; the `grammar` submodule additionally
//! provides Rust-accelerated implementations that the pure-Python
//! `mixedtape.grammar` package falls back from.

use pyo3::prelude::*;

mod grammar_rs;
mod text;

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
        // Register the submodule in sys.modules so that
        // `from mixedtape._mixedtape.grammar_rs import ...` works.
        let py = m.py();
        let full_name = "mixedtape._mixedtape.grammar_rs";
        let submodule = m.getattr("grammar_rs")?;
        submodule.setattr("__package__", "mixedtape._mixedtape")?;
        for fname in ["parse_selector", "matches"] {
            submodule
                .getattr(fname)?
                .setattr("__module__", "mixedtape._mixedtape.grammar_rs")?;
        }
        py.import("sys")?.getattr("modules")?.set_item(full_name, submodule)?;
        Ok(())
    }
}
