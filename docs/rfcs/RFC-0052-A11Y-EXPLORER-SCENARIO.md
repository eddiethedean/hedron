# RFC-0052: Explorer accessibility workspace and AccessibilityScenario

**Status:** Draft
**Phase:** 0.19 (`v0.19.0`)
**Stability:** `beta` (API); Explorer UX remains development-oriented
**Evidence:** `EXPLORER-019`, `TEST-019`
**Related:** RFC-0007, RFC-0019, RFC-0021, RFC-0023, RFC-0051, RFC-0055; D-050

## Summary

Expand Component Explorer with a source-mapped accessibility review workspace and define testing
APIs for accessibility-tree snapshots, targeted assertions, and an `AccessibilityScenario`
vocabulary with pinned ACT/axe provenance (JSON/SARIF).

## Motivation and background

Authors need to see computed roles, names, focus order, live regions, and visual review modes
beside the rendered tree. Automated checks must run after meaningful dynamic states and retain
upstream rule versions so snapshot churn cannot silently waive findings.

## Proposed design

### Explorer workspace (`EXPLORER-019`)

- Rendered accessibility tree with computed role/name/description/value/state.
- Source mapping to component/props/HDJ origin.
- Outlines for headings, landmarks, reading order, tab order, and focus.
- Keyboard map and live-region event log.
- Review modes: contrast/non-text contrast, target spacing, focus obstruction, text spacing,
  zoom/reflow/orientation, reduced motion, forced colors, media alternatives, visualization
  fallbacks.
- Findings distinguish automatic, semi-automatic, and manual status.
- Empty or incomplete scans never summarize as “accessible.”

### Testing APIs (`TEST-019`)

- Accessibility-tree snapshots and targeted assertions.
- `AccessibilityScenario` vocabulary covering keyboard, focus, state/value, announcements,
  pointer/touch alternatives, timeouts, fragments/history, loading/success/error/disconnect, and
  supported open-shadow/same-origin-frame states.
- Pinned semantic/ARIA validation and axe/ACT-aligned scans after meaningful dynamic states.
- Stable JSON/SARIF provenance; snapshot changes require review rather than bulk acceptance.

## Alternatives considered

1. **Rely only on external axe CI without Explorer.** Rejected — authors need source-mapped
   interactive review during development.
2. **Treat zero axe findings as conformance.** Rejected — RFC-0023 claim boundaries forbid it.
3. **Browser-only manual review without scenarios.** Rejected — loses regression automation for
   semantic-tree and dynamic-state suites.

## Security implications

Explorer remains development-oriented with production opt-in controls (RFC-0007). Scans must not
exfiltrate secrets from rendered props. SARIF/JSON artifacts redact secrets like other diagnostics.

## Accessibility implications

The workspace itself must be keyboard operable, announce findings without relying on color alone,
and preserve focus when switching review modes.

## Performance implications

Scans run on demand or after declared scenario steps; full-catalog continuous scanning is not a
default production cost. Large trees may paginate or virtualize outlines with documented limits.

## Testing strategy

- Unit/integration coverage for scenario vocabulary and provenance schema.
- Three-engine browser automation for semantic-tree and dynamic-state suites (Chromium, Firefox,
  WebKit) as required by the 0.19 exit gate.
- Snapshot review policy tests reject bulk-accept paths.

## Compatibility and migration

Additive testing helpers under `hedron.testing` / Explorer. Existing a11y pytest markers remain;
scenarios become the preferred structured vocabulary for 0.19 evidence.

## Open questions

- Exact pin policy for axe-core / ACT rule packs per release train.
- How open-shadow and same-origin iframe states are declared in fixtures.

## Acceptance criteria

- Explorer workspace ships the tree, source map, outlines, keyboard map, live-region log, and
  review modes (`EXPLORER-019`).
- `AccessibilityScenario` + tree snapshots + ACT/axe provenance emit stable JSON/SARIF
  (`TEST-019`).
- Findings never claim “accessible” from empty scans; snapshot bulk-accept is blocked.
