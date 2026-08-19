# hedron-conformance

Language-neutral Hedron conformance-test kit and capability runner.

**Package maturity:** Beta · **Train:** `0.51.x` (published `v0.51.0`) · pin `>=0.51.0,<0.52`
**Flagship extra:** `hedron[conformance]` · **Import:** `hedron_conformance`  
**CLI:** `hedron-conformance` · depends on pydantic only (no `hedron-core`)

## Install

```bash
pip install "hedron[conformance]>=0.51.0,<0.52"
# or
pip install "hedron-conformance>=0.51.0,<0.52"
```

## When to use

- Prove portable IR parity across Python reference, experimental Java/Node runtimes,
  or optional native accelerators
- Consume versioned fixtures without matching incidental CPython formatting

Cross-language runtimes that consume the kit remain **experimental** until labeled
Supported.

## Quick start

```bash
hedron-conformance run
hedron-conformance run --json
hedron-conformance list
hedron-conformance schema
hedron-conformance --version
# or
python -m hedron_conformance run
```

Failures report fixture id, contract version, and violated capability.

### Python API

```python
from hedron_conformance import load_bundled_fixtures, run_kit

fixtures = load_bundled_fixtures()
result = run_kit(fixtures)
assert result.ok
```

## Surfaces

| Symbol | Role |
|---|---|
| `load_bundled_fixtures()` | Load published fixtures shipped with the package |
| `run_kit(...)` | Capability-level runner over selected fixtures |
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
| HTML normalize input not text/HTML | Diagnostic / raise — never a silent pass |
| Host cannot satisfy a capability | Skip/fail per runner options — never mark Supported falsely |

## Related runtimes

Experimental monorepo evaluators (not PyPI app servers):

- [hedron-runtime-node](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-node) — Node ≥ 18
- [hedron-runtime-java](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-java) — JDK 11+

## Related docs

- Kit overview: [Conformance kit](../conformance/INDEX.md)
- API: [Conformance](../api/CONFORMANCE.md)

## Links

- [PyPI](https://pypi.org/project/hedron-conformance/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-conformance/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-conformance)
