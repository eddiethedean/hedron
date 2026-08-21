# Hedron `v0.57` unified presentation acceptance

**Status:** Published in-tree as `v0.57.0` (all nine gates Verified; tag/PyPI deferred)<br>
**Planning baseline:** In-tree `0.56.1`<br>
**Required predecessor/cut baseline:** Published `v0.56.0`<br>
**Target:** Hedron `v0.57.0`<br>
**Decision/RFC:** D-099 / D-100 / [RFC-0084](../rfcs/RFC-0084-UNIFIED-PRESENTATION.md)<br>
**Tracking:** [#570](https://github.com/eddiethedean/hedron/issues/570) ([#558](https://github.com/eddiethedean/hedron/issues/558)–[#569](https://github.com/eddiethedean/hedron/issues/569))

Stage 0 freezes the 0.57 gates and presentation contracts. Stage 1 implements the
presentation workstreams, Verifies all nine gates, and cuts the in-tree tip to
`v0.57.0`. **Do not tag yet.**

Shared authority remains `hedron_core.builtins.appearance` with stable
`data-hedron-*` markers. New symbols include `Surface`, `GridItem`,
`ResourceList`, `ResourceRow`, `Avatar`, `Identity`, `Brand`,
`AccountSummary`, `EnvironmentBanner`, `NavStatus`, and `AppFooter`. Appearance
vocabulary adds `plain` and `raised`. The phase proves zero-application-CSS for
a representative authenticated workspace.

## Exact gate matrix

| Gate | State | Evidence command |
|---|---|---|
| `CONTRACT-057` | Verified | `python scripts/check_contract_057.py` |
| `CSP-057` | Verified | `python scripts/check_csp_057.py` |
| `LAYOUT-057` | Verified | `python scripts/check_layout_057.py` |
| `SURFACE-057` | Verified | `python scripts/check_surface_057.py` |
| `DATA-057` | Verified | `python scripts/check_data_057.py` |
| `WORKFLOW-057` | Verified | `python scripts/check_workflow_057.py` |
| `REGRESS-057` | Verified | `python scripts/check_regress_057.py` |
| `ZERO-CSS-057` | Verified | `python scripts/check_zero_css_057.py` |
| `PKG-057` | Verified | `python scripts/check_pkg_057.py` |

## Stage 0 checklist

- [x] D-099 and RFC-0084 own 0.57 unified presentation.
- [x] D-100 names Published predecessor `v0.56.0` and refine baseline `0.56.1`.
- [x] Tracking #570 / #558–#569 is bound.
- [x] Gate index and acceptance locks are Planned.
- [x] 0.56 gates remain Verified and are not reopened.
- [x] Stage 0 does not bump package versions.

## Stage 1 checklist

- [x] Issue workstreams Verified with executable evidence.
- [x] All nine gates Verified with zero Deferred.
- [x] Acceptance locks flipped to Verified.
- [x] Package versions cut to `0.57.0` (in-tree tip; no Git tag yet).

## Cut checklist

- [x] Train packages + workspace bumped to `0.57.0`.
- [x] `docs/release.toml` tip honesty with `registry_status = "deferred"`.
- [x] CI `HEDRON_GATE_VERSION=0.57.0`.
- [x] Docs / SECURITY / STATUS / ROADMAP tip honesty.
- [ ] Git tag `v0.57.0` — **not yet**.
