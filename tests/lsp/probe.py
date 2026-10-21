"""Scratch file used to smoke-test LSP hover over mixedtape symbols."""

from mixedtape._mixedtape import levenshtein, shingle
from mixedtape.checksums import sha256_data, streaming
from mixedtape.checksums.streaming import ChunkedHasher
from mixedtape.text import similarity_ratio

d = levenshtein("kitten", "sitting")
s = shingle("the quick brown fox", 2)
h = sha256_data(b"abc")
c = ChunkedHasher()
c.update(b"abc")
_ = streaming.digest(b"abc")
r = similarity_ratio("kitten", "sitting")
