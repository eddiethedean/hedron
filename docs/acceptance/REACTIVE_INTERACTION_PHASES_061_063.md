# Acceptance rules: reactive interaction phases 0.61–0.63

**Status:** Proposed  
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)

This document defines shared evidence semantics. Phase gates live in
[RELEASE_0_61](RELEASE_0_61.md), [RELEASE_0_62](RELEASE_0_62.md), and
[RELEASE_0_63](RELEASE_0_63.md). These are plans, not implementation or availability claims.

## Maturity rules

| Disposition | Release meaning |
|---|---|
| Required | Must be Verified for the phase to release; zero Deferred rows. |
| Progressive | May enhance a Required fallback; absence/failure cannot break correctness. |
| Experimental | May ship only with explicit labeling, isolation, and no Supported claim. |
| Deferred | Not delivered in this phase; owner, reason, destination, and stability impact required. |
| Excluded | Deliberate non-goal; tests/docs prevent accidental support claims where useful. |

An API, adapter, demo, or passing unit test is not sufficient to change maturity. The accepted
machine-readable inventory is authoritative.

## Gate status

Planned gate rows use `Planned`. Stage 0 may change them to `Accepted` after contracts, commands,
budgets, and artifacts are locked. Implementation evidence changes them to `Verified`. A row cannot
be Verified by narrative alone.

## Required evidence packet per phase

Each release produces versioned, deterministic artifacts for:

- capability/disposition inventory;
- public contract/schema lock;
- resolved theme/component-contract inventory for any phase that consumes the 0.60 theme authority;
- host, transport, package, and browser dispositions;
- diagnostic catalog and suppression rules;
- security/redaction and accessibility matrices;
- numeric resource/performance budgets with baseline environment;
- compatibility and before/after upgrade fixtures;
- reference-app journey inventory;
- package/runtime identity and clean-install proof; and
- release-gate status with exact commands and artifact hashes.

Artifact names in the phase plans are proposed until Stage 0. Do not create empty TOML files merely
to satisfy a filename.

## Shared verification rules

1. Commands run from a clean checkout/package environment and identify platform/tool versions.
2. Evidence covers native HTML, no-JavaScript fallback, HTMX when Progressive, and elements where
   Required.
3. Browser evidence covers the Stage 0 locked Chromium/Firefox/WebKit matrix and feature-absent paths.
4. Security tests include CSRF, auth, tenant, replay/idempotency, target, redirect, cache, payload,
   redaction, and permission-change cases where applicable.
5. Accessibility evidence covers semantics, keyboard, focus, announcements, reduced motion, high
   contrast/forced colors, zoom/reflow, and cleanup; human-AT claims remain separate.
6. Race evidence covers late, duplicate, cancelled, retried, reconnected, expired, conflicting, and
   unauthorized outcomes.
7. Resource evidence tests baseline, exact limit, one over limit, degradation, cleanup, and repeated
   operation behavior.
8. Multi-worker/process evidence proves no correctness dependence on in-memory affinity unless that
   limitation is an explicit non-Supported disposition.
9. Public docs, generated metadata, theme exports/inspection, Explorer, CLI, package manifests, and
   runtime report the same maturity, version, and component-contract facts.
10. Every Progressive/Experimental path is disabled during fallback evidence.

## Cross-phase release rule

0.62 cannot release against an unverified or locally reinterpreted 0.61 schema. 0.63 cannot release
with a trace, identity, outcome, theme, or component-contract interpretation that differs from the
accepted 0.60/0.61/0.62 authorities. Compatibility fixtures for the immediately preceding release
are Required even if all three phases are developed on one branch.

## Supported-claim exclusions

No phase may claim React compatibility, automatic React conversion, offline-first synchronization,
live transport as a production default, or equivalent behavior merely because a recipe or adapter
exists. React islands, SSE, WebSockets, preload, and View Transitions remain outside Required
correctness unless a future RFC explicitly changes their dispositions.
