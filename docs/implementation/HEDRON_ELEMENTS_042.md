# Phase 0.42 plan: production-grade Web Component platform

**Status:** Stage 0 contract refined against Published `v0.41.0` (D-070). Runtime
implementation begins at Stage 1.

This plan turns [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) and D-070 into reviewable
work. Baseline: Published `v0.41.0`. Target: coordinated `v0.42.0`. Tracking:
[#97](https://github.com/eddiethedean/hedron/issues/97). Completion requires every row in
[`release-gate-0.42.toml`](../acceptance/release-gate-0.42.toml) Verified with zero Deferred.

## Architecture

| Layer | Owned contract | Failure boundary |
|---|---|---|
| Supported inventory | Machine-readable tags, ABI, events, forms, tokens, fallback, exclusions | Unlisted surfaces stay Experimental/excluded |
| Compatibility | Mixed 0.36–0.41 assets, upgrade/rollback, offline, CDN refusal, removal | Preserve SSR / form / link / full-fragment |
| Independent review | Code execution, CSP/TT, sinks, origins/workers, skew, redaction | Zero unresolved critical/high at cut |
| AT-042 | Element workflow honesty on D-052 matrix | Unproven surfaces out of Supported; not SR-021 |
| Performance | Reference-app budget categories | Numeric ceilings at Stage 1+ |
| Supply | Wheel/npm SBOM, provenance, license, rollback | Incomplete evidence blocks PKG-042 |
| Fleet remediations | Exact 32 medium/low issues | Cut-blocking; do not expand element inventory |

## Contract artifacts

- [`supported-element-inventory-042.toml`](../acceptance/supported-element-inventory-042.toml)
- [`production-grade-inventory-042.toml`](../acceptance/production-grade-inventory-042.toml)
- [`upgrade-fixtures-042.md`](../acceptance/upgrade-fixtures-042.md)
- [`security-review-042/BRIEF.md`](../acceptance/security-review-042/BRIEF.md)
- [`human-at/042`](../acceptance/human-at/042/PROTOCOL.md)

## Work breakdown

### Stage 0 — contract and evidence packet (complete)

- Accept D-070 and RFC-0060 resolved questions.
- Lock release packet, planned gate manifest, inventories, upgrade matrix, review brief, AT skeleton.
- Bind #97 and the exact 32 regression issues; preserve Published `v0.41.0` living tip.

### Stage 1 — Supported inventory (`STABLE-042`, sketched)

- Flesh tag/ABI/attribute/event/form/token/fallback rows for each locked Supported tag.
- Prove Experimental exclusions remain non-default and independently owned.
- Cross-reference Published `hedron-chart` without re-cutting `hedron-charts`.

### Stage 2 — compatibility (`COMPAT-042`, sketched)

- Prove minimum/current browsers/dependencies, mixed 0.36–0.41 versions, upgrades, rollback,
  offline installs, CDN refusal, package removal, and unknown-feature fallback.

### Stage 3 — review and AT (`REVIEW-042`, `AT-042`, sketched)

- Complete structured maintainer-led (or external) review; resolve every critical/high.
- Run AT-042 sessions for declared workflows; keep blocked surfaces outside Supported.
- Do not close SR-021 / #86 from this packet alone.

### Stage 4 — performance and supply (`PERF-042`, `SUPPLY-042`, sketched)

- Lock numeric ceilings for named budget categories on `examples/reference-app`.
- Complete wheel/npm/module/worker/WASM/source/license/SBOM/provenance/rollback evidence.

### Stage 5 — closure (`REGRESS-042`, `PKG-042`, sketched)

- Close the exact 32-issue packet; run hosts/HDJ/plugins/conformance/browser/a11y/security/perf/docs
  packaging rehearsal.
- Cut only with zero Deferred 0.42 rows; tip becomes `v0.42.0` at cut, not Stage 0.

## Explicitly forbidden until Stage 1+

- Runtime/product code under `packages/**`, npm modules, static JS changes for graduation claims
- Workspace or tip bump (`docs/release.toml`, package versions, changelogs, `whats-new-0.42.md`)
- Flipping any 0.42 gate to Verified
- Adopter-facing “0.42 Published” / pin `>=0.42.0` claims
- Closing #97 or the 32 remediation issues
- Creating `security-review-042/DISPOSITION.toml` or `REDACTED_REPORT.md` before cut evidence
- Inventing `PRESENT-042`, reopening `polling_only`, or wrapping every component as a custom element

## Exit

Planning: `python scripts/verify_pkg_42.py --allow-planned`.
Cut: `python scripts/verify_pkg_42.py` and
`python scripts/check_release_gate.py 0.42.0 --execute-verified`.
