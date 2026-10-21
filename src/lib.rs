//! Native extension module for mixedtape.
//!
//! Compiled to `mixedtape._mixedtape`. The public Python API re-exports
//! selected pieces of this module; each submodule self-registers via
//! [`util::register`] from its own `#[pymodule_init]`, so this root
//! module only has to name its children — never their contents.

use pyo3::prelude::*;

pub mod checksums;
pub mod text;
mod util;

/// The mixedtape native extension.
///
/// This module is private; import from ``mixedtape`` or one of its
/// subpackages instead of using it directly.
#[pymodule(name = "_mixedtape")]
mod mixedtape {
    use super::*;

    #[pymodule_export]
    use text::levenshtein;

    #[pymodule_export]
    use text::levenshtein_batch;

    #[pymodule_export]
    use text::shingle;

    #[pymodule_export]
    use checksums::checksums;

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
        use crate::util::RegisterSubmodules as _;

        m.add("__version__", env!("MIXEDTAPE_VERSION"))?;
        m.register_submodules("mixedtape._mixedtape")
    }
}
