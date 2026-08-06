# RFC-0045: InferenceInterface and ModelDemo

**Status:** Accepted
**Phase:** 0.18 (`v0.18.0`)
**Stability:** `beta` (API)
**Evidence:** `DEMO-018`
**Related:** [Gradio feature cross-check](../GRADIO_FEATURE_CROSSCHECK.md);
RFC-0008, RFC-0012, RFC-0013, RFC-0026, RFC-0040, RFC-0047; D-049

## Summary

Define an `InferenceInterface` / `ModelDemo` composition layer that builds a reviewable
input/result demo surface only from an explicitly registered typed action or callable adapter.
Generation fails closed for unregistered callables, ambiguous schemas, undeclared side effects,
missing authorization or resource policy, or accidental HTTP/MCP exposure.

## Motivation and background

Gradio `Interface` demonstrates the useful outcome of turning a model function into a shareable
demo with little code. Hedron already has typed actions, forms, fragments, jobs, and interaction
graphs. What is missing is a deliberate demo composition layer that preserves explicit registration,
authorization, rate/resource policy, and exposure — without automatically publishing arbitrary
callables or introducing a second application runtime.

## Proposed design

### InferenceInterface / ModelDemo

- Build a reviewable input/result surface only from an explicitly registered typed action or
  callable adapter. Unregistered callables raise diagnostics and refuse generation.
- Support multiple inputs and outputs, submit/clear/stop, declared safe live/debounced mode,
  preprocessing/postprocessing, artifacts, descriptions, and component overrides.
- Side effects, authorization, rate/resource policy, cache policy, and HTTP/MCP exposure remain
  independently explicit. The demo layer never infers public exposure from UI composition alone.
- Ordinary typed actions remain usable without the demo layer through ordinary HTTP.

### Fail-closed registration

Refuse generation when any of the following hold:

- callable is not registered as a typed action or approved adapter;
- input/output schemas are ambiguous or incomplete;
- side effects are undeclared;
- authorization or resource/admission policy is missing;
- HTTP or MCP exposure would be accidental rather than explicit.

### Lifecycle

Submit, clear, stop, progress, cancellation, and stale-result rejection compose with
`InferencePolicy` (RFC-0047) and existing action/job contracts. Live/debounced execution requires
an idempotent declared action plus rate, cancellation, and stale-result policy.

## Alternatives considered

1. **Gradio-style automatic publication of arbitrary callables.** Rejected — conflicts with explicit
   exposure and authorization (D-049 deliberate non-parity).
2. **Compose demos only with ad-hoc pages (no demo layer).** Rejected — loses fail-closed schema
   checks, Explorer diagnostics, and `DEMO-018` evidence required by the 0.18 exit gate.
3. **Embed Gradio UI runtime in core.** Rejected — optional protocol adapter only (RFC-0049).

## Security implications

Demo generation never expands endpoint authority. Browser identity and UI option filtering are not
authorization. Accidental API/MCP exposure fails closed. Artifact and upload paths reuse existing
file authorization, size, content-type, and cleanup contracts.

## Accessibility implications

Generated demos must preserve focus, announce busy/error states, support keyboard alternatives for
media and ranked outputs, honor reduced-motion, and keep no-JavaScript full-fragment HTTP paths
functional. Presentation components are owned by RFC-0046.

## Performance implications

Live/debounced modes require declared rate and resource policy. Generation cost, payload caps, and
admission remain owned by the action and `InferencePolicy`. Demo scaffolding must not bypass
queue/concurrency groups.

## Testing strategy

Unit fail-closed registration diagnostics; integration submit/clear/stop/progress/cancel; adversarial
unregistered callable, ambiguous schema, undeclared side effect, and accidental exposure schedules.
Gate command under `DEMO-018`.

## Compatibility and migration

Additive APIs. Existing typed actions remain valid without registering a demo. Gradio migration
inventories map `Interface(fn, …)` → registered action + `InferenceInterface` without claiming
automatic conversion (`MIGRATE-018`).

## Open questions

None blocking Acceptance. Explorer demo diagnostics may ship with `experimental` labeling until
reference-app evidence lands.

## Acceptance criteria

- Interface generation fails closed for unregistered callables and the other refuse conditions above.
- Equivalent typed actions remain usable without the demo layer through ordinary HTTP.
- Multi I/O, submit/clear/stop, and declared live/debounced mode are supported with explicit policy.
- Reference model application composes a demo over synthetic typed actions (`DEMO-018`).
