# RFC-0047: InferencePolicy over JobBackend

**Status:** Accepted
**Phase:** 0.18 (`v0.18.0`)
**Stability:** `beta` (API); in-process queue is development-only
**Evidence:** `INFER-018`, `SCENARIO-018`
**Related:** [Gradio feature cross-check](../GRADIO_FEATURE_CROSSCHECK.md);
RFC-0013, RFC-0020, RFC-0032, RFC-0045, RFC-0050; D-020, D-037, D-049

## Summary

Define an inference execution policy over existing `JobBackend` with admission control,
fair/priority queues, bounded queue-position and ETA semantics, named concurrency groups, batch
windows, generator streaming, and Explorer diagnostics. An in-process queue is development-only;
production durability is not owned by a single web process.

## Motivation and background

Gradio queuing, concurrency groups, batch functions, progress, and cancellation demonstrate useful
model-serving outcomes. Hedron already owns durable jobs, streams, and cancellation. What is
missing is model-aware admission, resource pools, batch isolation, and queue status over that
boundary — without treating an in-process web queue as the production promise.

## Proposed design

### InferencePolicy

Compose over `JobBackend`:

- admission control and fair/priority queues;
- bounded queue-position and ETA semantics;
- named model/resource/GPU concurrency groups that remain correct under multi-worker adapters;
- durable multi-worker backends (Redis/Celery/RQ and conformance targets);
- batch windows and compatible-shape grouping with per-item correlation and partial failure;
- generator/async-generator streaming, progress, cancellation, timeout, retry, overload, and
  artifact cleanup;
- Explorer timing and resource diagnostics hooks.

### Development-only in-process queue

An in-process queue may exist for local demos and unit tests. It is explicitly labeled
development-only and must not be the Supported production durability or fairness claim (D-049).

### ModelDemoScenario

A `ModelDemoScenario` kit layered on `AppScenario` supplies synthetic typed fixtures for versioned
examples, queue/admission outcomes, streamed progress, cancellation, feedback consent, and
redaction/retention assertions. It never loads a real model or treats generated output as
trustworthy test data by default (`SCENARIO-018`).

## Alternatives considered

1. **In-process queue as production durability.** Rejected — D-020 / D-049; durability stays on
   `JobBackend`.
2. **Fork a second job runtime for models.** Rejected — compose existing jobs and streams.
3. **Gradio-style queue correctness pinned to one web process.** Rejected — multi-worker evidence
   is mandatory for `INFER-018`.

## Security implications

Admission and concurrency groups never bypass action authorization. Artifact cleanup must not
leak paths across tenants. Overload and rejection paths return safe diagnostics without payload
leakage. Scenario fixtures never embed Hub credentials or unbounded artifacts.

## Accessibility implications

Queue position, ETA, progress, and cancellation must be announcable and keyboard-operable in demo
surfaces. No-JavaScript polling/fragment fallbacks remain functional for Supported production
observation paths.

## Performance implications

Batch isolation, capacity, fairness, and cleanup suites must not depend on timing-sensitive sleeps.
Explorer diagnostics expose timing/resource panels without requiring production payload capture.

## Testing strategy

Multi-worker fairness, capacity, batch isolation, queue rank/ETA, overload, generator failure,
disconnect/cancel, timeout, retry, resource exhaustion, cleanup, and durable-backend failure
(`INFER-018`). Scenario kit coverage without real models (`SCENARIO-018`).

## Compatibility and migration

Additive policy APIs over existing `JobBackend`. Existing jobs remain valid without inference
policy. Gradio queue/batch inventories map without claiming automatic conversion (`MIGRATE-018`).

## Open questions

None blocking Acceptance. Named GPU pool adapters may remain experimental until multi-worker
hardware evidence is available; portable concurrency-group contracts still ship.

## Acceptance criteria

- Inference scheduling passes the multi-worker and failure suites above without pinning correctness
  to one web process.
- In-process queues are development-only and documented as such.
- `ModelDemoScenario` covers HTTP and job contracts with synthetic fixtures only.
- Gate evidence under `INFER-018` and `SCENARIO-018`.
