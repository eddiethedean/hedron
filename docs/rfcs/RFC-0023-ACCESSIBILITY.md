# RFC-0023: Accessibility

**Status:** Accepted (umbrella; 0.19 packet expands via RFCs 0051–0055)
**Phase:** 0.1–0.8 baseline; comprehensive engineering in 0.19 (`v0.19.0`)
**Stability:** `beta` (framework contracts); application conformance claims remain human-owned
**Evidence:** `PROFILE-019` (umbrella); see RFCs 0051–0055 for packet gates
**Related:** [ACCESSIBILITY_FEATURE_RESEARCH.md](../ACCESSIBILITY_FEATURE_RESEARCH.md);
RFC-0051–RFC-0055; D-050; [RELEASE_0_19.md](../acceptance/RELEASE_0_19.md)

## Commitment

Accessibility is a component contract and release requirement, not a documentation suggestion.
Built-in components target WCAG 2.2 AA where applicable and use native elements before ARIA.
Phase 0.19 makes obligations, authoring assistance, dynamic evidence, assistive-technology
support, and known limitations inspectable and release-governed without claiming that automation
or framework markup can certify an arbitrary application.

## Normative baseline (`PROFILE-019`)

| Layer | Stable baseline | Notes |
|---|---|---|
| Web content | WCAG 2.2 Level A and AA | Understanding docs inform tests; APG is informative only |
| Semantics | HTML + WAI-ARIA 1.2 | Accessible Name and Description Computation 1.2 |
| Authoring tools | ATAG 2.0 (applicable parts) | Full ATAG claim needs a separate applicability report |
| Conformance testing | ACT rules + pinned engines | Versions recorded in evidence inventory |
| Drafts | WAI-ARIA 1.3, WCAG 3, other drafts | Labeled experimental until an accepted baseline revision |

Release gates and support claims must pin ACT/engine/browser/AT versions. Draft features may inform
experiments but cannot silently change a Verified gate or Supported claim.

## Claim boundaries (non-goals)

Hedron must not automatically emit:

- a WCAG conformance statement for an arbitrary application;
- legal-compliance, certification, ACR, or VPAT claims;
- “accessible” summaries from empty or incomplete automated scans.

Leaf `AccessibilityContract`s never imply whole-application conformance. Composition can add unmet
obligations. Third-party plugins publish their own contracts; Hedron reports the boundary.

## Requirements

- Interactive components have accessible names, keyboard operation, visible focus, states,
  relationships, and error announcements.
- Forms generate labels, instructions, required state, and error associations.
- Lazy regions expose busy, fallback, error, and retry states.
- DataEditor supports keyboard navigation and does not rely only on color.
- Charts require descriptions and appropriate static or tabular fallbacks.
- Themes support contrast, reduced motion, zoom, reflow, forced colors, and touch target needs.
- Progressive-enhancement paths for critical forms/mutations remain usable without HTMX/JS
  (`PE-019`; issue #8).

Compiler and Explorer diagnostics catch statically knowable problems but do not claim to prove
accessibility. Components may require an explicit waiver with rationale, owner, affected users,
expiry, and remediation for requirements that cannot be automated (`GOVERN-019`).

## 0.19 packet ownership

| Concern | RFC | Primary gates |
|---|---|---|
| `AccessibilityContract` schema and catalog | RFC-0051 | `CONTRACT-019`, `INTERACT-019`, `MEDIA-019`, `COG-019`, `I18N-019` |
| Explorer workspace + scenarios / ACT-axe | RFC-0052 | `EXPLORER-019`, `TEST-019` |
| Progressive enhancement, landmarks, Page scripts | RFC-0053 | `PE-019`, `LANDMARK-019`, `SCRIPT-019` |
| ATAG authoring assistance | RFC-0054 | `ATAG-019` |
| Evidence governance, AT matrix, statement template | RFC-0055 | `AT-019`, `GOVERN-019`, `PROFILE-019` |

`REGRESS-019` and `PKG-019` close the cut. Zero Deferred among 0.19-owned rows (D-050).

## Severity and waiver policy

- Release severity, regression policy, and waiver authority are defined with the evidence inventory
  (RFC-0055). Expired or unowned waivers block Verified cut.
- Snapshot regeneration alone cannot waive automatic or incomplete/manual findings.
- Issues [#8](https://github.com/eddiethedean/hedron/issues/8),
  [#27](https://github.com/eddiethedean/hedron/issues/27),
  [#31](https://github.com/eddiethedean/hedron/issues/31), and
  [#39](https://github.com/eddiethedean/hedron/issues/39) remain normative for PE/landmark/script
  acceptance criteria.

## Acceptance criteria

- Every built-in interactive component has a keyboard interaction specification.
- Automated semantic checks, browser axe/ACT-aligned tests, and manual scenarios are part of
  release gates (`TEST-019`, `AT-019`).
- Accessibility metadata is available to examples, Explorer, and documentation generators
  (`CONTRACT-019`, `EXPLORER-019`, `ATAG-019`).
- Public claim surfaces refuse automatic WCAG/legal/certification/VPAT emission (`GOVERN-019`).
