//! Shared helpers for declaring python submodules in Rust.
//!
//! Workaround machinery for [PyO3#759](https://github.com/PyO3/pyo3/issues/759):
//! `wrap_pymodule!` attaches a nested pymodule to its parent only as an
//! attribute, but `import a.b.c` and `from a.b.c import x` resolve through
//! `sys.modules`. The extension root calls
//! [`RegisterSubmodules::register_submodules`] once from its
//! `#[pymodule_init]`; it walks the whole tree recursively, so nested
//! submodules need no per-module glue at any depth.

use pyo3::prelude::*;
use pyo3::types::PyModule;

/// Recursively register a module tree with python's import machinery.
pub trait RegisterSubmodules {
    /// Register this module and everything nested beneath it.
    ///
    /// For each module in the tree:
    ///
    /// - Inserts it into `sys.modules` under its dotted python name
    ///   (computed from attribute names, the same source of truth the
    ///   import system itself uses) so dotted imports work.
    /// - Sets `__name__` and `__package__` to the dotted paths.
    /// - Rewrites `__module__` on every non-dunder member (functions,
    ///   classes, and any future export kinds) so introspection — IDEs,
    ///   `help()`, sphinx — reports the real python path instead of the
    ///   bare Rust module name.
    ///
    /// Call once from the root pymodule:
    ///
    /// ```ignore
    /// #[pymodule_init]
    /// fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
    ///     m.register_submodules("mixedtape._mixedtape")
    /// }
    /// ```
    ///
    /// Submodules need only be reachable via attribute (e.g. through
    /// `#[pymodule_export] use child;`); their own `#[pymodule_init]`, if
    /// any, is free to do module-specific work and can ignore registration
    /// entirely.
    fn register_submodules(&self, name: &str) -> PyResult<()>;
}

impl RegisterSubmodules for Bound<'_, PyModule> {
    fn register_submodules(&self, name: &str) -> PyResult<()> {
        let sys_modules = self.py().import("sys")?.getattr("modules")?;
        register_recursive(self, name, &sys_modules)
    }
}

fn register_recursive(
    m: &Bound<'_, PyModule>,
    name: &str,
    sys_modules: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let package = match name.rfind('.') {
        Some(idx) => &name[..idx],
        None => "",
    };
    m.setattr("__name__", name)?;
    m.setattr("__package__", package)?;
    sys_modules.set_item(name, m)?;

    for member in m.dir()? {
        let member: String = member.extract()?;
        if member.starts_with("__") {
            continue;
        }
        let attr = m.getattr(&member)?;
        if let Ok(submodule) = attr.cast::<PyModule>() {
            // Recurse into nested modules first; they get their own
            // __module__ context below.
            register_recursive(submodule, &format!("{name}.{member}"), sys_modules)?;
        } else {
            // PyO3 sets each pyfunction's __module__ to the bare Rust module
            // name at creation time; rewrite to the real dotted path.
            // Members that refuse the assignment (e.g. constants) are left
            // as-is. pyclasses declare their own path via
            // #[pyclass(module = "...")] and are simply re-set to the same
            // value here.
            let _ = attr.setattr("__module__", name);
        }
    }
    Ok(())
}
