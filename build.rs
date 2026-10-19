//! Build script: derives the package version from git tags.
//!
//! Runs `git describe --tags --long --dirty` and emits the result as the
//! `MIXEDTAPE_VERSION` environment variable, consumed by `src/lib.rs` via
//! `env!`. Falls back to the Cargo package version when git metadata is
//! unavailable (e.g. building from an sdist tarball).

use std::process::Command;

fn main() {
    // Rebuild (and re-derive the version) when git state moves or when
    // any source file in either language's tree changes. Without the
    // `mixedtape/` entry, a python-only edit would leave a stale
    // `.dirty`-less version baked into the cached extension.
    println!("cargo:rerun-if-changed=.git/HEAD");
    println!("cargo:rerun-if-changed=.git/refs/tags");
    println!("cargo:rerun-if-changed=src");
    println!("cargo:rerun-if-changed=mixedtape");

    let version = git_describe().unwrap_or_else(|| {
        let v = env!("CARGO_PKG_VERSION").to_string();
        if v == "0.0.0" {
            "0.0.0.dev0+unknown".to_string()
        } else {
            v
        }
    });

    println!("cargo:rustc-env=MIXEDTAPE_VERSION={version}");
}

fn git_describe() -> Option<String> {
    let output = Command::new("git")
        .args(["describe", "--tags", "--long", "--dirty", "--match", "v*"])
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let raw = String::from_utf8(output.stdout).ok()?;
    let raw = raw.trim();
    // raw looks like "v0.1.0-3-gabc1234[-dirty]" -> normalize to PEP 440
    Some(pep440(raw))
}

/// Convert `v<tag>-<n>-g<sha>[-dirty]` into a PEP 440 version.
fn pep440(describe: &str) -> String {
    let describe = describe.strip_prefix('v').unwrap_or(describe);
    let (core, dirty) = match describe.strip_suffix("-dirty") {
        Some(c) => (c, true),
        None => (describe, false),
    };
    let mut parts = core.rsplitn(3, '-');
    let sha = parts.next().unwrap_or("");
    let distance = parts.next();
    let tag = parts.next();

    let mut version = match (tag, distance) {
        // Exactly on a tag: "0.1.0"
        (Some(tag), Some("0")) => tag.to_string(),
        // N commits past a tag: "0.1.0.dev3+gabc1234"
        (Some(tag), Some(n)) => format!("{tag}.dev{n}+{sha}"),
        // No tag matched at all (shallow clone etc.)
        _ => format!("0.0.0.dev0+{sha}"),
    };
    if dirty {
        version.push_str(".dirty");
    }
    version
}
