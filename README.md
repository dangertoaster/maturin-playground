# maturin-playground

Feasibility test for a mixed Python/Rust package built with
[maturin](https://www.maturin.rs/), in the shape of a small craft-style
library (`mixedtape`, with `grammar` and `platform` submodules).

## Layout

```
Cargo.toml                 # rust crate; version here drives the wheel version
build.rs                   # derives MIXEDTAPE_VERSION from `git describe`
src/                       # rust sources (cargo's conventional location)
  lib.rs                   # #[pymodule] _mixedtape (crate root)
  util.rs                  # register(): shared submodule registration helper
  grammar_rs.rs            # rust acceleration for mixedtape.grammar
  checksums.rs             # checksums module + nested streaming submodule
  text.rs                  # native text helpers (levenshtein, shingle)
mixedtape/                 # python package
  __init__.py              # __version__ comes from the extension
  _mixedtape/              # type stubs mirroring the rust module tree
  checksums/               # public package; streaming.py shims the rust module
  grammar/                 # partially oxidized: rust fast path + py fallback
  platform/                # pure python
tests/unit/                # pytest: unit + rust/python parity tests
tests/integration/         # pytest: import-form conformance + LSP hover tests
tests/lsp/                 # self-contained headless neovim config + hover probe
```

## Versioning

`setuptools_scm` is **not** used. Instead:

- The wheel/sdist version comes from `package.version` in `Cargo.toml`
  (maturin merges it into the PEP 621 metadata). Bump it to `X.Y.Z` when
  tagging `vX.Y.Z` — the same discipline used by ruff and uv.
- The runtime `mixedtape.__version__` is compiled into the extension by
  `build.rs` from `git describe --tags --long --dirty`, normalized to
  PEP 440 (`0.2.0`, `0.2.0.dev3+gdeadbee`, `…​.dirty`). Dev builds
  therefore always report an exact, tag-derived version.

## Partial oxidation pattern

`mixedtape.grammar` is partially oxidized. The public package
(`grammar/__init__.py`) does:

```python
try:
    from mixedtape._mixedtape.grammar_rs import matches, parse_selector  # rust
except ImportError:
    from mixedtape.grammar._arch import matches, parse_selector  # python
```

- **Consumers** import from `mixedtape.grammar` and get the fastest
  available implementation; the signatures and behaviour are identical.
- **Maintainers** keep both implementations in tree: the Rust one in
  `src/grammar_rs.rs`, the Python reference in
  `mixedtape/grammar/_arch.py`. Parity is enforced by
  `tests/unit/grammar/test_impl_parity.py`, which runs the same cases
  against both.

## Native module tree

The extension (`mixedtape._mixedtape`) can be arbitrarily deep. Every
rust `#[pymodule]` self-registers from its own `#[pymodule_init]` with a
one-line call to `util::register(m, "<fully.qualified.python.name>")`,
which handles the `sys.modules` insertion (working around
[PyO3#759](https://github.com/PyO3/pyo3/issues/759)), sets `__package__`,
and rewrites members' `__module__` to the dotted python path. Parents
only name their children (`#[pymodule_export] use checksums::checksums;`)
— never their contents — and nesting works bottom-up with no recursive
glue. Classes additionally declare `#[pyclass(module = "...")]` so
pickle/repr use the right name from birth.

Oxidation is invisible to consumers: every import form that would work
for a pure-python package works against the native tree, on both the
private path and (via thin shim modules like
`mixedtape/checksums/streaming.py`) the public one. This is verified
exhaustively by `tests/integration/test_import_forms.py`.

## Testing strategy

Two complementary suites, wired together in the `Makefile`:

- `make test-rust` (`cargo test`): unit tests for the pure-Rust cores in
  `src/*.rs` — fast, no Python runtime required.
- `make test-python` (`pytest`): the full Python suite, including tests
  that exercise the compiled extension directly
  (`tests/unit/test_native_text.py`) and the parity tests above.
  Requires `make build` (`maturin develop`) first.
- LSP hover smoke tests (`tests/integration/test_lsp_hover.py`, part of
  the pytest run): spawn headless neovim with the self-contained config
  in `tests/lsp/nvim/` and the `ty` language server from the project
  venv (installed by `make setup`), and assert that docstrings from the
  Rust extension (via its `.pyi` stubs) render on hover. Skip cleanly if
  `nvim` (≥ 0.11) is not installed.

## Getting started

```
make setup   # uv sync incl. dev tools (pytest, ty)
make build   # maturin develop: compile the rust extension into .venv
make test    # cargo test + pytest (incl. LSP hover tests)
```
