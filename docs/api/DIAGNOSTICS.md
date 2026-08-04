---
status: shipped
---

# Diagnostics formatters


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted for phase 0.4

`Diagnostic` records render as:

- human text (`as_text`)
- JSON (`as_json` / `diagnostics_to_json`)
- SARIF 2.1.0 (`diagnostics_to_sarif`)

Suppressions name a code, smallest source scope, and justification. Security-area codes (`HED-SEC-*`) and selected strict diagnostics cannot be suppressed.

CI and `hedron check` apply severity thresholds without mutating underlying records.
