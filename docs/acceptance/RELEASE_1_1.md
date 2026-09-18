# Hedron `v1.1.0` open enhancement acceptance plan

**Status:** **Verified and published as `v1.1.0` on 2026-09-18**
**Target:** `v1.1.0`
**Authority:** [RFC-0098](../rfcs/RFC-0098-OPEN-ENHANCEMENT-COMPLETION.md)
**Implementation:** [OPEN_ENHANCEMENTS_1_1](../implementation/OPEN_ENHANCEMENTS_1_1.md)
**Machine packet:** [release-gate-1.1.toml](release-gate-1.1.toml)

This packet replaces the former 1.1 testing packet, which moves to
[Phase 1.2](RELEASE_1_2.md) with its gate IDs renumbered from `*-110` to `*-120`.
All rows below are Verified against the Phase 1.1 implementation, unit suite, and documentation
source-of-truth checks. There is no `check_110.py`; the packet uses the repository’s existing
release and test commands.

## Required evidence

| Gate | Required result |
|---|---|
| `FREEZE-110` | Current-source reconciliation for all 20 issues; exact additive APIs, named owners, package/maturity matrix, complementary tasks, reference corpus, measured budgets, and accepted contract decisions |
| `ERROR-110` | #891: unknown/unauthorized targets stay rejected; only trusted error sinks are allowed; no recursive rejection; original status/approved headers and non-HTMX fallback survive |
| `BUILD-110` | #892: build-safe CLI/config/factory application loading; deterministic theme/style/script manifests; runtime mismatch detection; no-app library mode, imports/collisions/path/remote-asset failures, mount-independent assets |
| `URL-110` | #893: purpose-aware request-bound navigation/form/asset/Location/HX-Redirect matrix across root, prefixes, Workbench, Connect, and inactive modes; query/fragment/Unicode preservation and traversal/open-redirect rejection |
| `IDENTITY-110` | #889: display-safe identity, async provider, generic resources, safe missing-provider behavior, deterministic overrides/Explorer previews, optional integrations, and independently enforced server denial |
| `COLLECTION-110` | #890: bounded direct/endpoint sources, page/cursor modes, optional fastapi-pagination adapter, server sort/filter, URL history, counts/states/accessibility, and representative AuthMate/ShuETL/Datdex fixtures |
| `FORM-110` | #916–#919/#944: validated keep/replace/clear; no secret echo; coherent help/IDs/errors/summary/focus; guards handle commit/reset, failed/pending/stale saves and session expiry; measured natural/shared-label alignment |
| `PRESENTATION-110` | #913/#914/#939–#943/#945/#946: additive Dialog hooks, distinct elevations, finite shell/Brand/ProcessFlow/toggle policies, safe defaults, shared manifest coverage, and native/component stylesheet parity |
| `STYLE-110` | #915: browser evaluates bounded declared style/geometry relationships; enum/breakpoint coverage or reviewed exclusions; regression mutations fail; loaded-asset provenance and expected/actual values appear in failures; missing runtime is incomplete |
| `COMPLEMENT-110` | W1–W4 complementary behavior composes: asset provenance, provider/URL collection state, secure form lifecycle, measured shell geometry, and consistent presentation metadata; each task has linked evidence |
| `FLOW-110` | W5 packaged reference flow demonstrates identity-aware pagination, guided secret settings, error recovery, unsaved guard, successful save, native chrome, sealed assets, and trusted-prefix deployment |
| `ASSURANCE-110` | Compatible 1.0 defaults/imports, security/redaction/cache isolation, keyboard/focus/no-JS, RTL/zoom/forced-colors/reduced-motion, browser matrix, bounded resources/cleanup, optional packaging, documentation, and rollback evidence |
| `RELEASE-110` | Every required non-release row Verified; all 20 issues have linked implementation/evidence; required complements complete; per-capability maturity and support statements approved; immutable artifacts and release/rollback disposition recorded |

## Scope and evidence rules

The exact issue inventory is in the implementation plan and `required_issues` in the machine
packet. The full issue acceptance criteria remain authoritative; grouping issues does not remove
requirements. New ideas enter only through a recorded scope amendment. Deferring required work
requires the same amendment and matching packet/roadmap updates.

Static/render checks remain a separate fast tier. Browser effects require actual browser evidence;
markers, accepted props, screenshots alone, or skipped required rows cannot pass style contracts.
Secret fixtures use synthetic values and redact replacements from captured evidence. Numeric limits
are frozen from measured baselines. Required runtime/dependency rows pass rather than skip.

The reference flow preserves framework authorization, stable 1.1 behavior, and application-owned
domain/storage/preference responsibilities. The release decision and package versions are recorded
as `v1.1.0`; close issues only after the implementation and evidence are linked.
