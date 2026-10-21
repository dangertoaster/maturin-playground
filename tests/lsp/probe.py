"""Scratch file used to smoke-test LSP hover over mixedtape symbols."""

from mixedtape._mixedtape import levenshtein, shingle
from mixedtape.checksums import sha256_data, streaming
from mixedtape.checksums.streaming import ChunkedHasher
from mixedtape.grammar import matches, parse_selector

d = levenshtein("kitten", "sitting")
s = shingle("the quick brown fox", 2)
p = parse_selector("on amd64")
m = matches("on amd64", "amd64")
h = sha256_data(b"abc")
c = ChunkedHasher()
c.update(b"abc")
_ = streaming.digest(b"abc")
