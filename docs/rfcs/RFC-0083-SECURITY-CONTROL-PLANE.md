# RFC-0083: Security control plane and adversarial assurance

**Status:** Accepted<br>
**Target phase:** 0.56 (`v0.56.0`)<br>
**Decision:** D-097<br>
**Stage 0 contract refine:** D-098<br>
**Planning baseline:** Published in-tree `v0.55.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.55.0`<br>
**Tracking:** [#550](https://github.com/eddiethedean/hedron/issues/550)–[#557](https://github.com/eddiethedean/hedron/issues/557)<br>

**Revision:** 2026-08-20 — D-097 ownership + D-098 Stage 0 refine against
Published in-tree `v0.55.0`. No Stage 0 runtime, version bump, or registry claim.

## Summary

Phase 0.56 composes and hardens existing security mechanisms into one inspectable
control plane. Every Hedron-controlled request crosses shared authorities for
context, sensitivity, sinks, egress, signed intents, and request budgets.
Supported hosts prove the same portable invariants with threat-oriented evidence.
It does not reopen 0.55 workflow scope or promote experimental transports.

## Goals

- Permanent versioned cross-adapter security conformance profile (`CONFORM-056` / #550).
- Provenance-aware sensitive-data labels and sink enforcement (`SENS-056` / #551).
- Immutable request `SecurityContext` with serialization and narrowing (`CTX-056` / #552).
- Offline `hedron security-check` posture report (`POSTURE-056` / #553).
- Purpose-specific trust-boundary sink compiler (`SINK-056` / #554).
- Shared outbound egress/SSRF policy (`EGRESS-056` / #555).
- Short-lived signed action intents (`INTENT-056` / #556).
- Framework-wide streaming `RequestBudget` ledger (`BUDGET-056` / #557).
- Contract, adversary, performance, regression, and packaging gates.

## Non-goals and exclusions

- Identity provider, RBAC/ABAC engine, secrets vault, hosted KMS, WAF, malware
  scanner, SIEM, compliance certification, vulnerability scanner, network proxy,
  or infrastructure sandbox.
- Arbitrary Python information-flow tracking; live production probing.
- Defending against trusted in-process application/plugin code with memory, key,
  or raw-socket access.
- Claiming transport-level streaming enforcement from hosts that only expose
  pre-buffered bodies.
- Reopening `polling_only`, `MORPH-048`, `SR-021`, 0.55 workflow scope, or
  scheduling Hedron `1.0`.
- Runtime symbols, numeric performance limits, version bumps, or living-tip
  movement during Stage 0.

## Composition naming (locked)

Today's `SecurityProfile` StrEnum (`development` / `standard` / `strict`) remains
the preset namespace via `SecurityPolicy.from_name()`. The 0.56 **composition
object** is the evolved versioned **`SecurityPolicy`** dataclass (additional
fields for conformance version, trust/sink/egress/intent/budget/posture knobs).
ROADMAP's illustrative "SecurityProfile composition" name is corrected onto this
shipped seam (D-098).

Public shared schema import path (locked): **`hedron_core.security_plane`**
(re-exported from `hedron.security_plane` for FastAPI apps).

## Consume shipped, do not fork (D-098)

| Area | Published 0.55 seams retained |
|---|---|
| Security / CSRF | `SecurityPolicy`, `SecurityHeadersPolicy`, double-submit CSRF |
| Trust types | `SafeUrl`, `UrlPurpose`, `TrustedHtml`, `Secret` |
| Auth signal | `AuthSignal` (not a substitute for `SecurityContext`) |
| Workflows | capabilities, `IdempotencyPolicy`/`ReplayStore`, upload/CSP budgets |
| Package egress | maps `assert_ssrf_safe`, Gradio remote policy, MCP origin bounds |
| Diagnostics | `hedron check` text/JSON/SARIF plumbing |
| Conformance | `hedron-conformance` kit scaffolding (PROFILE-052) |

## Locked public types (Stage 1)

| Symbol | Package | Role |
|---|---|---|
| `SecurityPolicy` (extended) | `hedron-core` | Versioned composition object |
| `SecurityContext` | `hedron-core` | Immutable request-local authority |
| `SensitiveLabel` / `SensitiveValue` | `hedron-core` | Provenance labels + declassification |
| `TrustPurpose` / `compile_trust` | `hedron-core` | Purpose-specific sink compiler |
| `EgressPolicy` / `EgressDecision` | `hedron-core` | Deny-by-default outbound decisions |
| `RequestBudget` | `hedron-core` | Nested monotonic request ledger |
| `SignedIntent` / `IntentStore` | `hedron-core` / `hedron` | Short-lived action intents |
| `SecurityKeyring` | `hedron-core` | Purpose-bound key lifecycle |
| `SecurityEvent` | `hedron-core` | Stable denied-boundary events |
| Security conformance profile | `hedron-conformance` | Portable differential fixtures |
| `hedron security-check` | `hedron` CLI | Offline posture (read-only) |

All new 0.56 public APIs begin `beta`.

## Locked gate plan

| Gate | Verified means |
|---|---|
| `CONTRACT-056` | Accepted RFC/decisions; schemas; threat/boundary maps; fixtures |
| `CONFORM-056` | #550 machine-readable profile + FastAPI/Flask/Django differentials |
| `SENS-056` | #551 labels, sinks, declassification audit, retention |
| `CTX-056` | #552 immutable context, serialization, narrowing, isolation |
| `POSTURE-056` | #553 `security-check` human/JSON/SARIF + exit semantics |
| `SINK-056` | #554 purpose compiler + equivalence + dispositions |
| `EGRESS-056` | #555 deny-by-default + DNS/redirect + injected transport |
| `INTENT-056` | #556 bind/consume + keyring + multi-worker one-time use |
| `BUDGET-056` | #557 request ledger + earliest-enforcement + cleanup |
| `ADVERSARY-056` | Shared adversarial/fuzz corpus across adapters/packages |
| `PERF-056` | Measured ceilings locked with default-selection evidence |
| `REGRESS-056` | 0.55 upgrade + cancel/retry/disconnect/restart suites |
| `PKG-056` | Wheel/install/API/docs/migration/inventory/release metadata |

## Package ownership

- `hedron-core` — policy values, trust compilation, labels/events, budget/keyring
  protocols, transport-neutral egress decisions (no host/HTTP-client/conformance deps).
- `hedron` / Flask / Django / Posit — host ingress, request binding, typed failures,
  action integration; may tighten, never weaken the floor.
- `hedron-conformance` — portable profile schema, fixtures, differential runner.
- Concrete HTTP transports/stores/crypto remain injected or in packages that already
  own the dependency.

## Normative ordering

1. Install `SecurityPolicy` + request-local `RequestBudget` before Hedron body expansion.
2. CSRF, authentication, capability, and signed-intent validation before side effects.
3. `SecurityContext` may only narrow; serialization captures only allowed fields.
4. Sensitivity labels authoritative at framework sinks; heuristics are defense in depth.
5. Dangerous sinks compile through purpose-specific types; cross-purpose reuse fails closed.
6. Egress binds connection to policy-validated resolution; revalidate every redirect hop.
7. Replay (0.55) and intents compose; neither substitutes for CSRF or object-level authz.
8. Posture reports remain read-only and offline-capable.

## Testing strategy

Evidence index names `scripts/check_*_056.py` commands. Stage 0 rows are
`Planned`; Stage 1 supplies implementations and Verified evidence. PKG-056
upgrade source is 0.55 (`v0.55.0`).

## Resolved questions (D-097 / D-098)

1. **Who owns 0.56?** RFC-0083 under D-097, issues #550–#557 bound.
2. **What is the baseline?** Published/Verified in-tree `v0.55.0`; target `v0.56.0`.
3. **Composition object?** Evolved `SecurityPolicy`; `SecurityProfile` stays presets.
4. **Shared schema path?** `hedron_core.security_plane`.
5. **Does Stage 0 change runtime or versions?** No.
