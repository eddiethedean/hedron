# Hedron `v0.21` human assistive-technology acceptance

Phase 0.21 delivers the human AT **engineering train** (protocol packet, PE corpus, fragment
parity) and indexes compensated screen-reader / participant evaluation against
`examples/reference-app`. Automated `AT-019` Playwright/axe evidence remains complementary —
not a substitute — and Hedron never emits automatic WCAG/legal/certification/VPAT claims.
Evidence is indexed by [`release-gate-0.21.toml`](release-gate-0.21.toml).

Owning decision: [D-052](../DECISIONS.md). RFC baseline:
[RFC-0055](../rfcs/RFC-0055-A11Y-GOVERNANCE.md) (amended).
Protocol packet: [`human-at/`](human-at/).

## Engineering release vs Verified human-AT cut

| Track | Meaning |
|---|---|
| **Published `v0.21.0` train** | Package metadata / adopter pins `>=0.21.0,<0.22`; engineering gates + docs honesty |
| **Verified human AT** | `SR-021` / `PARTICIPANT-021` / `ARTIFACT-021` / `REMEDIATE-021` flipped after real sessions |

**Do not market human AT as Supported** until the Verified human-AT cut. Use
`python scripts/check_human_at_packet.py --require-sessions` only when flipping those gates.
`PROTOCOL-021` stays Verified without session evidence.

## Spec packet

- [x] ROADMAP §0.21 scope accepted; D-052 recorded.
- [x] RFC-0055 human-AT section amended; open questions closed.
- [x] Entry gate: 0.19 / 0.20 Published; protocol under `docs/acceptance/human-at/`.
- [x] Gate checker recognizes `0.21`
  (`python scripts/check_release_gate.py 0.21.0 --allow-planned`).
- [x] Reference-app PE create/edit/delete, edit pages, DataEditor Escape, facilitator task-scripts.
- [x] `scripts/verify_pkg_21.py` + CI evidence wiring (packet + `0.21.0 --allow-planned`).
- [x] Adopter docs / SSOT claim Published `v0.21.0` with honest AT gap.
- [x] `REGRESS-021` / `PKG-021` Verified for engineering publish.
- [ ] Human AT sessions executed; SR/PARTICIPANT/ARTIFACT/REMEDIATE flipped Planned → Verified.

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

- [x] `verify_pkg_21.py` available for local packet evidence. *(`PKG-021` — Verified)*

## Exit

- [x] Full regression suite. *(`REGRESS-021` — Verified)*

**Engineering Published train is `v0.21.0`** (PROTOCOL / REGRESS / PKG Verified). Verified
human-AT exit remains outstanding (sessions + SR/PARTICIPANT/ARTIFACT/REMEDIATE). Tagging
uses `check_release_gate.py 0.21.0 --allow-planned` until session gates close.
