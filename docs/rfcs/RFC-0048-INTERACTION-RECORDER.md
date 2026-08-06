# RFC-0048: Redacted interaction and API recorder

**Status:** Accepted
**Phase:** 0.18 (`v0.18.0`)
**Stability:** `beta` (API)
**Evidence:** `RECORD-018`
**Related:** [Gradio feature cross-check](../GRADIO_FEATURE_CROSSCHECK.md);
RFC-0016, RFC-0017, RFC-0040, RFC-0045; D-049

## Summary

Define an interaction/API recorder that emits redacted, reviewable Python and HTTP examples only
for explicitly public endpoints, including file fixtures and session assumptions. Generated
snippets never expand endpoint authority or record credentials and sensitive values.

## Motivation and background

Gradio’s View API page and client examples help developers call demos remotely. Hedron already
exposes FastAPI/OpenAPI. What is missing is a recorder that produces reviewable client snippets
with mandatory redaction and an explicit public-endpoint boundary — without capturing production
credentials or inventing privileged traffic replay.

## Proposed design

### Public-endpoint recorder

- Emit redacted Python and HTTP examples only for endpoints that are explicitly public (or
  explicitly selected under a reviewable export policy).
- Include file fixtures and session assumptions as declared placeholders, never as live secrets.
- Snippets document required authentication schemes without embedding tokens, cookies, or PII.
- A generated snippet never expands endpoint authority beyond the recorded public contract.

### Redaction and review

- Credentials, secrets, authorization headers, cookies, and configured sensitive fields are
  stripped or replaced with placeholders.
- Large or binary payloads become bounded fixtures with content-type and size metadata.
- Recordings are contract fixtures for docs and tests — not a way to replay privileged production
  traffic (consistent with RFC-0040 recorder posture).

### Integration

Thin FastAPI/OpenAPI-aware wiring in `hedron`; core contracts remain framework-neutral where
applicable. Explorer may surface recorded public calls with redaction overlays.

## Alternatives considered

1. **Record all traffic by default.** Rejected — credentials and sensitive values must never be
   captured casually.
2. **Claim Gradio client parity including privileged replay.** Rejected — public contracts and
   redaction only.
3. **Docs-only curl paste without tooling.** Rejected — loses deterministic `RECORD-018` evidence
   and redaction guarantees.

## Security implications

Recorder output must not contain credentials or sensitive values. Export policy is deny-by-default
for non-public endpoints. Fixtures used in CI are synthetic and bounded. Snippets never widen
authorization.

## Accessibility implications

Not applicable to recorder generation itself beyond ensuring documented examples remain usable
with ordinary HTTP clients. Any Explorer UI for recordings follows existing a11y contracts.

## Performance implications

Recording is opt-in and bounded. Fixture generation must not capture unbounded payloads or block
request paths in production by default.

## Testing strategy

Unit redaction and public-endpoint gating; adversarial credential/secret leakage; snippet authority
non-expansion. Gate command under `RECORD-018`.

## Compatibility and migration

Additive tooling. OpenAPI remains the protocol source of truth. Gradio client inventories map to
recorded public calls without automatic conversion (`MIGRATE-018`).

## Open questions

None blocking Acceptance. Optional remote Gradio provider recording belongs to RFC-0049 contract
tests rather than this recorder’s core claim.

## Acceptance criteria

- Recorder emits redacted Python/HTTP examples for explicitly public endpoints only.
- Credentials and sensitive values are never recorded.
- Generated snippets never expand endpoint authority.
- Gate evidence under `RECORD-018`.
