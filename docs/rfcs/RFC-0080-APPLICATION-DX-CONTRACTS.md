# RFC-0080: Application DX contracts

**Status:** Accepted<br>
**Target phase:** 0.53 (`v0.53.0`)<br>
**Decision:** D-091<br>
**Stage 0 contract refine:** D-092<br>
**Planning baseline:** Published in-tree `v0.52.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.52.0`<br>
**Tracking:** [#514](https://github.com/eddiethedean/hedron/issues/514)–[#521](https://github.com/eddiethedean/hedron/issues/521)<br>

**Revision:** 2026-08-20 — D-091 ownership + D-092 Stage 0 refine against
Published in-tree `v0.52.0`. No Stage 0 runtime, version bump, or registry claim.

## Summary

Phase 0.53 turns eight application-facing seams into one coherent DX contract:
ordered assets, actionable diagnostics, route/effect export, durable-operation
composition, catalog-derived tests, semantic themes, API discovery, and
installed-fleet triage. These are additive contracts over 0.52; they do not
replace the registries, catalogs, job backends, or diagnostic records already
shipped.

## Goals

- Let applications register dependency-ordered CSS/scripts/modules through the
  typed, CSP-aware page asset pipeline without response-body middleware.
- Give diagnostics an explicit applicability interval, conventional severity
  aliases, justified suppressions, and structured remediation actions while
  retaining stable `HED-*` codes and JSON/text/SARIF output.
- Export versioned route and effect documents with typed nested values rather
  than stringified metadata; export never imports or executes a handler.
- Compose start/monitor/cancel/retry, terminal states, busy regions, and
  completion effects over `JobBackend`; terminal observation stops monitoring.
- Generate deterministic, reviewable interaction-test source from a sealed
  `InteractionCatalog` for page, HTMX, mount, and error cases.
- Lock a semantic-token-only contract for apps using `default_styles=False` and
  a reusable visual-conformance workflow across supported elements.
- Discover curated imports and stability from an explicit inventory while
  preserving existing imports.
- Diagnose the installed application fleet: distribution/train skew, selected
  extras, plugin/asset activation, and evidence-backed recommendations.

## Non-goals and exclusions

- Arbitrary HTML response rewriting, CDN fetching, implicit remote assets, or
  bypassing CSP/integrity policy.
- Executing route handlers during graph export or executing untrusted catalog
  payloads during test generation.
- Replacing `JobBackend`, promising exactly-once execution, or reopening the
  0.24 `polling_only` disposition.
- Renaming the broad public facade or graduating undocumented imports.
- Replacing 0.54 external-author `hedron package doctor`; `FLEET-053` inspects
  an installed application, while `DOCTOR-054` validates a package being built.
- Reopening Explorer 0.50, extras 0.51, conformance/Posit 0.52,
  `MORPH-048`, `SR-021`, adapter dispositions, or scheduling `1.0`.
- Runtime symbols, numeric performance limits, version bumps, or living-tip
  movement during Stage 0.

## Consume shipped, do not fork (D-092)

| Area | Published 0.52 seams retained |
|---|---|
| Assets | `inject_page_assets`, `AssetRef`, `AssetMeta`, `register_asset`, extension plans, build manifests, `SecurityPolicy` |
| Diagnostics | `Diagnostic`, `DiagnosticSeverity` (`error`/`warning`/`information`), `Suppression`, `apply_suppressions`, JSON/text/SARIF writers, `hedron check` |
| Routes/effects | registry `RouteMeta`, `routes_json`, `hedron routes`, `InteractionCatalog`, `CatalogEntry`, observed/declared/dynamic effect state |
| Workflow | `JobBackend`, `JobHandle`, `JobStatus`, `JobState`, `job_status_interaction`, authorized status endpoints, SSE events |
| Test generation | `compile_interaction_catalog`, `seal_app_catalog`, catalog/manifest fingerprints and redaction profiles |
| Theme | `Theme`, `REQUIRED_A11Y_TOKENS`, forced-color/print token sets, element style contracts, `default_styles=False` |
| Discovery/fleet | `hedron.__all__`, package metadata/plugin registries, Explorer read-only package-health slice |

## Locked contract boundaries

1. Asset dependencies form a deterministic acyclic plan. Duplicate logical IDs,
   missing dependencies, cycles, invalid placement, and integrity/CSP conflicts
   fail diagnostically. Existing framework ordering remains compatible.
2. Applicability and remediation are data, not prose parsing. Security findings
   remain unsuppressible. Severity aliases normalize to the existing enum.
3. Route/effect schemas are versioned, deterministic, redacted, and bounded by
   existing catalog limits. Unknown fields are preserved or rejected according
   to the declared schema version—never silently stringified.
4. Workflow state derives from `JobState`; cancellation is cooperative, retries
   are explicit, authorization remains backend/route owned, and terminal states
   stop refresh/SSE monitoring.
5. Generated tests contain no catalog-supplied executable code and are stable
   under identical catalog fingerprint, profile, and generator version.
6. Theme compatibility covers semantic tokens, parts, slots, forced colors,
   reduced motion, print, focus, and contrast evidence; private selectors are
   not part of the contract.
7. Discovery recommendations come from a versioned stability inventory.
   Fleet recommendations cite detected evidence and never install packages or
   enable plugins without a separate explicit action.

## Locked gate plan

| Gate | Verified means |
|---|---|
| `ASSET-053` | Ordered application assets pass dependency, placement, CSP/integrity, adapter, and no-rewrite cases. |
| `DIAG-053` | Applicability, aliases, suppressions, remediation actions, and machine formats pass. |
| `ROUTE-053` | Versioned route/effect documents are typed, deterministic, redacted, and non-executing. |
| `WORKFLOW-053` | Start/monitor/cancel/retry/terminal/busy/completion behavior passes without duplicate terminal monitoring. |
| `TESTGEN-053` | Deterministic catalog-generated tests cover page/HTMX/mount/error paths and detect drift. |
| `THEME-053` | Semantic-only custom-theme and visual-conformance matrices pass. |
| `DISCOVER-053` | Curated import/stability discovery is versioned and preserves existing imports. |
| `FLEET-053` | Read-only installed-fleet diagnosis reports train/extras/plugin/asset evidence honestly. |
| `DOCS-053` | Application, operator, security, migration, and troubleshooting docs pass. |
| `PKG-053` | Clean artifacts and 0.52 upgrade/rollback pass. |
| `REGRESS-053` | Whole-fleet regression passes with no hidden Deferred 0.53 claims. |

## Security implications

Asset paths and dependencies are validated before emission; integrity and CSP
remain fail-closed. Route export and test generation consume redacted metadata
only. Diagnostics do not expose secrets. Workflow status/cancel endpoints retain
authorization and CSRF requirements. Fleet doctor is read-only and redacts
environment paths, credentials, cookies, and package-manager tokens.

## Testing strategy

The evidence index names `scripts/check_*_053.py` commands. Stage 0 rows are
`Planned`; Stage 1 supplies implementations and Verified evidence. PKG-053
upgrade source is 0.52 (`v0.52.0`).

## Resolved questions (D-091 / D-092)

1. **Who owns 0.53?** RFC-0080 under D-091, with the #514–#521 issue packet
   bound directly to its eight workstreams.
2. **What is the baseline?** Published/Verified in-tree `v0.52.0`; target
   `v0.53.0`.
3. **Is this one feature?** No: eight workstreams, one application-DX cut and
   one shared exit gate.
4. **Which doctor is this?** Read-only installed-application fleet triage.
   External package-author validation remains 0.54 `DOCTOR-054`.
5. **Does workflow reopen polling-only?** No. It composes existing job and
   typed-effect seams and must cease monitoring at terminal state.
6. **Does Stage 0 change runtime or versions?** No.

Locks:
[application-dx-inventory-053.toml](../acceptance/application-dx-inventory-053.toml) ·
[application-assets-053.toml](../acceptance/application-assets-053.toml) ·
[application-contracts-053.toml](../acceptance/application-contracts-053.toml) ·
[application-tooling-053.toml](../acceptance/application-tooling-053.toml).

## Acceptance criteria

- RFC-0080 and D-091/D-092 are Accepted; #514–#521 are bound.
- Every owned gate is Planned with an evidence command.
- All four contract locks parse and agree on baseline, target, and boundaries.
- Stage 0 changes contracts only; living tip remains `v0.52.0`.
