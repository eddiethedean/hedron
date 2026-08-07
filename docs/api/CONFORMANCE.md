# Conformance API

Package: [`hedron-conformance`](https://pypi.org/project/hedron-conformance/).

Public surface for the language-neutral conformance kit:

| Symbol | Role |
|---|---|
| `load_bundled_fixtures()` | Load published fixtures shipped with the package |
| `run_kit(...)` | Capability-level runner over selected fixtures |
| `normalize_html(...)` | `html-v1` normalization for stable comparisons |
| `ConformanceFixture` | Fixture metadata model |
| `Capability` | Capability identifier enum / labels |
| `CONTRACT_VERSION` | Kit contract version string |
| `FIXTURE_VERSION` | Bundled fixture corpus version |

## Errors

| Condition | Behavior |
|---|---|
| Unknown capability / missing fixture | Runner fails closed with a clear error; does not invent fixtures |
| HTML normalize input not text/HTML | Raises / returns diagnostic — do not treat as a silent pass |
| Host cannot satisfy a capability | Report as skip/fail per runner options; never mark Supported falsely |

See [Language-neutral conformance kit](../conformance/INDEX.md) and
[Autodoc](AUTODOC.md) for signatures when the package is installed.
