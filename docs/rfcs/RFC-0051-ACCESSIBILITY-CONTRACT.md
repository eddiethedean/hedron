# RFC-0051: AccessibilityContract

**Status:** Draft
**Phase:** 0.19 (`v0.19.0`)
**Stability:** `beta` (API)
**Evidence:** `CONTRACT-019` (primary); contributes to `INTERACT-019`, `MEDIA-019`, `COG-019`,
`I18N-019`
**Related:** RFC-0023, RFC-0052, RFC-0054, RFC-0055; D-050;
[ACCESSIBILITY_FEATURE_RESEARCH.md](../ACCESSIBILITY_FEATURE_RESEARCH.md)

## Summary

Define a versioned, machine-readable `AccessibilityContract` for every public component, variant,
dynamic state, package, and authoring surface so obligations, evidence, limitations, and waivers
are inspectable without implying whole-application conformance.

## Motivation and background

Hedron already treats accessibility as a release concern, but obligations are scattered across
docs, tests, and informal checklists. Phase 0.19 needs one shared contract schema so core, data,
charts, extras, Explorer, HDJ, and inference surfaces record the same fields and can be composed
without package-specific inventiveness.

## Proposed design

### Schema fields

Each contract records at least:

- native/ARIA semantics and role mappings;
- accessible name/description sources and label relationships;
- keyboard and focus behavior (including restoration after HTMX swaps);
- pointer/touch/drag alternatives and target/reflow assumptions;
- announcements and live-region expectations;
- visual/motion/media/data alternatives and fallbacks;
- standard mappings (WCAG/ARIA criteria references);
- manual checks that automation cannot close;
- support evidence pointers and known limitations;
- waivers (owner, rationale, affected users, expiry, remediation).

### Composition rules

- Composition may add unmet obligations; a parent never inherits “conforms” from leaves.
- Leaf contracts never imply whole-application conformance.
- Third-party/plugin contracts are reported as boundaries, not transitive guarantees.
- Dynamic states (busy, error, open, selected, virtualized rows, streaming) are first-class
  contract entries, not footnotes.

### Catalog coverage (`CONTRACT-019`)

Every public built-in, optional first-party component, authoring surface, example, and template on
the 0.19 train has a reviewed contract. Missing contracts block Verified cut.

### Related conformance packets

- **`INTERACT-019`** — WCAG 2.2 interaction cases (focus not obscured, target size/spacing,
  pointer cancellation, label-in-name, drag alternatives, consistent help, redundant entry,
  timeouts, accessible authentication).
- **`MEDIA-019`** — captions, transcripts, audio description, player controls, chart/map/table
  alternatives, non-spatial views.
- **`COG-019`** — cognitive/personalization helpers (labels, help/glossary, progress, undo,
  motion/intensity controls); never auto-judge prose clarity.
- **`I18N-019`** — language/direction/structure validation; RTL/translated variants share reflow,
  focus, target, and AT evidence requirements.

## Alternatives considered

1. **Per-package checklists only.** Rejected — diverges semantics and blocks Explorer/CLI reuse.
2. **Automated scan results as the contract.** Rejected — scans cannot encode author intent,
   fallbacks, or waivers; empty scans must not summarize as “accessible.”
3. **ARIA-first markup generation.** Rejected — native HTML remains first choice (RFC-0023).

## Security implications

Contracts must not embed secrets. Waivers and known-limitation text are reviewable public or
security-sensitive records under release policy; they must not weaken CSRF, CSP, or TrustedHtml
boundaries.

## Accessibility implications

This RFC *is* the accessibility metadata substrate. Contracts drive diagnostics, Explorer panels,
and statement inventory fields without claiming application certification.

## Performance implications

Contract catalogs must be loadable for CLI/Explorer without unbounded I/O. Large media/chart
fallback assets remain subject to existing payload budgets.

## Testing strategy

- Schema unit tests and snapshot fixtures for representative components across packages.
- Catalog completeness gate (`CONTRACT-019`) fails on missing/unowned/expired waiver entries.
- Interaction/media/cognitive/i18n suites attach to the same contract IDs.

## Compatibility and migration

Additive on the Beta train. Existing informal a11y notes migrate into contracts; absence of a
contract is a 0.19 release blocker for public surfaces, not a silent default.

## Open questions

- Exact serialization format (Python models vs sidecar YAML/JSON) for docs generators.
- Whether HDJ authoring surfaces store contracts in prologue metadata or companion files.

## Acceptance criteria

- Public schema and composition rules documented and typed.
- Catalog covers every public 0.19 surface with reviewed contracts (`CONTRACT-019`).
- Related gates `INTERACT-019`, `MEDIA-019`, `COG-019`, and `I18N-019` reference contract IDs.
- No leaf contract implies application WCAG conformance.
