# Edron 0.2 acceptance

**Status:** Verified release candidate

Phase 0.2 is accepted for the source tree when the focused unit and lint commands in
[`EDRON_002.md`](../implementation/EDRON_002.md) pass.

The 0.2.0 release gate is [edron-release-gate-002.toml](edron-release-gate-002.toml). It records
the verified package metadata, full unit suite, lint, wheel/sdist inspection, and tag workflow.
Publication remains a maintainer-controlled external step; the repository is ready for tag
`edron-v0.2.0`.

| Gate | Evidence | State |
|---|---|---|
| `EDR-02-DIAGNOSTICS` | structured source-aware diagnostics, redaction, JSON/SARIF | Verified |
| `EDR-02-STATIC` | AST check does not import or execute application source | Verified |
| `EDR-02-EXPLAIN` | explanation/source-map facts include native routes and source spans | Verified |
| `EDR-02-SCAFFOLD` | deterministic templates and overwrite protection | Verified |
| `EDR-02-AUTHORING` | function pages and explicit descriptor inheritance | Verified |
| `EDR-02-REGRESSION` | 0.1 runtime and docs checker remain green | Verified |

The phase remains Beta. Function-page and inheritance conveniences are additive and explicit;
existing class registration behavior and native Hedron ownership are preserved.
