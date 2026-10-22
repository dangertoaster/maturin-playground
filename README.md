# maturin-playground

Feasibility test for a mixed Python/Rust package built with
[maturin](https://www.maturin.rs/), in the shape of a small library of
string and hashing helpers.

## Layout

```
Cargo.toml                 # rust crate; version here drives the wheel version
build.rs                   # derives MIXEDTAPE_VERSION from `git describe`
src/                       # rust sources (cargo's conventional location)
  lib.rs                   # #[pymodule] _mixedtape (crate root)
  util.rs                  # register(): shared submodule registration helper
  checksums.rs             # checksums module + nested streaming submodule
  text.rs                  # native text helpers (levenshtein, shingle)
mixedtape/                 # python package
  __init__.py              # __version__ comes from the extension
  _mixedtape/              # type stubs mirroring the rust module tree
  checksums/               # public package; streaming.py shims the rust module
  text.py                  # partially oxidized: rust hot paths + python conveniences
tests/unit/                # pytest: unit tests
tests/integration/         # pytest: import-form conformance + LSP hover tests
tests/lsp/                 # self-contained headless neovim config + hover probe
docs/                      # sphinx docs (canonical-sphinx theme); `make docs-build`
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

`mixedtape.text` is partially oxidized: its hot paths are Rust, the rest
is still Python. The public module (`mixedtape/text.py`) imports the
rust members from the extension and defines the remainder in place:

```python
from mixedtape._mixedtape import levenshtein, shingle  # rust

MAX_RATIO = 1.0  # python


def similarity_ratio(a: str, b: str) -> float:  # python, builds on rust
    ...
```

- **Consumers** import everything from `mixedtape.text`; which language
  implements a given member is invisible at the import site (and only
  shows in introspection, e.g. `levenshtein.__module__`).
- **Maintainers** oxidize one member at a time — the realistic shape for
  gradually porting a large module — without moving anything in the
  public namespace. Tests exercise the module through the public path
  only (`tests/unit/test_text.py`), including a check that the
  provenance split stays as expected.

## Parallelism

CPU-bound batch work uses [rayon](https://docs.rs/rayon):
`levenshtein_batch` parallelizes pairwise distances across a thread pool
and releases the GIL for the duration (`py.detach`), so python threads
stay live during native work. The pattern to copy when adding parallel
entry points:

1. Pure-rust core taking owned data (`lev_batch` in `src/text.rs`) —
   testable with `cargo test`, benchmarkable, no pyo3 in the loop.
2. A thin `#[pyfunction]` that extracts python values into owned rust
   data, then `py.detach(|| core(...))`.
3. Thread count follows `RAYON_NUM_THREADS`; no python-side knob.

`tests/unit/test_text.py::TestLevenshteinBatch::test_releases_gil`
proves the GIL handover (a small call on another thread must complete
while a large one is running) and is mutation-checked: removing the
`py.detach` makes it fail.

## Native module tree

The extension (`mixedtape._mixedtape`) can be arbitrarily deep. The root
pymodule's `#[pymodule_init]` makes a single call,
`m.register_submodules("mixedtape._mixedtape")` (a `util` trait method on
`Bound<PyModule>`), which walks the module tree recursively and, for every
module, inserts it into `sys.modules` under its dotted name (working
around [PyO3#759](https://github.com/PyO3/pyo3/issues/759)), sets
`__name__` and `__package__`, and rewrites members' `__module__` to the
dotted python path. Dotted names are computed from attribute names — the
same source of truth the import system uses — so no per-module path
strings exist to drift out of sync with the code.

Adding a new rust submodule at any depth requires exactly two things:
declare the `#[pymodule]`, and make it reachable from the root via
`#[pymodule_export] use` in its parent. No registration code, no
boilerplate. Classes additionally declare `#[pyclass(module = "...")]`
so pickle/repr use the right name from birth (macro attributes can't
call helpers, so this one literal remains).

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

## Benchmarks

Performance regression benchmarks live in
[`benches/perf.rs`](benches/perf.rs), using
[criterion](https://benches.rs) (the standard rust benchmarking harness).
That file is the reference for how to write new ones — group related
benchmarks, parameterize by input size with `BenchmarkId`, and register
in the `criterion_group!` at the bottom.

```
make bench                                # run all benchmarks
cargo bench -- --save-baseline main       # snapshot before a change
cargo bench -- --baseline main            # compare after
```

CI smoke-runs the benchmarks (`cargo bench -- --test`) so they can't
silently stop compiling; real regression comparisons are a local/PR
workflow via baselines.

## Documentation

Sphinx docs live in `docs/`, built the RTD way (sphinx +
[canonical-sphinx](https://github.com/canonical/canonical-sphinx),
starbase-style scaffold). The point of interest here: autodoc documents
the **Rust** functions too — pyo3 turns `///` rustdoc comments into
runtime `__doc__` strings on the compiled module, so the oxidized
members render with signatures, `:param:` fields and doctests straight
from `src/*.rs`, no stubs or duplication. See for yourself:

```
make docs-build
open docs/_build/index.html   # reference/text: levenshtein et al. are Rust
```

Deps come from the `docs` extra in `pyproject.toml`
(`docs/requirements.txt` mirrors it for a future RTD project). Also
available: `make docs-auto` (live reload), `make docs-lint`,
`make docs-clean`.

## Linting

`make lint` runs the same static checks as CI: `ruff check`, `ruff
format --check`, `ty check`, and `clippy --all-targets -- -D warnings`.
All with default configuration.

## Getting started

```
make setup   # uv sync incl. dev tools (pytest, ty)
make build   # maturin develop: compile the rust extension into .venv
make test    # cargo test + pytest (incl. LSP hover tests)
```
