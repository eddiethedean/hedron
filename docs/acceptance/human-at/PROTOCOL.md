# Human assistive-technology evaluation protocol (0.21)

**Phase:** 0.21 · **Decision:** D-052 · **RFC baseline:** RFC-0055 (amended)
**Gates:** `PROTOCOL-021`, `SR-021`, `PARTICIPANT-021`, `ARTIFACT-021`, `REMEDIATE-021`
**Companion:** [PRIVACY.md](PRIVACY.md) · [task-scripts.md](task-scripts.md) ·
[ledger.schema.json](ledger.schema.json)

This protocol defines how Hedron runs **human** screen-reader and compensated
disabled-participant evaluation for the reference application. It complements automated
`AT-019` Playwright/axe evidence; it does **not** replace it and never authorizes automatic
WCAG, legal, certification, or VPAT/ACR claims.

## Goals

1. Complete the Verified AT minimum matrix (`SR-021`).
2. Complete the compensated participant floor (`PARTICIPANT-021`).
3. Land redacted public ledger rows and update the reference-app inventory/statement
   (`ARTIFACT-021`).
4. Remediate blockers or record owned waivers with expiry (`REMEDIATE-021`).

## Verified AT minimum (`SR-021`)

| Combo id | AT | Browser | OS |
|---|---|---|---|
| `vo-safari-macos` | VoiceOver | Safari | macOS |
| `nvda-firefox-windows` | NVDA | Firefox | Windows |
| `talkback-chromium-android` | TalkBack | Chromium | Android |

Each combo must exercise the [task corpus](task-scripts.md) at least once. Record one redacted
ledger row per (combo × task) or a consolidated row that lists completed `task_id`s — schema
allows either via `task_id` / `task_ids`.

**Out of Verified minimum (optional stretch):** JAWS; iOS VoiceOver; NVDA + Chromium second
pass; voice-input or switch-control lab. Stretch results may appear only as known limitations
or optional ledger rows with `"stretch": true`; they are not gate blockers.

Passing one screen reader is **not** generalized to all users or disability groups.

## Participant floor (`PARTICIPANT-021`)

- At least **two** compensated sessions.
- At least **one** participant who primarily uses a screen reader.
- At least **one** participant in another disability category: motor, low-vision, or cognitive.
- Sessions use the same [task corpus](task-scripts.md) against `examples/reference-app`.
- Compensation is arranged before the session; amount and method are recorded only in the
  **private** store (never in git). Public ledger rows use opaque `session_id` values
  (`sess-001`, …).

## Recruitment and consent

1. Recruit adults who match the participant floor; disclose that the product under test is
   open-source framework UI (reference app), not a production customer system.
2. Obtain informed consent covering: purpose, tasks, recording policy (audio/screen if any),
   voluntary withdrawal, compensation, data retention, and how findings are published
   (redacted).
3. Store consent artifacts **only** in the private store ([PRIVACY.md](PRIVACY.md)).
4. Offer accommodations (extra time, alternate input, breaks, preferred AT version when
   feasible).

## Session procedure

1. Confirm environment: OS / browser / AT versions; start reference app locally (or Codespaces)
   with documented demo credentials.
2. Brief the participant; do not coach announcement expectations mid-task.
3. Run tasks from [task-scripts.md](task-scripts.md); note blockers, workarounds, and
   unexpected silence or focus traps.
4. Debrief: what blocked completion, what was confusing, preferred alternatives.
5. Immediately draft a **redacted** ledger row (no names, emails, voice, or video).
6. Map findings to severity (below) and file issues or waivers.

## Severity → remediation / waiver

| Severity | Meaning | Required action before Verified cut |
|---|---|---|
| Blocker | Prevents completing a Verified task with the target AT, or traps focus/keyboard with no exit | Fix before cut, **or** owned `Waiver` with expiry + remediation + affected users |
| Major | Significant confusion or missing name/state that forces a non-obvious workaround | Fix preferred; waiver allowed with owner/expiry |
| Minor | Announcement polish, order quirks, non-blocking verbosity | Track; may ship as known limitation |
| Note | Observation without functional impact | Optional known limitation |

Empty human-AT evidence, missing ledger rows, or “no findings because we skipped SR” **never**
summarize as accessible.

## Retest policy

- After a Blocker fix, retest the affected (combo × task) before flipping `REMEDIATE-021`.
- Waivers expire; expired/unowned waivers fail governance (`HED-A11Y-0010`).
- Stretch AT need not be retested for Verified cut.

## Public artifacts after sessions

1. Append redacted rows validating against [ledger.schema.json](ledger.schema.json).
2. Update `examples/reference-app/accessibility_statement.py` inventory/statement fields
   (tested environments, assessment approach, known limitations, feedback route).
3. Export only with human `approved_by` (`AccessibilityStatement.export()`).
4. Keep raw notes private.

## Packet refine vs execution

This repository may ship the protocol, schema, and example **placeholder** ledger row while
gates remain `Planned`. Flipping `SR-021` / `PARTICIPANT-021` / `ARTIFACT-021` /
`REMEDIATE-021` to `Verified` requires real session evidence under this protocol.
