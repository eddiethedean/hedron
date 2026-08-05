# Language-neutral conformance kit

**Status:** Accepted for phase 0.14 (D-048)

The `hedron-conformance` package publishes versioned fixtures that any Hedron
implementation — Python reference, experimental Java/Node runtimes, or optional
native accelerators — must pass.

## Fixture fields

| Field | Meaning |
|---|---|
| `id` | Stable fixture identifier |
| `fixture_version` | Fixture file format version (`1.0.0`) |
| `contract_version` | Portable contract id (`hedron-portable-1`) |
| `capability` | One of: escaping, identity, diagnostics, artifact-version, rendering, accessibility, adversarial |
| `input` | Machine-readable IR / parameters |
| `expected` | Golden outcomes |
| `normalization` | Rule set id (`html-v1`) |
| `negative` | When true, the case is an expected failure / rejection |

## Normalization (`html-v1`)

Implementations must not pass merely by matching incidental CPython formatting.
Comparisons use `hedron_conformance.normalize_html` (`html-v1`):
strip ends, collapse whitespace between tags, preserve attribute order from the
reference `ATTR_ORDER` contract (serializers emit sorted attributes).

## Runner

```bash
hedron-conformance run
hedron-conformance run --json
```

Failures name `fixture`, `contract_version`, and `capability`.
