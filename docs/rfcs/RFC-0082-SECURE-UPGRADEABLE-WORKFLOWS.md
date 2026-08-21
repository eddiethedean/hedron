# RFC-0082: Secure, upgradeable application workflows

**Status:** Accepted<br>
**Target phase:** 0.55 (`v0.55.0`)<br>
**Decision:** D-095<br>
**Stage 0 contract refine:** D-096<br>
**Planning baseline:** Published in-tree `v0.54.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.54.0`<br>
**Tracking:** [#544](https://github.com/eddiethedean/hedron/issues/544)–[#549](https://github.com/eddiethedean/hedron/issues/549)<br>

**Revision:** 2026-08-20 — D-095 ownership + D-096 Stage 0 refine against
Published in-tree `v0.54.0`. No Stage 0 runtime, version bump, or registry claim.

## Summary

Phase 0.55 delivers secure, inspectable primitives for common application
workflows: responsive master-detail composition, policy-aware affordances,
replay-safe mutations, validated multipart actions, security-header reporting,
and offline upgrade-impact reports. It extends the 0.54 application-composition
work without owning application RBAC, final security policy, storage backends,
or deployment infrastructure.

## Goals

- Master-detail / split-pane layout with named fragment regions, history/focus,
  and mobile collapse (`LAYOUT-055` / #544).
- Typed authorization-aware component capabilities with request-bound evaluation
  and server-side action enforcement (`CAP-055` / #546).
- Explicit idempotency and replay-safe action policies (`REPLAY-055` / #548).
- Typed multipart/file-upload fields and actions with limits and cleanup
  (`UPLOAD-055` / #549).
- Optional CSP/security-header reporting, request-scoped nonces, and bounded
  violation ingestion (`CSP-055` / #545).
- Offline application-level upgrade compatibility reports (`UPGRADE-055` / #547).
- Shared workflow contract manifest, reason codes, audit hooks, and budgets
  (`CONTRACT-055`), adapter parity (`PARITY-055`), packaging (`PKG-055`), and
  regression (`REGRESS-055`).

## Non-goals and exclusions

- RBAC/ABAC engine, malware scanner, object-storage implementation.
- General workflow orchestration or arbitrary CSS/JS layout escapes.
- Automatic security-policy authoring or blind source-to-source migration.
- Reopening `polling_only`, `MORPH-048`, `SR-021`, or scheduling Hedron `1.0`.
- Runtime symbols, numeric performance limits, version bumps, or living-tip
  movement during Stage 0.

## Consume shipped, do not fork (D-096)

| Area | Published 0.54 seams retained |
|---|---|
| Security / CSRF | `SecurityPolicy`, `SecurityHeadersPolicy`, double-submit CSRF, `prepare_csrf_from_request` |
| Navigation / layout | `AppShell`, `MainPanel`, `SplitView`, layout builtins, `Theme`, `default_styles` |
| Action handle | `@app.action` / `HedronRouter.action`, `_wrap_endpoint`, fragment regions |
| Interaction | `InteractionPolicy`, `FragmentRegion`, interaction catalog / manifest |
| Request model | Type-authoring `FormBody`, encoding auto-multipart for file fields |
| Route / effect | RouteMeta, `hedron routes`, effect catalog (0.53) |
| Authoring loop | `hedron_conformance.authoring_loop`, sample-kit / sim / notebook / package doctor |

Public shared schema import path (locked): **`hedron.workflow`**.

## Locked public types (Stage 1)

| Symbol | Package | Role |
|---|---|---|
| `MasterDetail` | `hedron-core` | Responsive list/detail with named regions |
| `Capability`, `CapabilityDecision`, `CapabilityProvider` | `hedron` | Request-bound authz affordances |
| `IdempotencyPolicy`, `ReplayStore`, `ReplayOutcome` | `hedron` | Opt-in mutation replay protection |
| `UploadField`, `UploadHandle`, `UploadBudget` | `hedron` | Typed multipart lifecycle |
| `CspReporting`, `NonceContext`, `ingest_csp_report` | `hedron` | Nonce + bounded report helpers |
| `WorkflowManifest`, `ReasonCode`, `WorkflowBudget` | `hedron.workflow` | Inspection model |
| `upgrade_report` / `hedron upgrade-report` | `hedron` CLI | Offline contract diff |

All new APIs are opt-in and `beta` for the first 0.55 release.

## Locked gate plan

| Gate | Verified means |
|---|---|
| `CONTRACT-055` | Workflow manifest, reason codes, budgets, schemas, and Accepted RFC/decision. |
| `LAYOUT-055` | Master-detail desktop/mobile/focus/history/region swap evidence. |
| `CAP-055` | Capability provider, render semantics, server enforcement, redaction. |
| `REPLAY-055` | Key/fingerprint/state machine, concurrency, retention, retry fixtures. |
| `UPLOAD-055` | Limits, filename validation, CSRF order, cleanup, adapter matrix. |
| `CSP-055` | Nonce lifecycle, report-only/enforcing, bounded redacted ingestion. |
| `UPGRADE-055` | Offline definite/heuristic diffs, JSON schema, reviewed baselines. |
| `PARITY-055` | FastAPI/Flask/Django supported/degraded/unsupported matrix. |
| `REGRESS-055` | 0.54 upgrade plus cancel/retry/disconnect/restart suites. |
| `PKG-055` | Wheel/install/API/docs/migration/reference/acceptance/release metadata. |

## Normative ordering

1. Request/body budgets and CSRF.
2. Authentication and capability enforcement.
3. Normalized idempotency-key validation and fingerprint comparison.
4. Atomic claim; business effect; durable outcome publication.

Failed authentication or authorization must not reserve a caller-controlled
replay key. Render-time capability results are never authorization tokens.

## Security implications

CSP reports are untrusted telemetry. Upload validation is not malware scanning.
Capability metadata must not leak sensitive policy details. Master-detail URL
state accepts only application-resolved identifiers without disclosing whether
an inaccessible record exists.

## Testing strategy

Evidence index names `scripts/check_*_055.py` commands. Stage 0 rows are
`Planned`; Stage 1 supplies implementations and Verified evidence. PKG-055
upgrade source is 0.54 (`v0.54.0`).

## Resolved questions (D-095 / D-096)

1. **Who owns 0.55?** RFC-0082 under D-095, issues #544–#549 bound.
2. **What is the baseline?** Published/Verified in-tree `v0.54.0`; target `v0.55.0`.
3. **Shared schema path?** `hedron.workflow`.
4. **Does Stage 0 change runtime or versions?** No.

Locks:
[workflow-inventory-055.toml](../acceptance/workflow-inventory-055.toml) ·
[workflow-contract-055.toml](../acceptance/workflow-contract-055.toml) ·
[workflow-parity-055.toml](../acceptance/workflow-parity-055.toml) ·
[workflow-upgrade-055.toml](../acceptance/workflow-upgrade-055.toml).

## Acceptance criteria

- RFC-0082 and D-095/D-096 are Accepted; #544–#549 are bound.
- Every owned gate is Planned with an evidence command.
- All four contract locks parse and agree on baseline, target, and boundaries.
- Stage 0 changes contracts only; living tip remains `v0.54.0`.
