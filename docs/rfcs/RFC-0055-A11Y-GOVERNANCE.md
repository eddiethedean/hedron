# RFC-0055: Accessibility evidence governance and AT matrix

**Status:** Accepted
**Phase:** 0.19 (`v0.19.0`); human AT owned by 0.21 (`v0.21.0`, D-052)
**Stability:** `beta` (process/artifacts); statement content is human-approved
**Evidence:** `AT-019`, `GOVERN-019`, `PROFILE-019`; human AT gates `PROTOCOL-021` /
`SR-021` / `PARTICIPANT-021` / `ARTIFACT-021` / `REMEDIATE-021`
**Related:** RFC-0023, RFC-0051, RFC-0052; D-050, D-052;
[ACCESSIBILITY_FEATURE_RESEARCH.md](../ACCESSIBILITY_FEATURE_RESEARCH.md);
[human-at protocol](../acceptance/human-at/PROTOCOL.md);
[WCAG-EM](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/)

## Summary

Define automated browser accessibility evidence (`AT-019`), evidence inventory,
accessibility-statement template, and waiver governance so releases can publish honest, scoped
claims without automatic WCAG/legal/certification/VPAT output. Human screen-reader and compensated
disabled-participant evaluation is owned by phase **0.21** (D-052), complementing rather than
replacing `AT-019`.

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

### Human AT (→ 0.21 / D-052)

VoiceOver/Safari, NVDA, TalkBack, and compensated disabled-participant evaluation are owned by
phase **0.21**. They complement rather than substitute for WCAG-oriented automation and do not
block `AT-019` Verified for `v0.19.0`.

**Verified AT minimum** (`SR-021`):

- VoiceOver + Safari on macOS;
- NVDA + Firefox on Windows;
- TalkBack + Chromium on Android.

JAWS, iOS VoiceOver, NVDA+Chromium second pass, and voice/switch lab sessions are optional stretch
evidence (not Verified gate rows). Passing one screen reader is not generalized to all users.

**Participant floor** (`PARTICIPANT-021`): ≥2 compensated sessions with ≥1 screen-reader user and
≥1 other disability category (motor, low-vision, or cognitive). Task corpus:
`examples/reference-app` critical flows (see
[task-scripts.md](../acceptance/human-at/task-scripts.md)).

**Artifacts** (`PROTOCOL-021`, `ARTIFACT-021`, `REMEDIATE-021`):

- Written protocol under [`docs/acceptance/human-at/`](../acceptance/human-at/)
  (`PROTOCOL.md`, `PRIVACY.md`, ledger schema, redacted example row).
- Redacted public ledger rows may enter git; raw consent notes and participant identifiers never
  do (private store outside the repository).
- Blocker findings remediate or receive an owned `Waiver` with expiry; empty or missing human AT
  never summarizes as "accessible."
- Reference-app `EvidenceInventory` / human-approved `AccessibilityStatement` update after
  sessions; no CLI-required statement path beyond existing Python export.

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
Human AT severity → waiver/fix path is documented in
[PROTOCOL.md](../acceptance/human-at/PROTOCOL.md).

## Alternatives considered

1. **Require compensated user testing for `v0.19.0`.** Rejected for this cut (D-050 automation
   proxy); retained as owned destination → 0.21 (D-052).
2. **Auto-generate VPAT/ACR from contracts.** Rejected — deliberate non-goal.
3. **Skip AT automation entirely.** Rejected — `AT-019` remains a Verified gate via Playwright/axe.
4. **Require JAWS / iOS VoiceOver / voice-switch for Verified `v0.21.0`.** Rejected — keeps the
   cut cuttable; stretch evidence may still be recorded as known limitations.

## Security implications

Evidence artifacts may contain privacy-sensitive notes; store/redact per
[PRIVACY.md](../acceptance/human-at/PRIVACY.md). Feedback routes must not expose secrets.
Waivers are auditable records.

## Accessibility implications

Statement and inventory content must themselves be publishable in an accessible format. Automation
and human AT tasks should exercise real user goals, not only component demos.

## Performance implications

Automated AT evidence runs under `HEDRON_BROWSER=1` / browser CI job. Inventory generation should
be reproducible from contracts + retained artifacts. Human AT sessions are offline evidence and
do not run in CI.

## Testing strategy

- Schema validation for matrix rows and waiver records.
- Gate checker treats missing required AT automation rows / expired waivers as incomplete evidence.
- Reference-app statement export dry-run in docs/acceptance artifacts.
- `scripts/check_human_at_packet.py` validates protocol files, ledger schema, and redacted example
  row for `PROTOCOL-021` / `ARTIFACT-021` while Planned.

## Compatibility and migration

New acceptance artifacts under `docs/acceptance/` and evidence bundles. No breaking runtime API
required for governance templates alone. Optional typed `HumanAtRecord` helpers may ship on the
0.21 train without changing claim boundaries.

## Resolved questions (was Open questions)

- **Storage / PII:** Protocol and redacted ledger templates live under
  `docs/acceptance/human-at/`. Raw session notes, consent forms, and participant identifiers stay
  in a private store outside git (see [PRIVACY.md](../acceptance/human-at/PRIVACY.md)).
- **Statement export:** Continues as human-approved `AccessibilityStatement.export()` (reference
  app dry-run and docs). No separate CLI export is required for Verified 0.21; docs may embed
  published statement fields after approval.

## Acceptance criteria

- Published automated AT matrix completes representative tasks with versions and known limitations
  (`AT-019`).
- Evidence inventory + human-approved statement template with feedback route (`GOVERN-019`).
- Profile pins and claim boundaries enforced (`PROFILE-019`); no auto WCAG/legal/VPAT emission.
- Human AT owned by 0.21 with D-052 gate IDs, protocol packet, and zero-Deferred cut policy.
