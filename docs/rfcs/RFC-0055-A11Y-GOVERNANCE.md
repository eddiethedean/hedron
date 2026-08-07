# RFC-0055: Accessibility evidence governance and AT matrix

**Status:** Accepted
**Phase:** 0.19 (`v0.19.0`)
**Stability:** `beta` (process/artifacts); statement content is human-approved
**Evidence:** `AT-019`, `GOVERN-019`, `PROFILE-019`
**Related:** RFC-0023, RFC-0051, RFC-0052; D-050;
[ACCESSIBILITY_FEATURE_RESEARCH.md](../ACCESSIBILITY_FEATURE_RESEARCH.md);
[WCAG-EM](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/)

## Summary

Define automated browser accessibility evidence (`AT-019`), evidence inventory,
accessibility-statement template, and waiver governance so releases can publish honest, scoped
claims without automatic WCAG/legal/certification/VPAT output. Human screen-reader and compensated
disabled-participant evaluation is Deferred to 0.21 (D-050).

## Motivation and background

Automation and semantic-tree suites are necessary release evidence. Hedron needs a governed place
for AT automation artifacts, known limitations, third-party boundaries, and human-approved
statement data. Compensated user evaluation remains valuable but is not a `v0.19.0` blocker.

## Proposed design

### Standards profile pointer (`PROFILE-019`)

This RFC consumes the normative baseline and draft/experimental policy from RFC-0023. Evidence
records must include pinned ACT/engine/browser versions used by automation.

### Automated AT matrix (`AT-019`)

Normative for Verified cut (D-050):

- Chromium, Firefox, and WebKit Playwright paths;
- keyboard-only operation;
- browser zoom;
- reduced motion;
- forced colors / high-contrast where automatable;
- pinned axe/ACT-aligned scans after representative dynamic states;
- representative surfaces: forms, data editor smoke, media, authentication/recovery smoke,
  dashboard, inference workflow stubs.

Each record includes versions, settings, representative task, result, known issue, owner, and
retest date. Empty or missing axe installs never summarize as "accessible."

### Deferred human AT (→ 0.21)

VoiceOver/Safari, NVDA, TalkBack, voice/switch lab sessions, and compensated disabled-participant
evaluation remain in scope for a later owned packet. They complement rather than substitute for
WCAG-oriented automation and do not block `AT-019` Verified for `v0.19.0`.

### Governance outputs (`GOVERN-019`)

- Rule/version inventory, test and automation results.
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

1. **Require compensated user testing for `v0.19.0`.** Rejected for this cut (D-050 automation
   proxy); retained as Deferred → 0.21.
2. **Auto-generate VPAT/ACR from contracts.** Rejected — deliberate non-goal.
3. **Skip AT automation entirely.** Rejected — `AT-019` remains a Verified gate via Playwright/axe.

## Security implications

Evidence artifacts may contain privacy-sensitive notes when human AT arrives in 0.21; store/redact
per release policy. Feedback routes must not expose secrets. Waivers are auditable records.

## Accessibility implications

Statement and inventory content must themselves be publishable in an accessible format. Automation
tasks should exercise real user goals, not only component demos.

## Performance implications

Automated AT evidence runs under `HEDRON_BROWSER=1` / browser CI job. Inventory generation should
be reproducible from contracts + retained artifacts.

## Testing strategy

- Schema validation for matrix rows and waiver records.
- Gate checker treats missing required AT automation rows / expired waivers as incomplete evidence.
- Reference-app statement export dry-run in docs/acceptance artifacts.

## Compatibility and migration

New acceptance artifacts under `docs/acceptance/` and evidence bundles. No breaking runtime API
required for governance templates alone.

## Open questions

- Exact storage location for 0.21 compensated-participant protocols and PII minimization.
- Whether statement template ships as a CLI export, docs page, or both.

## Acceptance criteria

- Published automated AT matrix completes representative tasks with versions and known limitations
  (`AT-019`).
- Evidence inventory + human-approved statement template with feedback route (`GOVERN-019`).
- Profile pins and claim boundaries enforced (`PROFILE-019`); no auto WCAG/legal/VPAT emission.
- Human AT Deferred destination documented (0.21).
