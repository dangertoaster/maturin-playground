//! Text-similarity helpers exposed to Python.
//!
//! These are pure functions over strings with no Python-specific logic in
//! their core; the PyO3 wrappers are thin.

use pyo3::prelude::*;
use rayon::prelude::*;
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

/// Compute Levenshtein distances for many string pairs in parallel.
///
/// Pairs are processed on a rayon thread pool; the GIL is released for
/// the duration, so python threads (and other native calls) keep running
/// while this works. Pool size follows the ``RAYON_NUM_THREADS``
/// environment variable, defaulting to the number of CPUs.
///
/// :param pairs: A list of ``(a, b)`` string tuples.
/// :returns: Distances as a list of ints, in the same order as ``pairs``.
///
/// >>> from mixedtape._mixedtape import levenshtein_batch
/// >>> levenshtein_batch([("kitten", "sitting"), ("abc", "abc")])
/// [3, 0]
#[pyfunction]
pub fn levenshtein_batch(py: Python<'_>, pairs: Vec<(String, String)>) -> Vec<usize> {
    // Extract python data into owned rust values first (cheap), then
    // release the GIL for the actual work.
    py.detach(|| lev_batch(&pairs))
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
///
/// Public for benches/integration tests; not part of the python API.
pub fn lev(a: &str, b: &str) -> usize {
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
///
/// Public for benches/integration tests; not part of the python API.
pub fn shingle_words(words: &[String], n: usize) -> HashSet<String> {
    if words.len() < n {
        return HashSet::new();
    }
    words
        .windows(n)
        .map(|w| w.join(" "))
        .collect()
}

/// Pure-Rust core of [`levenshtein_batch`]: pairwise distances over a
/// slice of string pairs, parallelized with rayon.
///
/// Public for benches/integration tests; not part of the python API.
pub fn lev_batch(pairs: &[(String, String)]) -> Vec<usize> {
    pairs
        .par_iter()
        .map(|(a, b)| lev(a, b))
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

    fn pairs(items: &[(&str, &str)]) -> Vec<(String, String)> {
        items
            .iter()
            .map(|(a, b)| (a.to_string(), b.to_string()))
            .collect()
    }

    #[test]
    fn lev_batch_matches_scalar() {
        let p = pairs(&[("kitten", "sitting"), ("abc", "abc"), ("", "abc")]);
        let expected: Vec<usize> = p.iter().map(|(a, b)| lev(a, b)).collect();
        assert_eq!(lev_batch(&p), expected);
    }

    #[test]
    fn lev_batch_empty() {
        assert_eq!(lev_batch(&[]), Vec::<usize>::new());
    }

    #[test]
    fn lev_batch_preserves_order() {
        // parallelism must not reorder results
        let p = pairs(&[("aaaa", "a"), ("a", "aaaa"), ("xy", "xy")]);
        assert_eq!(lev_batch(&p), vec![3, 3, 0]);
    }
}
