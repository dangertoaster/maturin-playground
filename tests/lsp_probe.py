"""Scratch file used to smoke-test LSP hover over mixedtape symbols."""

from mixedtape._mixedtape import levenshtein, shingle
from mixedtape.grammar import parse_selector, matches

d = levenshtein("kitten", "sitting")
s = shingle("the quick brown fox", 2)
p = parse_selector("on amd64")
m = matches("on amd64", "amd64")
