# Native fuzz + ASAN process (NATIVE-028)

Owning gate: `NATIVE-028`. Package: `hedron-native`.

## Goal

Exercise the Rust HTML escape helpers (`escape_text_inner` /
`escape_attr_inner`) under `cargo fuzz` with AddressSanitizer so memory-safety
regressions fail before a wheel ships.

## Prerequisites

- Rust toolchain with `cargo`
- `cargo install cargo-fuzz`
- Nightly recommended for `cargo fuzz` + ASAN
- Seed corpus under `packages/hedron-native/fuzz/corpus/`

## Process

1. From `packages/hedron-native/`, follow `fuzz/README.md` to build the fuzz
   target (libFuzzer) against the escape helpers.
2. Run with ASAN enabled (cargo-fuzz default on nightly):

   ```bash
   cd packages/hedron-native
   cargo +nightly fuzz run escape_html -- -max_total_time=60
   ```

3. Keep the seed corpus cases that cover:
   - empty / short ASCII
   - HTML metacharacters (`<>&"'`)
   - NUL-adjacent notes (NUL must be stripped, not rendered)
   - long repetitive inputs (allocation pressure)
4. Record a successful summary in `RESULT.log` (seed count, duration, no
   crashes / ASAN findings).
5. Python-side parity remains covered by `tests/unit/test_native_fuzz.py` and
   `tests/unit/test_native_parity.py`.

## Pass criteria

- No crashes, timeouts-as-failures, or ASAN reports on the recorded run
- Seed corpus present and referenced from `RESULT.log`
- Supported inventory row `fuzz_sanitizer_parity` remains honest
