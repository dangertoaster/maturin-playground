//! Checksum helpers exposed to Python.
//!
//! Deliberately exercises the full export matrix of the extension:
//! a `checksums` submodule with its own top-level functions
//! ([`sha256_data`], [`xxh3_data`]) *and* a further-nested
//! `checksums.streaming` submodule with its own exports — proving the
//! registration machinery handles modules nested two levels deep.

use pyo3::prelude::*;

/// Checksum functions, one-shot and streaming.
#[pymodule(submodule)]
pub mod checksums {
    use pyo3::prelude::*;
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    /// Compute the SHA-256-style digest of a byte string.
    ///
    /// .. note::
    ///    Placeholder (FNV-1a) for the prototype; swap in a real
    ///    SHA-256 before relying on it.
    ///
    /// :param data: The bytes to hash.
    /// :returns: Lowercase hex digest.
    #[pyfunction]
    fn sha256_data(data: &[u8]) -> String {
        super::fnv1a_hex(data)
    }

    /// Compute a 64-bit XXH3-style hash of a byte string.
    ///
    /// .. note::
    ///    Placeholder (SipHash via ``DefaultHasher``); swap in real
    ///    XXH3 before relying on it.
    ///
    /// :param data: The bytes to hash.
    /// :returns: The hash as an unsigned 64-bit integer.
    #[pyfunction]
    fn xxh3_data(data: &[u8]) -> u64 {
        let mut h = DefaultHasher::new();
        data.hash(&mut h);
        h.finish()
    }

    /// Streaming hashers that accept data in chunks.
    #[pymodule]
    pub mod streaming {
        use pyo3::prelude::*;

        /// A hasher that accepts data incrementally.
        #[pyclass(module = "mixedtape._mixedtape.checksums.streaming")]
        pub struct ChunkedHasher {
            buf: Vec<u8>,
        }

        #[pymethods]
        impl ChunkedHasher {
            /// Create an empty hasher.
            #[new]
            fn new() -> Self {
                Self { buf: Vec::new() }
            }

            /// Feed a chunk of data into the hasher.
            ///
            /// :param data: The next chunk of bytes.
            fn update(&mut self, data: &[u8]) {
                self.buf.extend_from_slice(data);
            }

            /// Return the hex digest of all data fed so far.
            ///
            /// :returns: Lowercase hex digest.
            fn hexdigest(&self) -> String {
                super::super::fnv1a_hex(&self.buf)
            }
        }

        /// One-shot helper: digest of ``data`` in a single call.
        ///
        /// :param data: The bytes to hash.
        /// :returns: Lowercase hex digest.
        #[pyfunction]
        fn digest(data: &[u8]) -> String {
            super::super::fnv1a_hex(data)
        }
    }
}

/// FNV-1a 64-bit, hex-encoded. Placeholder digest for prototyping.
pub(crate) fn fnv1a_hex(data: &[u8]) -> String {
    let mut hash: u64 = 0xcbf2_9ce4_8422_2325;
    for &b in data {
        hash ^= u64::from(b);
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    format!("{hash:016x}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fnv1a_empty() {
        assert_eq!(fnv1a_hex(b""), "cbf29ce484222325");
    }

    #[test]
    fn fnv1a_known_vector() {
        // FNV-1a 64 of "a" is a well-known constant.
        assert_eq!(fnv1a_hex(b"a"), "af63dc4c8601ec8c");
    }
}
