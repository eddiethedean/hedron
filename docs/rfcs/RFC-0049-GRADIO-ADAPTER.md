# RFC-0049: Optional hedron-gradio protocol adapter

**Status:** Accepted
**Phase:** 0.18 (`v0.18.0`); package maturity Alpha `0.1.x`
**Stability:** `experimental` (API and distribution)
**Evidence:** `GRADIO-018`, `MIGRATE-018`
**Package:** optional `hedron-gradio` distribution (D-015 / D-049); not embedded in core
**Related:** [Gradio feature cross-check](../GRADIO_FEATURE_CROSSCHECK.md);
RFC-0014, RFC-0016, RFC-0045, RFC-0047, RFC-0050; D-049

## Summary

Define an optional `hedron-gradio` interoperability package for Gradio endpoint discovery, typed
file/artifact transport, authentication, session state, job status/cancel, and streamed results,
plus FastAPI coexistence guidance and a Gradio migration inventory. Absence of the package adds
no core dependency, route, asset, or startup cost. Deliberate non-parity is documented.

## Motivation and background

Teams often need to call existing Gradio endpoints or migrate demos into Hedron without adopting
Gradio’s UI runtime as a second application model. Hedron should offer a portable protocol adapter
and reviewable migration guidance while keeping core free of Gradio cost when the package is
absent.

## Proposed design

### hedron-gradio (Alpha)

- Gradio client protocol: discovery, typed file/artifact transport, authentication, session,
  job status/cancel, and streamed results.
- Contract tests against the supported upstream Gradio version range, including version-mismatch
  errors.
- FastAPI coexistence guidance (mount beside Hedron) without embedding Gradio’s UI runtime in
  `hedron-core`.
- Optional Hugging Face Space/OAuth/ZeroGPU vendor nodes as thin adapters over the portable
  workflow contract (RFC-0050) — not Hub hosting in core.
- Flagship extra: `hedron[gradio]`; pin `hedron-core` on the 0.19 train (`>=0.19.0,<0.20`).

### Migration inventory (`MIGRATE-018`)

Document mapping and deliberate non-parity for:

- mutable globals as app state;
- default-public UI→API publication;
- raw JS/HTML injection;
- current-directory file exposure;
- public share tunnels;
- deployed host-code editing (“vibe” mode);
- embedding Gradio’s UI runtime in core;
- treating feedback as ground truth.

Migration diagnostics for app builders, components, events, state, queues/batches, API visibility,
raw HTML/JavaScript, file paths, and share links are reviewable guidance — not automatic
conversion.

## Alternatives considered

1. **Embed Gradio UI runtime in core.** Rejected — D-049; optional package only.
2. **Claim class-for-class Gradio parity.** Rejected — outcome-oriented mapping with deliberate
   non-parity.
3. **Docs-only migration without contract tests.** Rejected — `GRADIO-018` requires protocol
   evidence against the supported range.

## Security implications

Adapter authentication and file transport reuse Hedron authorization, size, content-type, and
cleanup contracts. Credentials are never recorded (RFC-0048). Share tunnels and host-code editing
remain non-parity. Absence of the package must not register routes or assets.

## Accessibility implications

Adapter surfaces that render Hedron UI reuse core a11y contracts. Migration docs call out where
Gradio patterns lack keyboard/no-JS fallbacks and how Hedron alternatives apply.

## Performance implications

Optional package lazy-loads. Core CI and startup remain free of Gradio import cost. Contract suites
run when the package is installed.

## Testing strategy

Protocol contract tests for discovery, files, auth, sessions, status/cancel, streaming, errors, and
version mismatch (`GRADIO-018`). Migration inventory asserts deliberate non-parity coverage
(`MIGRATE-018`). Core tests pass without Gradio installed.

## Compatibility and migration

Independent Alpha version line (`0.1.x`). Supported Gradio range is declared in package metadata
and the cross-check. Breaking upstream protocol changes fail closed with version-mismatch
diagnostics.

## Open questions

None blocking Acceptance. Vendor HF nodes may remain experimental until Space/OAuth evidence is
Verified; portable protocol claims still ship.

## Acceptance criteria

- Gradio interoperability is contract-tested against the supported upstream range.
- Absence of `hedron-gradio` adds no core dependency, route, asset, or startup cost.
- Migration inventory documents deliberate non-parity without auto-conversion claims.
- Gate evidence under `GRADIO-018` and `MIGRATE-018`.
