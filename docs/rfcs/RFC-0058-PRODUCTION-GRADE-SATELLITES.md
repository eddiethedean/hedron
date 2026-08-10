# RFC-0058: Production-grade adapters, data, HDJ authoring, and curated extras

**Status:** Accepted
**Phase:** 0.27 (`v0.27.0`)
**Stability:** `beta` (process / package-graduation contract)
**Evidence:** [RELEASE_0_27.md](../acceptance/RELEASE_0_27.md) ·
[release-gate-0.27.toml](../acceptance/release-gate-0.27.toml) ·
[production-grade-inventory-027.toml](../acceptance/production-grade-inventory-027.toml)
**Related:** D-038, D-053, D-054, D-055; [RFC-0056](RFC-0056-PRODUCTION-QUALITY.md);
[RFC-0057](RFC-0057-PRODUCTION-GRADE-CORE.md); [ROADMAP §0.27](../ROADMAP.md);
[STABILITY.md](../api/STABILITY.md)

## Summary

Apply the ROADMAP **production-grade package contract (0.26+)** to
`hedron-data`, `hedron-flask`, `hedron-django`, `hedron-jinja`, and
`hedron-extras` for explicitly bounded Supported workflows. Baseline train is
Published **`v0.26.0`**. Beta maturity today is not the production-grade label;
0.27 is the graduation that earns that label for the **declared inventory only**.

## Motivation

Phase 0.26 (D-054 / RFC-0057) graduated `hedron-core`, `hedron`, and
`hedron-explorer` for the documented CRUD/admin surface. Remaining work for the
supported Python satellite train is package-level graduation evidence:
machine-readable inventories, upgrade fixtures from `v0.26.0`, host-only install
matrices, portable FastAPI/Flask/Django interaction parity, bounded
data/browser/a11y/CSP evidence, HDJ format compatibility, curated-extras
budgets with experimental-ui quarantine, and a Verified release packet — without
promoting experimental live transports, specialty UI landmines, charts/native,
or scheduling `1.0`.

## Design

### Packages in scope

| Package | Production-grade scope |
|---|---|
| `hedron-data` | Bounded DataTable/DataEditor CRUD; in-memory / pandas / SQLAlchemy / bounded Django QuerySet sources; saved views; documented spreadsheet paths |
| `hedron-flask` | Native Flask pages/fragments/actions; host-owned sessions/CSRF/auth; polling jobs; scaffolds; deployment integration |
| `hedron-django` | Native Django responses/views/middleware/forms; bounded QuerySet source; polling jobs; system checks; deployment integration |
| `hedron-jinja` | Trusted `.hdj` v1 authoring; strict sink analysis; manifests/assets; component bindings; async preparation; host integration |
| `hedron-extras` | Curated default `hedron[extras]` registry only; `experimental-ui` remains separately named and outside the production-grade Supported inventory |

### Gate IDs

`DATA-027`, `FLASK-027`, `DJANGO-027`, `HDJ-027`, `EXTRAS-027`, `PARITY-027`,
`REGRESS-027`, `PKG-027`.

Inventory agreement with public docs and package metadata is required for
`PKG-027` (machine-readable
[production-grade-inventory-027.toml](../acceptance/production-grade-inventory-027.toml)).

### Trust-boundary evidence bar

Satellite trust boundaries deferred from the 0.26 core review
([security-review-026/BRIEF.md](../acceptance/security-review-026/BRIEF.md)) are
owned by the per-package gates above plus `PARITY-027`. Verified at cut means
gate-owned adversarial suites are green and a structured maintainer-led review
(independent of the feature authoring pass for this packet) attaches a redacted
report plus disposition ledger for data/adapter/HDJ/extras boundaries —
same honesty bar as REVIEW-026. Commercial third-party re-review remains
optional follow-up.

### Upgrade fixtures

See [upgrade-fixtures-027.md](../acceptance/upgrade-fixtures-027.md): goldens
from `v0.26.0` data/adapter/HDJ/extras public contracts under `tests/upgrade/`.

### Non-goals

- Requiring Flask/Django parity for experimental live transports
- Treating arbitrary application QuerySets, SQL, templates, or trusted HTML as
  safe without app authorization and validation
- Graduating `CodeEditor`, `TerminalView`, joystick, or device bridges merely
  because the containing distribution graduates
- Bundling every optional dataframe, database, spreadsheet, or Jinja extension
  by default
- Making Explorer audit durable (`REV-026-003` remains Explorer-owned accepted risk)
- Graduating charts, native acceleration, MCP, Gradio, or conformance tooling
  (later phases)
- Scheduling `1.0`, SLA, or certification claims

## Acceptance

- Every 0.27-owned gate row Verified with zero Deferred
- Production-grade label used only for declared Supported inventory
- `python scripts/verify_pkg_27.py` passes without `--allow-planned` at cut
