# RFC-0054: ATAG-oriented authoring assistance

**Status:** Accepted
**Phase:** 0.19 (`v0.19.0`)
**Stability:** `beta` (tooling)
**Evidence:** `ATAG-019`
**Related:** RFC-0017, RFC-0023, RFC-0024, RFC-0051, RFC-0052; D-050;
[ATAG 2.0](https://www.w3.org/TR/ATAG20/)

## Summary

Apply ATAG-oriented authoring support across CLI, Explorer, previews, HDJ, inspect/eject,
generators, templates, examples, transformations, and the workflow editor so accessibility
properties, checks, and reversible repair guidance are first-class—without claiming a full ATAG
conformance statement by default.

## Motivation and background

Hedron’s authoring surfaces are authoring tools in the practical ATAG sense. Authors need
accessibility properties alongside ordinary props, preservation of accessibility metadata through
transforms, and repair guidance that remains author-reviewed.

## Proposed design

### Authoring surfaces (`ATAG-019`)

Across CLI, Explorer, previews, HDJ, inspect/eject, generators, templates, examples,
transformations, and the workflow editor:

- Accessibility properties are available alongside ordinary properties.
- Accessible choices are at least as prominent as inaccessible ones.
- Accessibility metadata survives generation, copy, conversion, and optimization.
- Checks locate source and explain which decisions require manual author judgment.
- Repair guidance is reversible and author-reviewed; AI-generated alternatives retain provenance
  and never auto-verify.
- Accessibility features are on by default and documented.

### Claims

An ATAG conformance claim requires a separate applicability report and evidence. The roadmap may
target applicable A/AA outcomes without claiming that all of ATAG is already satisfied.

### Metadata preservation

Failures during inspect/eject, serialization, caching, OOB swaps, or optimization preserve safe
ordinary-HTML alternatives and must not trap input or focus (shared exit gate with
`CONTRACT-019` / `EXPLORER-019`).

## Alternatives considered

1. **Docs-only ATAG guidance.** Rejected — not release-governed or testable as `ATAG-019`.
2. **Automatic repairs without author review.** Rejected — RFC-0023 / research deliberate
   constraints forbid unverified generated alternatives.
3. **Full ATAG certification as the 0.19 exit claim.** Rejected — requires separate applicability
   report; out of scope as an automatic framework claim.

## Security implications

Repair and transformation tools must not weaken TrustedHtml/SafeUrl boundaries or inject scripts.
Generated guidance is not executable host code.

## Accessibility implications

Authoring UIs themselves must meet applicable keyboard, name, and focus requirements so authors
with disabilities can use the tools (ATAG Part A orientation).

## Performance implications

Checks run in CLI/Explorer paths with deterministic budgets; full-catalog deep scans remain
opt-in or incremental.

## Testing strategy

- Preservation tests across generate/copy/convert/optimize/inspect/eject paths.
- Prominence and default-on behavior checks for accessibility property surfaces.
- Negative tests: rejected silent AI verification; reversible repair round-trips.

## Compatibility and migration

Additive diagnostics and property surfaces. Existing generators gain contract fields from
RFC-0051 rather than replacing public component APIs.

## Open questions

- How HDJ prologue declares accessibility-related feature IDs.
- Shared repair-guidance schema between CLI SARIF and Explorer UI.

## Acceptance criteria

- ATAG-oriented assistance is available on listed authoring surfaces (`ATAG-019`).
- Metadata survives the transformation matrix in the 0.19 exit gate.
- No automatic full ATAG conformance claim is emitted by default.
