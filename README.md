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
  grammar_rs.rs            # rust acceleration for mixedtape.grammar
  text.rs                  # native text helpers (levenshtein, shingle)
mixedtape/                 # python package
  __init__.py              # __version__ comes from the extension
  _mixedtape/__init__.pyi  # type stubs for the native module
  _mixedtape/grammar_rs.pyi
  grammar/                 # partially oxidized: rust fast path + py fallback
  platform/                # pure python
tests/                     # pytest suite (unit + rust/python parity tests)
tests/lsp_hover.lua        # headless neovim probe: do rust docstrings render?
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

## Testing strategy

Two complementary suites, wired together in the `Makefile`:

- `make test-rust` (`cargo test`): unit tests for the pure-Rust cores in
  `src/*.rs` — fast, no Python runtime required.
- `make test-python` (`pytest`): the full Python suite, including tests
  that exercise the compiled extension directly
  (`tests/unit/test_native_text.py`) and the parity tests above.
  Requires `make build` (`maturin develop`) first.
- `make test-lsp`: optional smoke test that opens a probe file in
  headless neovim with the `ty` language server and confirms docstrings
  from the Rust extension (via its `.pyi` stubs) render on hover.
