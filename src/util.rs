//! Shared helpers for declaring python submodules in Rust.
//!
//! Workaround machinery for [PyO3#759](https://github.com/PyO3/pyo3/issues/759):
//! `wrap_pymodule!` attaches a nested pymodule to its parent only as an
//! attribute, but `import a.b.c` and `from a.b.c import x` resolve through
//! `sys.modules`. Every `#[pymodule]` in this crate calls [`register`] from
//! its own `#[pymodule_init]`, passing its fully-qualified python name, which
//! keeps the glue next to the module it describes and lets arbitrarily deep
//! nesting work without the parent knowing anything about its children.

use pyo3::prelude::*;
use pyo3::types::PyModule;

/// Register a pymodule under its fully-qualified python name.
///
/// - Inserts the module into `sys.modules` so dotted imports work.
/// - Sets `__package__` to the parent path.
/// - Rewrites `__module__` on every non-dunder member (functions, classes,
///   and any future export kinds) so introspection — IDEs, `help()`, sphinx —
///   reports the real python path instead of the bare Rust module name.
///
/// Call from each submodule's `#[pymodule_init]`:
///
/// ```ignore
/// #[pymodule_init]
/// fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
///     crate::util::register(m, "mixedtape._mixedtape.grammar_rs")
/// }
/// ```
pub fn register(m: &Bound<'_, PyModule>, full_name: &str) -> PyResult<()> {
    let package = match full_name.rfind('.') {
        Some(idx) => &full_name[..idx],
        None => "",
    };
    m.setattr("__package__", package)?;

    // PyO3 sets each pyfunction's __module__ to the bare Rust module name
    // (e.g. "grammar_rs") at creation time; rewrite members to the real
    // dotted path so IDEs, help(), and sphinx report sensible names.
    // Dunders are skipped; members that refuse the assignment (e.g.
    // re-exported constants) are left as-is. pyclasses declare their own
    // path via #[pyclass(module = "...")] and are simply re-set to the
    // same value here.
    for member in m.dir()? {
        let member: String = member.extract()?;
        if member.starts_with("__") {
            continue;
        }
        let _ = m.getattr(member)?.setattr("__module__", full_name);
    }

    m.py()
        .import("sys")?
        .getattr("modules")?
        .set_item(full_name, m)?;
    Ok(())
}
