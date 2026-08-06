# RFC-0046: Model-demo presentation and PredictionFeedback

**Status:** Accepted
**Phase:** 0.18 (`v0.18.0`)
**Stability:** `beta` (API)
**Evidence:** `EXAMPLE-018`, `PRESENT-018`, `FEEDBACK-018`
**Related:** [Gradio feature cross-check](../GRADIO_FEATURE_CROSSCHECK.md);
RFC-0010, RFC-0011, RFC-0012, RFC-0023, RFC-0045; D-049

## Summary

Define `ExampleSet` with provenance and cached results; demo-oriented `PredictionLabel`,
`ParameterViewer`, multi-speaker `Dialogue`, and media/artifact gallery composition; and
explicit-consent `PredictionFeedback` with pluggable sinks. Feedback is never silently enabled
or treated as ground truth.

## Motivation and background

Gradio examples, labels, parameter viewers, dialogue transcripts, galleries, and flagging deliver
useful ML-demo evaluation outcomes. Hedron needs the same outcomes with inspectable provenance,
secret/PII redaction, tenant isolation, retention/deletion, accessibility, and consent — without
silent capture or feedback-as-truth inference.

## Proposed design

### ExampleSet

- Versioned sample datasets with partial examples, labels, provenance, pagination, and
  authorization.
- Eager/lazy cached results keyed by action/model, schema, code, and preprocessing version.
- Generation cost, invalidation, storage, retention, and stale-result behavior are inspectable.
- Synthetic bounded fixtures only in CI; never load a real model by default.

### PredictionLabel / ParameterViewer / Dialogue / galleries

- `PredictionLabel`: ranked scores retain class identity and calibration/precision metadata; an
  accessible table representation is mandatory; color alone is not the sole encoding.
- `ParameterViewer`: schemas redact secrets; defaults, descriptions, anchors, and language-neutral
  examples are generated from typed contracts.
- `Dialogue`: multi-speaker transcripts with accessible speaker labels, diarization/timing
  metadata, and text export without relying on color alone.
- Media/artifact gallery composition reuses 0.15 gallery contracts with authorization, captions,
  selection, and list fallback.

### PredictionFeedback

- Explicit-consent collection for rating, label, reason, correction, and selected input/output
  references.
- Pluggable sinks with mandatory collection notice, tenant scope, redaction, retention and
  deletion, abuse controls, authorization, export, audit, and artifact policy.
- Feedback is not silently enabled and is never treated as ground truth for model evaluation
  contracts.

## Alternatives considered

1. **Silent default flagging / analytics capture.** Rejected — D-049; consent and notice are
   mandatory.
2. **Treat feedback as labeled ground truth.** Rejected — evaluation contracts must keep feedback
   provisional and inspectable.
3. **Global mutable example datasets.** Rejected — deliberate non-parity with Gradio mutable
   globals; examples remain versioned and authorized.

## Security implications

Secret/PII redaction in examples, parameters, dialogue, and feedback is mandatory. Tenant isolation
and retention/deletion must be enforceable. Malicious-file and oversized-artifact suites apply to
example and feedback attachments. Sinks never expand endpoint authority.

## Accessibility implications

Labels, dialogue, galleries, and feedback controls must preserve focus, keyboard alternatives,
non-color encodings, captions/descriptions where media is shown, and no-JavaScript fragment paths.
Busy/error announcements apply during example cache generation and feedback submit.

## Performance implications

Example cache invalidation and cost controls are inspectable. Stale-cache behavior must not pin
correctness to timing sleeps. Gallery and dialogue payloads honor size budgets.

## Testing strategy

Unit provenance/invalidation (`EXAMPLE-018`); presentation a11y and redaction (`PRESENT-018`);
consent/retention/tenant/sink policy (`FEEDBACK-018`); adversarial secret leakage and malicious
files. Synthetic fixtures only.

## Compatibility and migration

Additive builtins and contracts. Existing gallery/chat/form components remain valid. Gradio
Examples/Flagging inventories map without automatic conversion (`MIGRATE-018`).

## Open questions

None blocking Acceptance. Optional Hugging Face dataset nodes remain vendor adapters over portable
example/workflow contracts (RFC-0049 / RFC-0050).

## Acceptance criteria

- Examples, cached results, labels, parameters, dialogue, galleries, and feedback pass
  accessibility, consent, provenance, secret/PII redaction, tenant isolation, retention/deletion,
  malicious-file, stale-cache, and cost-control suites.
- Feedback is never silent and never ground truth.
- Gate evidence under `EXAMPLE-018`, `PRESENT-018`, and `FEEDBACK-018`.
