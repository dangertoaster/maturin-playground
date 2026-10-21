"""Import-form conformance tests for the rust extension's module tree.

Every import form a downstream consumer might write is exercised at every
level of the native module tree (private and public paths), and resolved
symbols are checked for fully-qualified ``__module__``/``__package__`` so
IDEs, ``help()``, pickle, and sphinx all see the real python paths.

These live under tests/integration (not tests/unit) because they exercise
the *installed* extension's import machinery end to end.
"""

import importlib
import sys

import pytest


class TestExtensionRoot:
    def test_plain_import(self):
        import mixedtape._mixedtape as ext

        assert isinstance(ext.levenshtein("a", "b"), int)
        assert isinstance(ext.__version__, str)

    def test_from_import_functions(self):
        from mixedtape._mixedtape import levenshtein, shingle, version

        assert levenshtein("kitten", "sitting") == 3
        assert shingle("a b", 1) == ["a", "b"]
        assert isinstance(version(), str)

    def test_from_import_submodules(self):
        from mixedtape._mixedtape import checksums, grammar_rs

        assert grammar_rs.parse_selector("on amd64") == ("on", "amd64")
        assert checksums.sha256_data(b"a") == "af63dc4c8601ec8c"


class TestGrammarRsSubmodule:
    def test_dotted_import(self):
        import mixedtape._mixedtape.grammar_rs as g

        assert g.matches("on arm64", "arm64")

    def test_from_import(self):
        from mixedtape._mixedtape.grammar_rs import matches, parse_selector

        assert parse_selector("bogus") is None
        assert matches("to riscv64", "riscv64", verb="to")


class TestChecksumsSubmodule:
    """A submodule with its own functions AND a further-nested submodule."""

    def test_dotted_import(self):
        import mixedtape._mixedtape.checksums as c

        assert c.sha256_data(b"") == "cbf29ce484222325"
        assert isinstance(c.xxh3_data(b"x"), int)

    def test_from_import_functions(self):
        from mixedtape._mixedtape.checksums import sha256_data, xxh3_data

        assert sha256_data(b"a") == "af63dc4c8601ec8c"
        assert isinstance(xxh3_data(b""), int)

    def test_from_import_nested_submodule(self):
        from mixedtape._mixedtape.checksums import streaming

        assert streaming.digest(b"a") == "af63dc4c8601ec8c"


class TestStreamingSubmodule:
    """Two levels deep: mixedtape._mixedtape.checksums.streaming."""

    def test_dotted_import(self):
        import mixedtape._mixedtape.checksums.streaming as s

        h = s.ChunkedHasher()
        h.update(b"foo")
        h.update(b"bar")
        assert h.hexdigest() == s.digest(b"foobar")

    def test_from_import(self):
        from mixedtape._mixedtape.checksums.streaming import ChunkedHasher, digest

        h = ChunkedHasher()
        h.update(b"a")
        assert h.hexdigest() == digest(b"a")

    def test_deep_import_binds_top_level_name(self):
        # `import x.y.z.w` must bind `x` in the local namespace
        import mixedtape._mixedtape.checksums.streaming

        assert (
            mixedtape._mixedtape.checksums.streaming.digest(b"a") == "af63dc4c8601ec8c"
        )

    def test_deep_first_import_in_fresh_interpreter(self):
        # The hardest case: the deepest module is imported before anything
        # else has touched the package. Extension modules cannot be
        # reloaded in-process, so this must run in a fresh interpreter.
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import mixedtape._mixedtape.checksums.streaming as s; "
                    "assert s.digest(b'a') == 'af63dc4c8601ec8c'; "
                    "import mixedtape._mixedtape.checksums as c; "
                    "assert c.streaming is s"
                ),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr


class TestPublicPaths:
    """Oxidation must be an invisible implementation detail: the public
    paths support the same import forms as the private rust tree."""

    def test_from_import_function_and_submodule(self):
        from mixedtape.checksums import sha256_data, streaming

        assert sha256_data(b"a") == "af63dc4c8601ec8c"
        assert streaming.digest(b"a") == "af63dc4c8601ec8c"

    def test_public_dotted_import(self):
        import mixedtape.checksums.streaming as s

        assert s.ChunkedHasher is not None

    def test_public_from_import_deep(self):
        from mixedtape.checksums.streaming import ChunkedHasher

        h = ChunkedHasher()
        h.update(b"a")
        assert h.hexdigest() == "af63dc4c8601ec8c"

    def test_public_shim_exposes_identical_objects(self):
        import mixedtape._mixedtape.checksums.streaming as priv
        import mixedtape.checksums.streaming as pub

        assert pub.ChunkedHasher is priv.ChunkedHasher
        assert pub.digest is priv.digest


@pytest.mark.parametrize(
    ("path", "member"),
    [
        ("mixedtape._mixedtape", "levenshtein"),
        ("mixedtape._mixedtape.grammar_rs", "parse_selector"),
        ("mixedtape._mixedtape.checksums", "sha256_data"),
        ("mixedtape._mixedtape.checksums.streaming", "digest"),
        ("mixedtape._mixedtape.checksums.streaming", "ChunkedHasher"),
    ],
)
def test_module_attribute_is_fully_qualified(path, member):
    obj = getattr(importlib.import_module(path), member)
    assert obj.__module__ == path


@pytest.mark.parametrize(
    ("path", "expected_package"),
    [
        ("mixedtape._mixedtape", "mixedtape"),
        ("mixedtape._mixedtape.grammar_rs", "mixedtape._mixedtape"),
        ("mixedtape._mixedtape.checksums", "mixedtape._mixedtape"),
        (
            "mixedtape._mixedtape.checksums.streaming",
            "mixedtape._mixedtape.checksums",
        ),
    ],
)
def test_package_attribute(path, expected_package):
    assert importlib.import_module(path).__package__ == expected_package


@pytest.mark.parametrize(
    "path",
    [
        "mixedtape._mixedtape",
        "mixedtape._mixedtape.grammar_rs",
        "mixedtape._mixedtape.checksums",
        "mixedtape._mixedtape.checksums.streaming",
    ],
)
def test_sys_modules_registration(path):
    import mixedtape  # noqa: F401 - importing the package registers the tree

    assert path in sys.modules


@pytest.mark.parametrize(
    "path",
    [
        "mixedtape._mixedtape",
        "mixedtape._mixedtape.grammar_rs",
        "mixedtape._mixedtape.checksums",
        "mixedtape._mixedtape.checksums.streaming",
    ],
)
def test_module_name_is_fully_qualified(path):
    # PyO3 creates nested pymodules with the bare rust name ("streaming");
    # registration must rewrite __name__ to the dotted path.
    assert importlib.import_module(path).__name__ == path


def test_import_forms_return_identical_module():
    import mixedtape._mixedtape.checksums.streaming as s1
    from mixedtape._mixedtape.checksums import streaming as s2

    s3 = importlib.import_module("mixedtape._mixedtape.checksums.streaming")
    assert s1 is s2 is s3


def test_public_api_unchanged():
    import mixedtape
    from mixedtape.grammar import matches, parse_selector

    assert isinstance(mixedtape.__version__, str)
    assert parse_selector("on amd64") == ("on", "amd64")
    assert matches("on arm64", "arm64")
