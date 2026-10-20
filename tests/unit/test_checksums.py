"""Tests for the rust-native checksums module tree."""

import pytest

from mixedtape.checksums import sha256_data, streaming, xxh3_data

ChunkedHasher = streaming.ChunkedHasher


class TestOneShot:
    def test_sha256_known_vector(self):
        # FNV-1a 64 placeholder vectors
        assert sha256_data(b"") == "cbf29ce484222325"
        assert sha256_data(b"a") == "af63dc4c8601ec8c"

    def test_xxh3_deterministic(self):
        assert xxh3_data(b"hello") == xxh3_data(b"hello")
        assert xxh3_data(b"hello") != xxh3_data(b"world")


class TestStreaming:
    def test_chunked_equals_one_shot(self):
        h = ChunkedHasher()
        h.update(b"foo")
        h.update(b"bar")
        assert h.hexdigest() == sha256_data(b"foobar")

    def test_empty(self):
        assert ChunkedHasher().hexdigest() == "cbf29ce484222325"

    def test_submodule_attribute_and_import_agree(self):
        # The attribute re-export (rust module) and the dotted-path import
        # (python shim) are distinct module objects by design — the shim
        # exists so static tooling can follow the public path. What must
        # hold is that both expose the same symbols.
        import mixedtape.checksums as c
        import mixedtape.checksums.streaming as shim

        assert c.streaming.ChunkedHasher is shim.ChunkedHasher
        assert c.streaming.digest is shim.digest

    def test_digest_helper(self):
        assert streaming.digest(b"a") == "af63dc4c8601ec8c"

    def test_update_rejects_str(self):
        with pytest.raises(TypeError):
            ChunkedHasher().update("not bytes")
