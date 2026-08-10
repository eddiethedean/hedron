# REVIEW-026 redacted security review report

**Gate:** REVIEW-026  
**Baseline:** Published `v0.25.2`  
**Packages:** `hedron-core`, `hedron`, `hedron-explorer`  
**Date:** 2026-08-10  
**Method:** Structured maintainer-led review of the frozen CONTRACT-026 inventory
against ROADMAP trust boundaries (escaping, fragment/OOB authz, CSRF/session,
build/static serving, plugin discovery, job observation, Explorer exposure),
backed by the adversarial CI suite.

## Executive summary

No open **critical** or **high** findings remain. High findings related to
Explorer production refusal and experimental live-API leakage were verified
fixed by existing fail-closed behavior and packet tests. Medium/low items are
owned with deadlines in `DISPOSITION.toml`.

## Boundary results

| Boundary | Result |
|---|---|
| Escaping / trusted HTML | Adversarial suite asserts unsafe markup is escaped in Supported render path |
| Fragment / OOB authorization | Region allowlist failures remain fail-closed |
| CSRF / session composition | Standard/strict profiles still require CSRF on mutating HTMX paths |
| Build / static serving | Production asset manifest path retained; no path traversal in SafeUrl tests (0.25.2) |
| Plugin discovery | Entry-point loading does not auto-enable experimental live transports |
| Job observation | Polling Supported; SSE/WS remain experimental |
| Explorer exposure | Secured requires auth; development disabled in production; off by default in archetype |

## Critical / high

All critical/high dispositions are **fixed** (see `DISPOSITION.toml`).

## Residual risk

Process-local Explorer audit buffers and plugin entry-point trust remain
accepted risks with owners/deadlines. They do not block the production-grade
label for the declared Supported CRUD/admin inventory.

## Attestation

This redacted report is the REVIEW-026 evidence artifact. Raw notes with
environment specifics are omitted from the public tree.
