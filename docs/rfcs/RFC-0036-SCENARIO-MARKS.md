# RFC-0036: AppScenario identity marks and filter asserts

**Status:** Implemented
**Phase:** 0.15 (`v0.15.0`)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md)

## Summary

Extend the 0.15 `AppScenario` / HTMX testing helpers with stable identity **marks** and filter
asserts inspired by NiceGUI’s `ElementFilter` / `.mark()`, without inventing a parallel DOM
simulator or Streamlit-style rerun harness. Scenarios continue to execute ordinary host HTTP
against the production renderer.

## Motivation and background

NiceGUI’s fast `user` fixture queries marked elements. Hedron already plans route/fragment/header
asserts (#22–#26); authors still need ergonomic ways to locate components by stable test marks
and assert structure across PAGE vs FRAGMENT responses.

## Proposed design

- Optional `mark=` (or equivalent) on selected builtins / component props, emitted as a stable
  data attribute reserved for tests (not a public styling API).
- Scenario helpers: `find(mark=…)`, `find_all`, filter by component type / identity / region, with
  failures that print redacted HTML snippets and diagnostics.
- Marks are **not** authorization, routing, or addressable exposure; they must not appear in
  public OpenAPI as security parameters.
- Composes with existing InteractionResult, FragmentRegion, and markup asserts; Playwright remains
  required for focus/permission/playback.
- Document collision rules when multiple nodes share a mark.

## Alternatives considered

1. **CSS selectors only.** Insufficiently tied to component identity and easy to break on theme
   churn; still allowed as escape hatch.
2. **Full NiceGUI in-process element graph.** Deliberate non-parity — Hedron tests HTTP + HTML.
3. **Fold entirely into RFC-0019 revision without a new RFC.** Still acceptable later; this stub
   owns the NiceGUI-accepted gap until a decision merges it.

## Security implications

Marks must not embed secrets; test helpers redact tokens in failure output; marks unused in
production authz. Warn if marks leak into cached public HTML unexpectedly (document opt-in).

## Accessibility implications

Marks are test-only attributes; they must not replace accessible names or break semantics.

## Performance implications

Negligible in production if marks are stripped or cheap; scenario filtering stays O(nodes) with
documented limits for huge pages.

## Testing strategy

Meta-tests for the helpers themselves; examples in `tests/` showing mark → assert flows; ensure
fragment-only responses still resolve marks.

## Compatibility and migration

Additive. RFC-0019 remains the parent testing contract; this RFC is a 0.15 specialization.

## Accepted decisions (0.15)

1. **Production marks:** opt-in `mark=` emits `data-hedron-mark` and is never stripped (test-only
   contract; not a styling API).
2. **API surface:** `mark=` on `ElementProps` / selected builtins; filter helpers on `AppScenario`.
3. **Syrupy:** not required; optional for adopters.

## Acceptance criteria

- AppScenario docs show mark/filter examples for form validation and fragment swaps.
- Helpers covered by unit tests; no dependency on Vue/NiceGUI test runtime.
- 0.15 HTMX testing exit rows (#22–#26) remain satisfiable with or without marks.
