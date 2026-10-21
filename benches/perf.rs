//! Performance regression benchmarks for the hot paths.
//!
//! Uses [criterion](https://benches.rs), the standard rust benchmarking
//! harness. Criterion keeps a baseline per benchmark in
//! `target/criterion/` and reports statistically significant regressions
//! run-over-run; `cargo bench -- --save-baseline <name>` /
//! `--baseline <name>` turns that into explicit before/after comparisons
//! (the usual PR workflow for perf-sensitive changes).
//!
//! Keep all benchmarks in this file so they stay discoverable; add new
//! ones as additional fns registered in the `benches` group below.
//!
//! ```sh
//! cargo bench                          # run, compare against last run
//! cargo bench -- --save-baseline main  # snapshot before a change
//! cargo bench -- --baseline main       # compare after
//! ```

use std::hint::black_box;

use criterion::{BenchmarkId, Criterion, criterion_group, criterion_main};
use _mixedtape::grammar_rs::parse_selector_impl;
use _mixedtape::text::{lev, shingle_words};

fn bench_levenshtein(c: &mut Criterion) {
    let mut group = c.benchmark_group("levenshtein");
    for size in [16usize, 128, 1024] {
        let a: String = "the quick brown fox ".repeat(size / 20 + 1)[..size].to_string();
        let b: String = "the quik brwn fx ".repeat(size / 17 + 1)[..size].to_string();
        group.bench_with_input(BenchmarkId::from_parameter(size), &(a, b), |bencher, (a, b)| {
            bencher.iter(|| lev(black_box(a), black_box(b)));
        });
    }
    group.finish();
}

fn bench_shingle(c: &mut Criterion) {
    let mut group = c.benchmark_group("shingle");
    for (label, words) in [
        ("unique", (0..2000).map(|i| format!("w{i}")).collect::<Vec<_>>()),
        (
            "duplicated",
            (0..2000).map(|i| format!("w{}", i % 300)).collect::<Vec<_>>(),
        ),
    ] {
        group.bench_with_input(BenchmarkId::from_parameter(label), &words, |bencher, words| {
            bencher.iter(|| shingle_words(black_box(words), 3));
        });
    }
    group.finish();
}

fn bench_parse_selector(c: &mut Criterion) {
    let mut group = c.benchmark_group("parse_selector");
    for input in ["on amd64", "to riscv64", "bogus input here"] {
        group.bench_with_input(BenchmarkId::from_parameter(input), &input, |bencher, input| {
            bencher.iter(|| parse_selector_impl(black_box(input)));
        });
    }
    group.finish();
}

criterion_group!(benches, bench_levenshtein, bench_shingle, bench_parse_selector);
criterion_main!(benches);
