# RFC-0065: Production-grade MCP projection (`hedron-mcp`)

**Status:** Accepted

**Target phase:** 0.32 (`v0.32.0` train; `hedron-mcp` `0.2.0` Beta)

**Stability:** `beta` (process / package-graduation contract for the declared Supported MCP inventory)

**Evidence:** [RELEASE_0_32.md](../acceptance/RELEASE_0_32.md) ·
[release-gate-0.32.toml](../acceptance/release-gate-0.32.toml) ·
[production-grade-inventory-032.toml](../acceptance/production-grade-inventory-032.toml) ·
[security-review-032/BRIEF.md](../acceptance/security-review-032/BRIEF.md)

**Related:** D-015, D-053, D-060; [RFC-0043](RFC-0043-MCP-PROJECTION.md) (Alpha product
contract); [RFC-0056](RFC-0056-PRODUCTION-QUALITY.md);
[ROADMAP §0.32](../ROADMAP.md); tracking
[#89](https://github.com/eddiethedean/hedron/issues/89)

## Summary

Apply the ROADMAP **production-grade package contract (0.26+)** to the optional
`hedron-mcp` distribution so the **deny-by-default, authenticated MCP projection**
leaves Experimental Alpha for an explicit Supported inventory.

| Package | Production-grade scope at exit |
|---|---|
| `hedron-mcp` | Deny-by-default Streamable HTTP mount; explicit resource/tool registration; host authn reuse; app-owned authz/tenant hooks; fail-closed empty mount; read resources and read-only tools under documented bounds, audit, and cancellation |

[RFC-0043](RFC-0043-MCP-PROJECTION.md) remains the Alpha product contract shipped in
phase 0.17. This RFC is the **graduation** contract: gate IDs, machine-readable
inventory, version policy, independent security review, and cut rules. It does not
reopen the 0.17 Alpha ship or move MCP into core.

**Production-grade MCP** means install and mount grant **no** ambient authority;
every resource/tool/action is explicitly registered, scoped to the caller, bounded,
observable, cancellable, and safe under multi-worker deployment. It does **not**
make Hedron an identity provider, secrets broker, approval system, or tenant model,
and it does not schedule Hedron `1.0`.

## Motivation

Phase 0.17 shipped Experimental Alpha `hedron-mcp` (`MCP-017`). Phases 0.26–0.31
graduated core, satellites, charts/native, Workbench, and tooling under the 0.26+
contract while explicitly deferring MCP. Adopters need a pinned protocol/SDK matrix,
Supported-versus-Experimental inventory, adversarial authz evidence, and an
independent threat review before maturity labels change.

## Design

### Package dispositions and version policy

| Surface | At packet refine | At `v0.32.0` cut |
|---|---|---|
| `hedron-mcp` package maturity | Experimental Alpha `0.1.x` | Beta `0.2.0` (independent satellite line) |
| Pin guidance | `>=0.1.0,<0.2` | `>=0.2.0,<0.3` |
| Upgrade source | — | Alpha `0.1.x` consumers |
| Train alignment | Depends on `hedron-core` / extras floor for the living tip | Coordinated with Hedron train `v0.32.0`; package version stays satellite `0.2.0` (not train-locked `0.32.0`, not `1.0.0`) |

### Supported inventory freeze

Machine-checked in
[production-grade-inventory-032.toml](../acceptance/production-grade-inventory-032.toml):

- Deny-by-default Streamable HTTP mount (`mount_mcp` / equivalent)
- Explicit resource and tool registration APIs
- Fail-closed empty server when installed, mounted, or enabled with zero registrations
- Read resources and read-only tools under principal-bounded authz
- Host authentication reuse (no separate IdP)
- Application-owned authorization and tenancy hooks with fail-closed defaults
- Rate/size/concurrency/deadline/cancel/disconnect bounds for Supported paths
- Redacted structured audit/diagnostics for registration, authorization, execution,
  cancellation, and failure

### Experimental leftovers (excluded from package-level Supported claims)

- Mutating tools without full 0.32 evidence (idempotency/replay/audit/enablement)
- Vendor-specific MCP extensions and non-Streamable transports
- Auto-composition with Gradio or other agent frameworks
- Ambient projection of components, routes, Explorer panels, or OpenAPI surfaces

### Gate IDs

`PROTOCOL-032`, `AUTHZ-032`, `BOUNDS-032`, `AUDIT-032`, `REVIEW-032`, plus shared
`REGRESS-032` / `PKG-032`.

Planned checker / verifier names (implementation belongs to the 0.32 engineering
train, not this docs refine):

| Gate | Planned command |
|---|---|
| `PROTOCOL-032` | `python scripts/check_protocol_032.py` |
| `AUTHZ-032` | `python scripts/check_authz_032.py` |
| `BOUNDS-032` | `python scripts/check_bounds_032.py` |
| `AUDIT-032` | `python scripts/check_audit_032.py` |
| `REVIEW-032` | `python scripts/check_review_032.py` |
| `REGRESS-032` | `python scripts/check_regress_032.py` |
| `PKG-032` | `python scripts/verify_pkg_32.py` |

Inventory agreement with public docs and package metadata is required for
`PKG-032`.

### Auth story

- **Authentication:** MCP reuses the host application’s authn (sessions, bearer, or
  other application-owned wiring). Hedron does not become an IdP.
- **Authorization:** Application-owned hooks must fail closed. Authorization must
  match the underlying HTTP/UI/job action contracts (RFC-0043). UI option filtering
  is not authorization.
- **Tenancy:** Cross-tenant observation and identifier enumeration are cut-blocking
  under `AUTHZ-032`.
- **Confused deputy:** Tools must not widen authority relative to the authenticated
  principal across HTTP, UI, job, resource, and tool surfaces.

### Deny-by-default checkable claims (`PKG-032` / inventory)

- Install alone grants no resources or tools
- Mount / enable with zero registrations yields an empty server (no ambient
  component, route, or OpenAPI projection)
- Mutations require explicit enablement plus idempotency/replay/audit evidence; without
  that evidence they remain Experimental

### Independent security review (`REVIEW-032`)

Scope brief: [security-review-032/BRIEF.md](../acceptance/security-review-032/BRIEF.md).
Cut requires no unresolved critical/high finding for the Supported inventory.

### Non-goals

- Default-public tools, automatic projection of components/routes, or ambient
  application authority from install/mount
- Acting as an identity provider, secrets broker, approval system, or tenant model
- Arbitrary Python/shell/URL/filesystem execution from model input
- Treating MCP protocol conformance as equivalent to application tool safety
- Gradio MCP substitute or auto-composing Gradio tools (phase 0.33 owns Gradio)
- Scheduling Hedron `1.0`, SLA, or certification claims

## Acceptance

- Every 0.32-owned gate row Verified with zero Deferred at cut
- Production-grade / Beta maturity labels used only for the declared Supported inventory
- `python scripts/verify_pkg_32.py` passes without `--allow-planned` at cut
- Tracking [#89](https://github.com/eddiethedean/hedron/issues/89) closes only when
  those gates are Verified and `hedron-mcp` publishes `0.2.0` Beta for the Supported
  inventory
