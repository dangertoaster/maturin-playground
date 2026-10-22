# Env vars for the docs Sphinx Stack. The docs Makefile builds with the
# repo-root venv rather than its own.
export DOCS_BUILDDIR ?= _build

.PHONY: setup build test test-python test-rust test-lsp lint clean docs-setup docs-build docs-auto docs-clean docs-lint

#: Create the dev environment: python deps (including the `ty` language
#: server used by the LSP hover tests) installed into .venv.
setup:
	uv sync --extra dev

#: Build the rust extension in-place (editable install).
build:
	uv run --no-sync maturin develop

#: Run the full test suite (python + rust; includes the LSP hover tests).
test: test-python test-rust

#: Python tests. Requires `make build` first. The LSP hover tests need
#: `nvim` (>= 0.11) on PATH and skip cleanly without it.
test-python:
	uv run --no-sync pytest

#: Rust unit tests (pure-Rust cores, no python runtime needed).
test-rust:
	cargo test

#: Just the LSP hover smoke tests.
test-lsp:
	uv run --no-sync pytest tests/integration/test_lsp_hover.py

#: All static checks, same as CI: ruff (lint+format), ty (types), clippy.
lint:
	uv run --no-sync ruff check
	uv run --no-sync ruff format --check
	uv run --no-sync ty check
	cargo clippy --all-targets -- --deny warnings

#: Run the criterion benchmarks (benches/perf.rs). Use
#: `cargo bench -- --save-baseline main` / `--baseline main` to compare
#: a change against main.
bench:
	cargo bench

#: Install the Sphinx toolchain into .venv (the `docs` extra, on top of
#: whatever's already synced).
docs-setup:
	uv sync --extra dev --extra docs

#: Build the docs (HTML) to docs/_build/. Requires the extension to be
#: built (`make build`) so autodoc can import the package and read the
#: pyo3 docstrings out of the native module. Open docs/_build/index.html
#: afterwards.
docs-build:
	$(MAKE) docs-setup
	$(MAKE) build
	DOCS_VENVDIR="$(abspath .venv)" $(MAKE) -C docs html --no-print-directory

#: Build and serve the docs with live reload.
docs-auto:
	$(MAKE) docs-setup
	$(MAKE) build
	DOCS_VENVDIR="$(abspath .venv)" $(MAKE) -C docs run --no-print-directory

#: Remove the built docs.
docs-clean:
	rm -rf docs/_build docs/_dev/.doctrees

#: Lint the docs sources (rst style rules: trailing backslashes, bad
#: hyperlinks, etc.). Distinct from `docs-build`'s sphinx build warnings.
docs-lint:
	$(MAKE) docs-setup
	uv run --no-sync --extra dev --extra docs sphinx-lint docs \
		--ignore docs/_dev --ignore docs/_build --enable all

clean: docs-clean
	cargo clean
	rm -rf dist build *.egg-info
