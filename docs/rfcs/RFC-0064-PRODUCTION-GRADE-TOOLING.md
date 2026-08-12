# RFC-0064: Production-grade developer and portable conformance tooling

**Status:** Accepted

**Target phase:** 0.31 (`v0.31.0`)

**Stability:** `beta` (process / package-graduation contract for tooling roles)

**Evidence:** [RELEASE_0_31.md](../acceptance/RELEASE_0_31.md) ·
[release-gate-0.31.toml](../acceptance/release-gate-0.31.toml) ·
[production-grade-inventory-031.toml](../acceptance/production-grade-inventory-031.toml)

**Related:** D-038, D-053, D-059; [RFC-0056](RFC-0056-PRODUCTION-QUALITY.md);
[RFC-0061](RFC-0061-STREAMLIT-AST-MIGRATOR.md) (companion migrator packet);
[ROADMAP §0.31](../ROADMAP.md); tracking
[#87](https://github.com/eddiethedean/hedron/issues/87)

## Summary

Apply the ROADMAP **production-grade package contract (0.26+)** to developer and
portable conformance tooling for explicitly bounded **tooling** roles:

| Package | Production-grade scope at exit |
|---|---|
| `hedron-conformance` | Versioned schemas/fixtures, normalization, runner CLI/API, compatibility policy, third-party runtime author kit |
| `hedron-sample-kit` | Maintained external-plugin exemplar (compatibility, security, assets, diagnostics, Explorer tests) |
| `hedron-sim` | Deterministic offline docs/demo fragments with CSP-safe assets and a declared HTMX subset |
| `hedron-notebook` | Localhost-only preview lifecycle, iframe isolation, cleanup, Jupyter compatibility |
| `hedron-runtime-node` | Published, signed Node conformance evaluator — not an app server or full Hedron port |
| `hedron-runtime-java` | Published, signed Java conformance evaluator — not an app server or full Hedron port |

**Tooling-grade** means reliable and Supported for the stated development or
conformance purpose. It does **not** convert these packages into application
production servers, hosted multi-user notebook services, or full framework ports.

The Streamlit AST migration assistant is owned by [RFC-0061](RFC-0061-STREAMLIT-AST-MIGRATOR.md)
under the same phase decision (D-059 / `MIGRATE-031`). This RFC owns the #87
tooling graduation gates only.

## Motivation

Phases 0.26–0.30 graduated core, satellites, charts/native, and Workbench
deployment surfaces. Conformance, sample plugins, simulation, notebook preview,
and cross-language evaluators remain Alpha or under-specified relative to the
production-grade honesty bar. Adopters and CI consumers need versioned fixtures,
publish channels, and explicit non-goals before maturity labels change.

## Design

### Gate IDs

`CONF-031`, `PLUGIN-031`, `SIM-031`, `NOTEBOOK-031`, `NODE-031`, `JAVA-031`,
plus shared `REGRESS-031` / `PKG-031` with the migrator packet.

Inventory agreement with public docs and package metadata is required for
`PKG-031` (machine-readable
[production-grade-inventory-031.toml](../acceptance/production-grade-inventory-031.toml)).

### Publish channels

| Artifact | Channel |
|---|---|
| Python tooling packages | PyPI (coordinated or satellite lines per existing policy) |
| `hedron-runtime-node` | npm (signed / provenance where the registry supports it) |
| `hedron-runtime-java` | Maven Central or the project’s declared Java registry |

Cross-language evaluators must prove parity against the same immutable Python
reference fixture bundle, with supported runtime matrices, reproducible builds,
licenses, and offline/dependency-light execution where practical.

### Tooling-grade versus app Supported

- Notebook preview remains **localhost-only**; remote/public serving stays refused
  by the Supported API.
- Sim declares a finite HTMX subset and fails loudly outside it; it does not claim
  full browser/HTMX emulation.
- Sample-kit is an exemplar, never a required runtime dependency of Hedron apps.
- Node/Java evaluators are conformance runners, not Hedron application hosts.

### Non-goals

- Hosted multi-user notebook service
- Describing Node/Java evaluators as full component frameworks or web servers
- Claiming `hedron-sim` emulates all browser/HTMX behavior
- Making sample-kit a required runtime dependency
- Graduating MCP or Gradio (later phases)
- Scheduling Hedron `1.0`, SLA, or certification claims

## Acceptance

- Every 0.31 tooling-owned gate row (`CONF-031`…`JAVA-031` and shared regress/pkg
  rows) Verified with zero Deferred at cut
- Production-grade / tooling-grade labels used only for declared Supported inventory
- `python scripts/verify_pkg_31.py` passes without `--allow-planned` at cut
- Tracking [#87](https://github.com/eddiethedean/hedron/issues/87) closes only when
  those gates are Verified
