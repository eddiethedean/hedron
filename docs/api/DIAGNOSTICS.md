---
status: shipped
---

# Diagnostics formatters


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Stable diagnostic record on 1.0 (introduced in 0.4)

Stable `HED-*` records from `hedron_core.diagnostics`. Prefer these codes in CI and
operator logs — see [Error codes](../guides/error-codes.md).

## `Diagnostic`

| Field | Type | Description |
|---|---|---|
| `code` | `str` | Must start with `HED-` (for example `HED-BUILD-0003`) |
| `severity` | `DiagnosticSeverity` | `error` / `warning` / `information` |
| `title` | `str` | Short headline |
| `explanation` | `str` | What happened |
| `remediation` | `str` | Optional fix hint |
| `owner` | `str \| None` | Owning subsystem |
| `component_id` | `str \| None` | Related component identity |
| `context` | mapping | Extra structured fields (never secrets) |
| `docs_url` | `str \| None` | Optional docs link |
| `span` | `SourceSpan \| None` | 1-based source location |

### Instance methods

| Method | Returns | Description |
|---|---|---|
| `as_text()` | `str` | Human-readable multi-line text |
| `as_json()` | `dict` | JSON-serializable record |

## Module formatters

| Function | Returns | Description |
|---|---|---|
| `diagnostics_to_text(diagnostics)` | `str` | Joined `as_text()` for a sequence |
| `diagnostics_to_json(diagnostics)` | `list[dict]` | JSON list for CI / APIs |
| `diagnostics_to_sarif(diagnostics, …)` | `dict` | SARIF 2.1.0 document |

```python
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, diagnostics_to_json

diag = Diagnostic(
    code="HED-BUILD-0003",
    severity=DiagnosticSeverity.ERROR,
    title="missing production manifest",
    explanation="HEDRON_ENV=production requires a build manifest.",
    remediation="Run hedron build and deploy the build directory.",
)
print(diagnostics_to_json([diag]))
```

Suppressions name a code, smallest source scope, and justification. Security-area codes
(`HED-SEC-*`) and selected strict diagnostics cannot be suppressed.

CI and `hedron check` apply severity thresholds without mutating underlying records.

## See also

[Error codes](../guides/error-codes.md) · [CLI](CLI.md)
