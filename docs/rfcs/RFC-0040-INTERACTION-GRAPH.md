# RFC-0040: Dashboard interaction graph and TriggerContext

**Status:** Accepted
**Phase:** 0.17 (`v0.17.0`)
**Stability:** `beta` (API); Explorer graph overlays may ship `experimental` until replay evidence lands
**Evidence:** `GRAPH-017`, `XFILTER-017`, `REPLAY-017`
**Related:** [Plotly Dash feature cross-check](../PLOTLY_DASH_FEATURE_CROSSCHECK.md);
[NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md); RFC-0008, RFC-0009, RFC-0011,
RFC-0026, RFC-0032, RFC-0039; RFC-0041 (patches/collections)

## Summary

Define a finite, page-local `DashboardBinding` / `InteractionGraph` layer with typed
`TriggerContext`, a unified dashboard action lifecycle, Explorer diagnostics, and an
interaction-graph recorder/replay harness. Edges remain explicit typed actions over declared
regions — not an application-wide callback runtime or implicit remote API.

## Motivation and background

Dash and NiceGUI demonstrate cohesive cross-filter dashboards and binding ergonomics. Hedron
already has actions, fragments, chart/grid events (0.12), and live transports (0.10). What is
missing is a deterministic, inspectable composition layer that fails closed on cycles, ambiguous
writers, unauthorized targets, and stale results without adopting a React callback DAG or Vue
outbox.

## Proposed design

### DashboardBinding / InteractionGraph

- Page-local registration of trigger inputs, snapshot-only state, one or more target regions,
  initialization policy, and chained derived bindings.
- Registration checks: missing dependency, cycle, duplicate writer, authorization, payload bounds,
  and deterministic order. Failures raise diagnostics (`HED-*`) and refuse registration.
- Each edge is an explicit typed action (or composition of declared actions). No hidden whole-app
  rerun.

### TriggerContext

Typed context for a firing edge: binding identity, event source, component/collection identity,
changed fields, correlation ID, request/session correlation, and declared input snapshots.
Sensitive or large state remains server-owned; snapshots are allowlisted.

### Lifecycle envelope

Unified dashboard-facing states: changed inputs, no-change (all or selected targets), running,
disabled, progress, cancellation, errors, redirects/history, debounce/coalescing, stale-result
rejection, and final updates. Side effects, cache policy, and authorization remain owned by the
underlying action. Supported production updates prefer HTTP/HTMX fragments and polling; SSE/WS
remain experimental fallbacks per D-044.

### Cross-filter composition

Compose 0.12 chart/grid events, form controls, URL/session/`BrowserStorage`, data-source
transforms, jobs, multi-region results, and throttled map viewport events (RFC-0033 → this RFC)
into multi-region results. Saved dashboard views are versioned and scoped.

### Explorer and recorder

- Explorer shows the interaction graph with trigger, target, timing, payload, cache, job,
  transport, and failure overlays.
- Recorder/replay captures declared trigger/action/patch exchanges with correlation IDs, redacted
  payload snapshots, and ordering metadata. Replays support stale-result, duplicate-event,
  disconnect, and patch-conflict schedules and assert final regions plus audit/trace output.
  Recordings are contract fixtures — never a way to replay privileged production traffic.

## Alternatives considered

1. **Dash-style global callback DAG.** Rejected — conflicts with explicit request/authz boundary.
2. **NiceGUI element binding / refreshable.** Rejected — deliberate non-parity; inspectable edges only.
3. **Compose only with ad-hoc actions (no graph layer).** Rejected — loses cycle/writer diagnostics
   and Explorer/replay evidence required by the 0.17 exit gate.

## Security implications

Every edge rechecks server authorization. Browser identity, client hints, and UI option filtering
are not authorization. Recorder fixtures must redact secrets and never capture production credentials.
Stale and unauthorized targets fail closed.

## Accessibility implications

Cross-filter and graph-driven updates must preserve focus, announce busy/error states, support
keyboard/table alternatives for chart selections, honor reduced-motion, and keep no-JavaScript
full-fragment HTTP paths functional.

## Performance implications

Debounce/coalesce, payload caps, and Explorer timing panels are mandatory. Replay suites must not
depend on timing-sensitive sleeps. Multi-worker tests prove browser state cannot bypass authz.

## Testing strategy

Unit registration diagnostics; integration lifecycle; browser matrix for cross-filter/focus/
reconnect/patch conflict; recorder fixtures under `REPLAY-017`; adversarial oversized/stale/
unauthorized schedules. Gate commands under `GRAPH-017`, `XFILTER-017`, `REPLAY-017`.

## Compatibility and migration

Additive APIs. Existing fragment actions remain valid without registering a graph. Dash/NiceGUI
migration inventories map callbacks/bindings → `DashboardBinding` without claiming automatic
conversion (`MIGRATE-017`).

## Open questions

None blocking Acceptance. Implementation may defer Explorer overlay polish behind `experimental`
labeling until `REPLAY-017` is Verified.

## Acceptance criteria

- Graphs are finite, deterministic, inspectable, and race-tested; cycles and ambiguous writers fail
  registration.
- Ordinary full-fragment HTTP interactions remain functional without JavaScript.
- Reference analytical app demonstrates chart/grid cross-filtering with cancellable background work.
- Recorder replays deterministically across supported browsers and workers.
