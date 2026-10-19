.PHONY: setup build test test-python test-rust test-lsp clean

#: Install python dev dependencies.
setup:
	uv sync --extra dev

#: Build the rust extension in-place (editable install).
build:
	maturin develop

#: Run the full test suite (python + rust).
test: test-python test-rust

#: Python tests. Requires `make build` first.
test-python:
	uv run --no-sync pytest

#: Rust unit tests (pure-Rust cores, no python runtime needed).
test-rust:
	cargo test

#: Smoke-test that rust-symbol docstrings render in a python LSP.
test-lsp:
	nvim --headless -u NONE -l tests/lsp_hover.lua

clean:
	cargo clean
	rm -rf dist build *.egg-info
