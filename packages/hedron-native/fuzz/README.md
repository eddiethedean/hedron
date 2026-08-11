# cargo fuzz for hedron-native

Fuzz the Rust HTML escape helpers used by `hedron_native._native`.

## Setup

```bash
rustup toolchain install nightly
cargo install cargo-fuzz
cd packages/hedron-native
```

## Suggested target sketch

Create a libFuzzer target (for example `fuzz/fuzz_targets/escape_html.rs`) that
feeds arbitrary bytes into `escape_text_inner` / `escape_attr_inner` (UTF-8 lossy
decode is fine). Wire it via a `Cargo.toml` fuzz workspace as described in the
[cargo-fuzz book](https://rust-fuzz.github.io/book/cargo-fuzz.html).

Seed inputs live in `fuzz/corpus/`.

## Run

```bash
cargo +nightly fuzz run escape_html -- -max_total_time=60
```

AddressSanitizer is enabled by default with cargo-fuzz on nightly. Record a
passing summary under
`docs/acceptance/native-fuzz-028/RESULT.log` for NATIVE-028 evidence.

## Corpus notes

- `nul_note.txt` documents NUL handling (NUL bytes are stripped by the escape
  helpers; do not expect them to survive into HTML).
- Prefer growing the corpus from real crash minimizations rather than hand-editing
  after a finding.
