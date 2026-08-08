# Hedron `v0.21` human assistive-technology acceptance

Phase 0.21 delivers compensated disabled-participant evaluation and the Verified
screen-reader matrix (VoiceOver/Safari macOS, NVDA/Firefox Windows, TalkBack/Chromium
Android) against `examples/reference-app` critical flows — complementing automated
`AT-019` Playwright/axe evidence without substituting for it or emitting automatic
WCAG/legal/certification/VPAT claims.
Evidence is indexed by [`release-gate-0.21.toml`](release-gate-0.21.toml).
**Zero Deferred:** every 0.21-owned gate row must be Verified at cut.

Owning decision: [D-052](../DECISIONS.md). RFC baseline:
[RFC-0055](../rfcs/RFC-0055-A11Y-GOVERNANCE.md) (amended).
Protocol packet: [`human-at/`](human-at/).

**Engineering-complete ≠ Published / Supported.** Prep may land on `main` while the living
train remains **0.20**. Do not market human AT as Supported until every 0.21 gate row is
Verified and `v0.21.0` is Published. Use
`python scripts/check_human_at_packet.py --require-sessions` only at the Verified cut.

## Spec packet

- [x] ROADMAP §0.21 scope accepted; D-052 recorded.
- [x] RFC-0055 human-AT section amended; open questions closed.
- [x] Entry gate: 0.19 / 0.20 Published; protocol under `docs/acceptance/human-at/`.
- [x] Gate checker recognizes `0.21`
  (`python scripts/check_release_gate.py 0.21.0 --allow-planned`).
- [x] Reference-app PE create/edit, edit pages, DataEditor Escape, facilitator task-scripts.
- [x] `scripts/verify_pkg_21.py` + CI evidence wiring (packet + `0.21.0 --allow-planned`).
- [ ] Human AT sessions executed; remaining gates flipped Planned → Verified.

## Protocol and privacy

- [x] Written protocol (consent, compensation, privacy, severity, retest). *(`PROTOCOL-021` —
  Verified)*
- [x] Packet checker + redacted ledger schema/example present.

## Screen-reader matrix

- [ ] VoiceOver + Safari (macOS) task corpus. *(`SR-021` — Planned)*
- [ ] NVDA + Firefox (Windows) task corpus. *(`SR-021` — Planned)*
- [ ] TalkBack + Chromium (Android) task corpus. *(`SR-021` — Planned)*

## Compensated participants

- [ ] ≥2 compensated sessions; ≥1 screen-reader + ≥1 other category. *(`PARTICIPANT-021` —
  Planned)*

## Artifacts and remediation

- [ ] Redacted ledger rows validate; inventory/statement updated. *(`ARTIFACT-021` — Planned)*
- [ ] Blockers fixed or owned Waiver with expiry. *(`REMEDIATE-021` — Planned)*

## Packaging

- [x] `verify_pkg_21.py` available for local packet evidence. *(`PKG-021` command retargeted;
  gate remains Planned until cut)*

## Exit

- [ ] Full regression suite. *(`REGRESS-021` — Planned)*

**Exit not met for Published `v0.21.0`.** Engineering prep is complete; sessions and Verified
flip remain outstanding.
