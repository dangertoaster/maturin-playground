"""LSP hover smoke tests: do the rust extension's docstrings render?

Runs the project's self-contained headless neovim config against
``tests/lsp/probe.py`` and asserts that hovering each probed symbol
yields the documentation written in the rust sources / type stubs.

Requires the ``ty`` language server (installed into the project venv by
``make setup``) and a ``nvim`` binary (0.11+). Both are optional
developer tooling; the tests skip cleanly when either is absent.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
NVIM_CONFIG = ROOT / "tests" / "lsp" / "nvim" / "init.lua"
HOVER_SCRIPT = ROOT / "tests" / "lsp" / "hover.lua"
TY = ROOT / ".venv" / "bin" / "ty"

nvim = pytest.mark.skipif(shutil.which("nvim") is None, reason="nvim not installed")
ty = pytest.mark.skipif(not TY.exists(), reason="ty not installed; run `make setup`")


def _nvim_supports_lua_script() -> bool:
    """`nvim -l` requires neovim 0.9+; vim.lsp.config requires 0.11+."""
    try:
        out = subprocess.run(
            ["nvim", "--version"], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return False
    match = re.search(r"NVIM v(\d+)\.(\d+)", out)
    return bool(match) and (int(match.group(1)), int(match.group(2))) >= (0, 11)


def _run_hover() -> dict[str, str]:
    env = {
        **os.environ,
        "MIXEDTAPE_ROOT": str(ROOT),
        "MIXEDTAPE_TY": str(TY),
    }
    result = subprocess.run(
        [
            "nvim",
            "--headless",
            "-u",
            str(NVIM_CONFIG),
            "-l",
            str(HOVER_SCRIPT),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
        timeout=120,
    )
    if result.returncode != 0:
        pytest.fail(
            f"hover runner exited {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    # nvim's print() lands on stdout when attached to a tty and on stderr
    # when piped; the records may be on either stream.
    return _parse_records(result.stdout + result.stderr)


def _parse_records(text: str) -> dict[str, str]:
    records: dict[str, str] = {}
    name: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("=== END"):
            if name is not None:
                records[name] = "\n".join(body).strip()
            name, body = None, []
        elif line.startswith("=== "):
            name = line[4:].strip()
            body = []
        elif name is not None:
            body.append(line)
    return records


@pytest.fixture(scope="module")
def hovers() -> dict[str, str]:
    return _run_hover()


@nvim
@ty
class TestHoverDocs:
    """Each entry maps a probed symbol to a phrase that must appear in
    its hover documentation — proving the docstring survived the
    rust -> pyi -> LSP pipeline."""

    @pytest.fixture(autouse=True)
    def _require_nvim_version(self):
        if not _nvim_supports_lua_script():
            pytest.skip("neovim >= 0.11 required")

    @pytest.mark.parametrize(
        ("symbol", "expected"),
        [
            pytest.param("levenshtein", "Levenshtein edit distance", id="levenshtein"),
            pytest.param("shingle", "shingles", id="shingle"),
            pytest.param("sha256_data", "digest of a byte string", id="sha256_data"),
            pytest.param("streaming", "checksums.streaming", id="streaming"),
            pytest.param(
                "ChunkedHasher", "accepts data incrementally", id="ChunkedHasher"
            ),
        ],
    )
    def test_symbol_hover_contains_docstring(
        self, hovers: dict[str, str], symbol: str, expected: str
    ):
        assert symbol in hovers, f"no hover record for {symbol}"
        assert "<no hover>" not in hovers[symbol]
        assert expected in hovers[symbol]
