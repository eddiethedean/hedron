# Observability implementation

## Default

Hedron emits structured events through standard-library logging and bounded in-process diagnostic
hooks. Optional exporters and tracing integrations are lazy extras; core and adapter imports do not
require a telemetry SDK.

## Event model

Events use stable route, component, cache, job, adapter, and capability identifiers. Timing stages
distinguish dependency/I/O, render, serialization, cache wait/load, browser abort, application
deadline, server cancellation, and completed-but-discarded work. Values are redacted before storage,
formatting, Explorer display, or export.

## Operations

Health, readiness, cache/job degradation, lifecycle, audit, and supply-chain events have bounded
payloads and retention. Explorer consumes sanitized views and is not required for production
visibility.

## Verification

Use adversarial secret corpora, failure storms, bounded-memory checks, schema snapshots, optional
dependency absence, and external cache/job degradation tests.
