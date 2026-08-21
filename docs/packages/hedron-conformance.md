# hedron-conformance

Language-neutral Hedron conformance-test kit and capability runner.

**Package maturity:** Beta · **Train:** `0.56.x` (in-tree tip `v0.56.0`) · pin `>=0.56.0,<0.57` in-tree (PyPI `>=0.54.0,<0.55` while deferred)

**Flagship extra:** `hedron[conformance]` · **Import:** `hedron_conformance`

**CLI:** `hedron-conformance` · depends on pydantic only (no `hedron-core`)

Phase 0.52 authority contract: [RFC-0079](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md) /
[#522](https://github.com/eddiethedean/hedron/issues/522).

## Install

```bash
pip install "hedron[conformance]>=0.54.0,<0.55"
# or
pip install "hedron-conformance>=0.54.0,<0.55"
```

Checkout tip `v0.56.0` uses `>=0.56.0,<0.57` in-tree; PyPI first-run stays `>=0.54.0,<0.55` until the Git tag / PyPI upload lands.

## When to use

- Prove portable IR parity across Python reference, experimental Java/Node runtimes,
  or optional native accelerators
- Consume versioned fixtures without matching incidental CPython formatting
- Compile suites, select declared profiles, and emit CI report envelopes (JUnit / SARIF)

Cross-language runtimes that consume the kit remain **experimental** until labeled
Supported.

## Quick start

```bash
hedron-conformance run
hedron-conformance run --json
hedron-conformance run --junit
hedron-conformance run --sarif
hedron-conformance run --envelope
hedron-conformance compile
hedron-conformance profiles
hedron-conformance list
hedron-conformance schema
hedron-conformance --version
# or
python -m hedron_conformance run
```

Failures report fixture id, contract version, and violated capability.

### Python API

```python
from hedron_conformance import compile_suite, load_bundled_fixtures, run_kit

fixtures = load_bundled_fixtures()
compiled = compile_suite(fixtures)
assert compiled.ok
result = run_kit(fixtures)
assert result.ok
```

## Surfaces

| Symbol | Role |
|---|---|
| `load_bundled_fixtures()` | Load published fixtures shipped with the package |
| `run_kit(...)` | Capability-level runner over selected fixtures |
| `compile_suite(...)` | Fixture compiler; rejects contradictory suites |
| `CompileReport` | Compiler ok/errors payload |
| `load_profile_registry()` / `admit_fixtures(...)` | Versioned profile registry |
| `build_result_envelope(...)` | Signed-ish HMAC/SHA256 result envelope |
| `to_junit` / `to_sarif` | CI converters |
| `SandboxPolicy` / `check_archive_budget(...)` | Archive/process/network/secret sandbox defaults + fail-closed budget checks |
| `normalize_html(...)` | `html-v1` normalization for stable comparisons |
| `ConformanceFixture` | Fixture metadata model |
| `Capability` | Capability identifier enum / labels |
| `CONTRACT_VERSION` / `FIXTURE_VERSION` | Kit / corpus version strings |

### Fixture fields

| Field | Meaning |
|---|---|
| `id` | Stable fixture identifier |
| `fixture_version` | Fixture file format version |
| `contract_version` | Portable contract id (`hedron-portable-1`) |
| `capability` | escaping, identity, diagnostics, artifact-version, rendering, accessibility, adversarial |
| `input` / `expected` | Machine-readable IR and golden outcomes |
| `normalization` | Rule set id (`html-v1`) |
| `negative` | Expected failure / rejection when true |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Unknown capability / missing fixture | Fail closed — does not invent fixtures |
| Contradictory suite (compiler) | `compile_suite` returns `ok=False` with actionable errors |
| HTML normalize input not text/HTML | Diagnostic / raise — never a silent pass |
| Host cannot satisfy a capability | Skip/fail per runner options — never mark Supported falsely |

## Related runtimes

Experimental monorepo evaluators (not PyPI app servers):

- [hedron-runtime-node](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-node) — Node ≥ 18 (`0.53.0`)
- [hedron-runtime-java](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-java) — JDK 11+ (`0.53.0`)

## Related docs

- Kit overview: [Conformance kit](../conformance/INDEX.md)
- API: [Conformance](../api/CONFORMANCE.md)
- RFC: [RFC-0079](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md) · tracking [#522](https://github.com/eddiethedean/hedron/issues/522)

## Links

- [PyPI](https://pypi.org/project/hedron-conformance/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-conformance/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-conformance)
