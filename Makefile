.PHONY: setup build test test-python test-rust test-lsp lint clean

#: Create the dev environment: python deps (including the `ty` language
#: server used by the LSP hover tests) installed into .venv.
setup:
	uv sync --extra dev

#: Build the rust extension in-place (editable install).
build:
	maturin develop

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

clean:
	cargo clean
	rm -rf dist build *.egg-info
