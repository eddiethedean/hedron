# Human AT privacy and storage (0.21)

**Decision:** D-052 · **Gate:** `PROTOCOL-021` / `ARTIFACT-021`

## What may live in git

| Artifact | Path / form | Contents |
|---|---|---|
| Protocol | [`PROTOCOL.md`](PROTOCOL.md) | Process only |
| Task scripts | [`task-scripts.md`](task-scripts.md) | Steps and expected operations |
| Ledger schema | [`ledger.schema.json`](ledger.schema.json) | JSON Schema |
| Redacted ledger rows | `ledger/*.json` (when sessions land) or example row | Opaque ids, versions, task results, issue links — **no PII** |
| Inventory / statement | Reference-app Python + published docs excerpts | Scoped claims, known limitations, feedback route |

## What must never enter git

- Participant legal names, emails, phone numbers, addresses, photos
- Signed consent forms or raw survey responses identifying a person
- Unredacted audio, video, or screen recordings
- Compensation amounts tied to a named person
- Free-text notes that include identifying details

Store those materials in a **private** maintainer store (encrypted drive, access-controlled
folder, or org-private vault) with access limited to evaluation owners. Retention: delete raw
recordings within 90 days unless a longer hold is required for an open remediation and
re-consent is obtained.

## Redaction rules for public ledger rows

- Use opaque `session_id` values (`sess-001`, …), never initials that map 1:1 to a known person
  in public channels.
- Prefer disability **category** labels (`screen_reader`, `motor`, `low_vision`, `cognitive`)
  over clinical diagnoses.
- Quote AT announcements only when needed to reproduce a bug; strip any accidental PII.
- Link public GitHub issues for remediations; do not paste private ticket systems that embed PII.

## Feedback routes

Public feedback (issues, security@, a11y contact) must not require participants to disclose
disability status. Do not publish participant contact information in statements.
