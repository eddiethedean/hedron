# RFC-0067: Production-grade Gradio client interoperability (`hedron-gradio`)

**Status:** Accepted

**Target phase:** 0.34 (`v0.34.0` train; `hedron-gradio` `0.2.0` Beta)

**Stability:** `beta` (process / package-graduation contract for the declared Supported client-interop inventory)

**Evidence:** [RELEASE_0_34.md](../acceptance/RELEASE_0_34.md) ·
[release-gate-0.34.toml](../acceptance/release-gate-0.34.toml) ·
[production-grade-inventory-034.toml](../acceptance/production-grade-inventory-034.toml) ·
[security-review-034/BRIEF.md](../acceptance/security-review-034/BRIEF.md)

**Related:** D-062; [RFC-0049](RFC-0049-GRADIO-ADAPTER.md) (Alpha product contract);
[ROADMAP §0.34](../ROADMAP.md); tracking
[#90](https://github.com/eddiethedean/hedron/issues/90)

## Summary

Apply the ROADMAP **production-grade package contract (0.26+)** to the optional
`hedron-gradio` distribution so **explicitly declared remote Gradio endpoints and
Hugging Face Spaces** leave Experimental Alpha for a bounded Supported client-interop
inventory.

| Package | Production-grade scope at exit |
|---|---|
| `hedron-gradio` | Allowlisted destinations; pinned upstream matrix; bounded file/stream transport; auth/secret hygiene; cancellation and disconnect cleanup; Hedron polling job integration; redacted diagnostics |

[RFC-0049](RFC-0049-GRADIO-ADAPTER.md) remains the Alpha product contract shipped in
phase 0.18. This RFC is the **graduation** contract: gate IDs, machine-readable
inventory, version policy, independent security review, and cut rules. It does not
embed Gradio's UI runtime or reopen the 0.18 Alpha ship.

**Production-grade Gradio interop** means remote calls require explicit destination
and endpoint declarations, fail closed on policy violations, bound files and streams,
and never treat provider output as trusted HTML or ground truth. It does **not**
schedule Hedron `1.0` or promise remote provider availability.

## Motivation

Phase 0.18 shipped Experimental Alpha `hedron-gradio` (`GRADIO-018`). Phases 0.26–0.33
graduated core, satellites, MCP, and Posit adapters while explicitly deferring Gradio.
Adopters need allowlisted egress, adversarial file/stream bounds, vendor compatibility
evidence, and an independent threat review before maturity labels change.

## Design

### Package dispositions and version policy

| Surface | At packet refine | At `v0.34.0` cut |
|---|---|---|
| `hedron-gradio` package maturity | Experimental Alpha `0.1.x` | Beta `0.2.0` (independent satellite line) |
| Pin guidance | `>=0.1.0,<0.2` | `>=0.2.0,<0.3` |
| Upgrade source | — | Alpha `0.1.x` consumers |
| Train alignment | Depends on `hedron-core` floor for living tip | Coordinated with Hedron train `v0.34.0`; package version stays satellite `0.2.0` |

### Supported inventory freeze

Machine-checked in
[production-grade-inventory-034.toml](../acceptance/production-grade-inventory-034.toml):

- Explicit endpoint declarations; disabled-by-default adapter
- Allowlisted destination hosts/schemes with SSRF/redirect/TLS defenses
- Bounded upload/download types and sizes with artifact retention TTL and cleanup
- Queue/predict/stream timeouts, cancellation, disconnect cleanup
- Hedron polling job status integration for multi-worker evidence
- Pinned `gradio_client` matrix with schema drift detection
- Redacted diagnostics; HF Space auth scope for Supported vendor paths

### Experimental leftovers (excluded from package-level Supported claims)

- Gradio MCP auto-composition
- Arbitrary caller-provided remote URLs without allowlist
- Gradio share tunnels and UI runtime embed
- Vendor extensions without full evidence

### Threat model

- SSRF via destination allowlist bypass, redirect chains, DNS rebinding
- Credential leakage in logs, errors, and diagnostics
- Unbounded file/stream retention and path traversal in artifacts
- Cross-tenant job id enumeration when scopes are missing

### Gate ownership

| Gate | Owner |
|---|---|
| `CONTRACT-034` … `VENDOR-034`, `REVIEW-034`, `DOCS-034` | `hedron-gradio` |
| `REGRESS-034`, `PKG-034` | `hedron` (train) |
| `PRESENT-034` | `hedron-core` (optional; non-blocking for Gradio cut) |

## Non-goals

- Embedding or cloning Gradio's UI runtime, mutable globals, or share tunnels
- Allowing arbitrary caller-provided remote URLs, endpoint names, files, or credentials by default
- Remote host-code editing or treating provider output as trusted HTML/files/ground truth
- Gradio MCP substitute (phase 0.32 MCP inventory excludes `gradio_auto_composition`)
- Scheduling Hedron `1.0`, SLA, or certification claims

## Acceptance

- RFC-0067 Accepted before `v0.34.0` cut
- Every 0.34-owned Gradio gate Verified with zero Deferred
- `hedron-gradio` leaves Alpha for declared client-interop scope only
- Absence of `hedron-gradio` adds no core dependency, route, asset, or startup cost
