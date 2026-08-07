# RFC-0055: Accessibility evidence governance and AT matrix

**Status:** Draft
**Phase:** 0.19 (`v0.19.0`)
**Stability:** `beta` (process/artifacts); statement content is human-approved
**Evidence:** `AT-019`, `GOVERN-019`, `PROFILE-019`
**Related:** RFC-0023, RFC-0051, RFC-0052; D-050;
[ACCESSIBILITY_FEATURE_RESEARCH.md](../ACCESSIBILITY_FEATURE_RESEARCH.md);
[WCAG-EM](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/)

## Summary

Define the manual browser/assistive-technology evidence matrix, compensated disabled-participant
evaluation scope, evidence inventory, accessibility-statement template, and waiver governance so
releases can publish honest, scoped claims without automatic WCAG/legal/certification/VPAT output.

## Motivation and background

Automation and semantic-tree suites are necessary but insufficient. Hedron needs a governed place
for AT evidence, known limitations, third-party boundaries, and human-approved statement data.

## Proposed design

### Standards profile pointer (`PROFILE-019`)

This RFC consumes the normative baseline and draft/experimental policy from RFC-0023. Evidence
records must include pinned ACT/engine/browser/AT versions.

### Manual AT matrix (`AT-019`)

Scoped matrix including at least:

- VoiceOver/Safari on macOS and iOS;
- NVDA with Firefox and Chromium on Windows;
- TalkBack/Chromium on Android;
- keyboard-only;
- voice/switch-compatible label behavior;
- browser zoom;
- platform high contrast/forced colors;
- reduced motion;
- user text-spacing/style overrides.

Each record includes versions, settings, representative task, expected behavior/announcement,
result, known issue, owner, and retest date.

At least the data editor, media flow, authentication/recovery, live update, dashboard, and
inference workflow receive appropriately scoped evaluation with compensated disabled participants.
User testing complements rather than substitutes for WCAG evaluation.

### Governance outputs (`GOVERN-019`)

- Rule/version inventory, test and manual results.
- Known limitations and alternatives.
- Third-party boundaries and feedback route.
- Waiver owner/rationale/affected users/expiry/remediation; expired/unowned waivers block cut.
- Accessibility-statement template/export fields: standard, scope, contact/feedback, known
  limitations and alternatives, tested environments, assessment approach, and date.

Hedron never automatically emits a WCAG conformance, legal-compliance, certification, or ACR/VPAT
claim. A reference application publishes an evidence inventory and human-approved statement making
no broader claim than scoped evidence supports.

### Severity policy

Release policy defines blocker severity, affected-user impact, regression policy, waiver
authority and expiry, remediation ownership, and a public/security-sensitive reporting path.

## Alternatives considered

1. **Automation-only release gate.** Rejected — contradicts research and RFC-0023.
2. **Auto-generate VPAT/ACR from contracts.** Rejected — deliberate non-goal.
3. **Defer all AT matrix work past 0.19.** Rejected — structure-only refinement keeps full
   ambition in-phase (D-050).

## Security implications

Evidence artifacts may contain privacy-sensitive participant notes; store/redact per release
policy. Feedback routes must not expose secrets. Waivers are auditable records.

## Accessibility implications

Statement and inventory content must themselves be publishable in an accessible format. Matrix
tasks should exercise real user goals, not only component demos.

## Performance implications

Manual AT evidence is not a CI runtime cost; automation remains the blocking CI path where
applicable. Inventory generation should be reproducible from contracts + retained artifacts.

## Testing strategy

- Schema validation for matrix rows and waiver records.
- Gate checker treats missing required AT rows / expired waivers as incomplete evidence.
- Reference-app statement export dry-run in docs/acceptance artifacts.

## Compatibility and migration

New acceptance artifacts under `docs/acceptance/` and evidence bundles. No breaking runtime API
required for governance templates alone.

## Open questions

- Storage location for compensated-participant protocols and PII minimization.
- Whether statement template ships as a CLI export, docs page, or both.

## Acceptance criteria

- Published AT matrix completes representative tasks with versions and known limitations
  (`AT-019`).
- Evidence inventory + human-approved statement template with feedback route (`GOVERN-019`).
- Profile pins and claim boundaries enforced (`PROFILE-019`); no auto WCAG/legal/VPAT emission.
