---
description: What's new in Hedron 0.61 unified action state and async boundaries.
search:
  boost: 1.4
---

# What's new in 0.61

Hedron 0.61 is verified, tagged, and published on PyPI. Applications use
`hedron>=0.63.0,<0.64`.

## Highlights

- Unified `ActionState` lifecycle and `OperationIdentity` across forms, actions, jobs, fragments,
  and supported elements.
- Server-authored `AsyncRegion` states for idle, pending, empty, success, error, timeout,
  cancelled, stale, conflict, and explicit retry.
- Stale-generation rejection, bounded retry/idempotency policy, redacted portable interaction
  traces, and deterministic lifecycle diagnostics.
- Additive `Tabs`, `Container`, `NavGroup`, `AmbientBackdrop`, and default-theme `Identity`
  contracts for server-rendered application surfaces.
- Ordinary full-page and fragment fallback remains the correctness path; no hydration or client
  interaction runtime is required.

## Compatibility and boundaries

Existing handles, forms, jobs, fragments, HTMX markup, and element constructors remain valid when
0.61 arguments are omitted. Flask and Django retain their existing adapter behavior; HTMX remains
Progressive, while SSE/WebSocket delivery remains Experimental. Human assistive-technology session
sign-off remains outside this phase and is tracked by issue [#86](https://github.com/eddiethedean/hedron/issues/86).

See the [release notes](release-notes.md), [upgrade guide](upgrade.md), and
[0.61 release packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md).
