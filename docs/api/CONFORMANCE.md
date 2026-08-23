# Conformance API

Package: [`hedron-conformance`](https://pypi.org/project/hedron-conformance/).

**Phase 0.52 authority contract:** D-089 / D-090 /
[RFC-0079](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md) /
[#522](https://github.com/eddiethedean/hedron/issues/522). Introduced in
`v0.52.0`; the current package train is `0.59.x` (`v0.59.0` on PyPI).
Workstream A Stage 1 extends the portable-subset authority; it does
**not** replace `CONTRACT_VERSION` / `hedron-portable-1` without negotiation.

Public surface for the language-neutral conformance kit (0.51.2 seed + 0.52
authority extensions):

| Symbol | Role |
|---|---|
| `load_bundled_fixtures()` | Load published fixtures shipped with the package |
| `run_kit(...)` | Capability-level runner over selected fixtures |
| `normalize_html(...)` | `html-v1` normalization for stable comparisons |
| `ConformanceFixture` | Fixture metadata model |
| `Capability` | Capability identifier enum / labels |
| `CONTRACT_VERSION` | Kit contract version string (`hedron-portable-1`) |
| `FIXTURE_VERSION` | Bundled fixture corpus version |
| `PROTOCOL_CURRENT` / `PROTOCOL_PREVIOUS` | Negotiation aliases (extend, do not replace seed) |
| `negotiate_protocol(...)` | Current/previous protocol negotiation (COMPAT-052) |
| `protocol_matrix()` | Machine-readable current/previous matrix |
| `load_profile_registry()` | Versioned profile registry (PROFILE-052) |
| `admit_fixtures(profile_id)` | Fixtures admitted by a named profile |
| `suite_digest` / `suite_digests` / `profile_suite_digest` | Deterministic suite digests |
| `compile_suite(...)` | Fixture compiler; rejects contradictory suites |
| `CompileReport` | Compiler ok/errors payload |
| `build_result_envelope(...)` | Signed-ish HMAC/SHA256 result envelope |
| `to_junit` / `to_sarif` | CI converters |
| `offline_bundle_manifest(...)` | Offline provenance bundle inventory |
| `validate_suite_path(...)` | Reject path traversal in suite paths |
| `SandboxPolicy` / `check_archive_budget(...)` | Archive/process/network/secret sandbox defaults + fail-closed budget checks |
| `AUTHOR_KIT_VERSION` / `declared_capabilities()` | Author kit 0.52 without monorepo import |

## 0.52 authority contract

| Concern | Lock |
|---|---|
| Portable subset | Node/Java evaluate declared profiles only — not FastAPI, browser, or complete Hedron |
| Seed contract | Extend `hedron-portable-1` via negotiation; do not silently replace `CONTRACT_VERSION` |
| Profiles | `core-render`, `interaction`, `manifest`, `element`, `package` (see [conformance-profile-052.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/conformance-profile-052.toml)) |
| Default corpus | Top-level `fixtures/*.json`; subdirectory corpora opt-in until profiles admit them |
| Author kit | External packages declare `Capability` without monorepo import (`AUTHOR-052`) |
| Reports | Signed envelopes + JUnit/SARIF provenance (`REPORT-052` / `CI-052`) |

Gates: `PROTOCOL-052`, `PROFILE-052`, `FIXTURE-052`, `NEGATIVE-052`,
`RUNTIME-052`, `DIFF-052`, `SECURITY-052`, `SANDBOX-052`, `REPORT-052`,
`CI-052`, `COMPAT-052`, `PLATFORM-052`, `AUTHOR-052` (plus shared
`DOCS-052` / `PKG-052` / `SUPPLY-052` / `REGRESS-052`).

## Errors

| Condition | Behavior |
|---|---|
| Unknown capability / missing fixture | Runner fails closed with a clear error; does not invent fixtures |
| Contradictory suite (compiler) | `compile_suite` returns `ok=False` with actionable errors |
| HTML normalize input not text/HTML | Raises / returns diagnostic — do not treat as a silent pass |
| Host cannot satisfy a capability | Report as skip/fail per runner options; never mark Supported falsely |
| Incompatible protocol version | Explicit incompatible-version behavior under `COMPAT-052` |
| Suite path traversal | `validate_suite_path` raises `SuitePathError` |

See [Language-neutral conformance kit](../conformance/INDEX.md),
[CONFORMANCE_052](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/CONFORMANCE_052.md), and
[Autodoc](AUTODOC.md) for signatures when the package is installed.
