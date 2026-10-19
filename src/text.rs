//! Text-similarity helpers exposed to Python.
//!
//! These are pure functions over strings with no Python-specific logic in
//! their core; the PyO3 wrappers are thin.

use pyo3::prelude::*;
use std::collections::HashSet;

/// Compute the Levenshtein edit distance between two strings.
///
/// The distance is the minimum number of single-character insertions,
/// deletions, and substitutions required to turn ``a`` into ``b``.
///
/// :param a: First string.
/// :param b: Second string.
/// :returns: The edit distance as a non-negative integer.
///
/// >>> from mixedtape._mixedtape import levenshtein
/// >>> levenshtein("kitten", "sitting")
/// 3
#[pyfunction]
pub fn levenshtein(a: &str, b: &str) -> usize {
    lev(a, b)
}

/// Split text into word ``n``-gram *shingles* for similarity comparison.
///
/// Words are lowercased and split on whitespace. The result is a sorted
/// list of unique shingles, each a space-joined ``n``-gram of words.
///
/// :param text: The input text.
/// :param n: Shingle size (must be at least 1).
/// :returns: Sorted list of unique shingles.
/// :raises ValueError: if ``n`` is 0.
///
/// >>> from mixedtape._mixedtape import shingle
/// >>> shingle("the quick brown fox", 2)
/// ['quick brown', 'the quick', 'brown fox']  # sorted: ['brown fox', ...]
#[pyfunction]
#[pyo3(signature = (text, n))]
pub fn shingle(text: &str, n: usize) -> PyResult<Vec<String>> {
    if n == 0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "shingle size must be at least 1",
        ));
    }
    let words: Vec<String> = text.split_whitespace().map(|w| w.to_lowercase()).collect();
    let mut out: Vec<String> = shingle_words(&words, n).into_iter().collect();
    out.sort();
    Ok(out)
}

/// Pure-Rust core of [`levenshtein`], testable without a Python runtime.
pub(crate) fn lev(a: &str, b: &str) -> usize {
    let b_chars: Vec<char> = b.chars().collect();
    let mut prev: Vec<usize> = (0..=b_chars.len()).collect();
    let mut curr = vec![0usize; b_chars.len() + 1];

    for (i, ca) in a.chars().enumerate() {
        curr[0] = i + 1;
        for (j, cb) in b_chars.iter().enumerate() {
            let cost = usize::from(ca != *cb);
            curr[j + 1] = (prev[j] + cost).min(prev[j + 1] + 1).min(curr[j] + 1);
        }
        std::mem::swap(&mut prev, &mut curr);
    }
    prev[b_chars.len()]
}

/// Pure-Rust core of [`shingle`], testable without a Python runtime.
pub(crate) fn shingle_words(words: &[String], n: usize) -> HashSet<String> {
    if words.len() < n {
        return HashSet::new();
    }
    words
        .windows(n)
        .map(|w| w.join(" "))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lev_identical() {
        assert_eq!(lev("abc", "abc"), 0);
    }

    #[test]
    fn lev_classic() {
        assert_eq!(lev("kitten", "sitting"), 3);
    }

    #[test]
    fn lev_empty() {
        assert_eq!(lev("", "abc"), 3);
        assert_eq!(lev("abc", ""), 3);
        assert_eq!(lev("", ""), 0);
    }

    #[test]
    fn lev_unicode() {
        assert_eq!(lev("café", "cafe"), 1);
    }

    fn words(text: &str) -> Vec<String> {
        text.split_whitespace().map(str::to_string).collect()
    }

    #[test]
    fn shingles_bigrams() {
        let got = shingle_words(&words("a b c"), 2);
        assert_eq!(got.len(), 2);
        assert!(got.contains("a b"));
        assert!(got.contains("b c"));
    }

    #[test]
    fn shingles_too_short() {
        assert!(shingle_words(&words("a"), 2).is_empty());
    }

    #[test]
    fn shingles_dedupe() {
        let got = shingle_words(&words("a b a b"), 2);
        assert_eq!(got.len(), 2);
    }
}
