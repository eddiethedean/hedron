# Phase 1.1: first-class UI testing and adoption confidence

**Status:** Proposed refinement; implementation not authorized
**Predecessor:** Published Hedron `v1.0.0`
**Authority:** [RFC-0097](../rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md)
**Acceptance:** [RELEASE_1_1](../acceptance/RELEASE_1_1.md) ·
[release-gate-1.1.toml](../acceptance/release-gate-1.1.toml)

## Outcome

An application author can test a real Hedron user interface with pytest while Hedron manages the
application host, browser context, framework settle facts, error correlation, cleanup, and failure
evidence. Render tests and `AppScenario` remain the preferred faster layers when a real browser is
not required.

This document defines work packages and repository seams. Names and signatures shown here are
candidates until `FREEZE-110` is Verified.

## Entry lock

Stage 1 is blocked until W0 produces and freezes:

- a public-task inventory for render, application-contract, and browser testing;
- the exact `BrowserScenario`/pytest fixture candidate API and Playwright escape hatch;
- managed-host and external-URL support/maturity dispositions;
- a versioned settle record and a catalog of observable Hedron-owned lifecycle facts;
- a versioned failure-bundle schema, redaction rules, capture profiles, and size limits;
- default console, server, request, response, asset, and expected-failure policies;
- the reference behavior and deliberate-failure corpus;
- supported Python, host, browser, Playwright, pytest, OS, and parallel-execution matrices;
- measured performance, resource, artifact, and release-CI budgets; and
- additive packaging and compatibility decisions for `hedron[browser]` and a possible
  `hedron[testing]` extra.

The lock may choose different public spellings from this proposal. It may not authorize a fake DOM,
remote capture by default, a second test runner, a production runtime authority, or a regression in
the stable 1.0 testing inventory.

## Repository seam map

| Seam | Current owner | 1.1 responsibility |
|---|---|---|
| Render assertions | `hedron.testing.fastapi` / renderer | Preserve; document as layer one |
| HTTP/HTMX scenarios | `hedron_core.testing.app`, adapter fixtures | Preserve; document as layer two and reuse portable response facts |
| Browser hooks | `hedron.testing.browser` | Refine low-level imports and compose with the new scenario without breaking them |
| Interaction trace | `hedron-core` trace/lifecycle contracts | Supply redacted, versioned events to settle and failure evidence |
| Marks and regions | component/render and testing helpers | Supply stable app-aware locator identity |
| Managed host | new optional testing module | Own listener, readiness, lifespan, root path, exception channel, and teardown |
| Pytest integration | new optional plugin module | Own fixture/options/markers/artifact lifecycle without base-import side effects |
| Browser engine | Playwright | Own page, locator, actionability, web assertions, contexts, traces, screenshots |
| Test generation | `hedron testgen` | Optionally emit reviewable browser stubs from declared interactions |
| Documentation/scaffold | docs and `hedron new` | Teach the testing pyramid and include one bounded browser example |

Candidate source placement is `hedron.testing.browser_scenario` plus
`hedron.testing.pytest_plugin`; Stage 0 must confirm import layering before these paths become
public. Core-only modules cannot import pytest, Playwright, Uvicorn, or host implementations.

## Candidate public artifacts

| Artifact | Candidate maturity | Contract |
|---|---|---|
| `BrowserScenario` | Stable candidate | One application/browser test session with navigation, semantic lookup, settle, error, and cleanup behavior |
| `hedron_ui` pytest fixture | Stable candidate | Isolated scenario factory or instance; exact fixture shape freezes in W0 |
| `from_app` managed ASGI host | Stable candidate | Loopback-only ephemeral live server with readiness, lifespan, root path, assets, and bounded teardown |
| `from_url` external host | Stable candidate | Host-neutral browser session; non-loopback use is explicit and capture-conservative |
| mark/region locators | Stable candidate | Strict lookup by rendered `data-hedron-mark` or declared region identity |
| settle record v1 | Beta candidate | Bounded owned-work facts; never a claim that arbitrary browser work is idle |
| failure bundle v1 | Beta candidate | Redacted and bounded diagnostic artifact with provenance and missing-data markers |
| browser `testgen` profile | Beta candidate | Reviewable pytest stub generation; no execution or overwrite authority |
| visual golden comparison | Deferred | Requires a separate baseline/review/platform-variance contract |

Only evidence can promote a candidate. A convenient import, manifest, or generated stub does not
make an artifact Stable.

## Work packages

### W0 — Baseline, prototypes, and `FREEZE-110`

- Inventory all current testing exports, browser fixtures, first-party browser helpers, raw
  Playwright setup, sleeps, server launchers, artifact patterns, and CI browser jobs.
- Build two disposable API prototypes: thin `.page` composition and bounded locator delegation.
- Run a documented fresh-user exercise against both prototypes and record ambiguity, setup time,
  failure comprehension, and escape-hatch needs.
- Probe managed ASGI, Flask, Django, and external-URL lifecycle behavior without assuming parity.
- Capture baseline startup, navigation, settle, cleanup, xdist, and artifact measurements.
- Freeze public names, schemas, maturity, support matrix, budgets, and the Required corpus.

**Exit:** `FREEZE-110` is Verified and no open design question changes authority or release scope.

### W1 — Managed host and isolation

- Start the flagship application on a pre-bound ephemeral loopback listener to prevent port races.
- Enter and exit application lifespan exactly once; surface startup/shutdown exceptions.
- Preserve configured root path, forwarded/path behavior, cookies, static assets, build manifest,
  and dependency overrides.
- Provide readiness based on an owned signal rather than retrying an arbitrary public page.
- Isolate temporary roots, logs, registries, overrides, ports, threads/processes, and worker ids.
- Implement cancellation and forced bounded cleanup without leaking a background host.
- Add `from_url` with explicit remote authorization and capture/network policy.

**Exit:** repeated, failed, timed-out, interrupted, and xdist sessions leave no live resource and
produce a deterministic startup or teardown diagnostic.

### W2 — Browser session and semantic lookup

- Compose the managed/external host with the pinned Playwright pytest/browser lifecycle.
- Expose direct `Page`, `BrowserContext`, and supported Playwright configuration where needed.
- Add only the frozen convenience surface for goto, role, label, text, mark, and region lookup.
- Preserve Playwright strictness, auto-waiting, web assertions, device/viewport, locale/timezone,
  color-scheme, reduced-motion, and JavaScript settings.
- Generate app-aware ambiguity reports containing semantic candidates without dumping secrets.
- Make CSS/XPath an explicit direct-Playwright path rather than a Hedron locator abstraction.

**Exit:** the locator corpus proves accessible-first lookup, strict ambiguity, dynamic re-query after
swaps, shadow/element boundary dispositions, and direct Playwright interoperability.

### W3 — Owned-work settle probe

- Install a test-only observer before application scripts without changing shipped browser assets.
- Normalize HTMX/Hedron request generation, swap, settle, abort, timeout, error, and removal events.
- Consume existing action-state and interaction-trace identities rather than inventing parallel ids.
- Observe only documented first-party Alpine and Web Component lifecycle facts.
- Define opt-in polling/action completion waits and reject implicit unbounded background waiting.
- Return a versioned settle record with current/pending events, sources, ages, truncation, and
  unavailable facts.
- Add a source check banning arbitrary sleeps from maintained browser examples and generated tests.

**Exit:** every maintained interaction either settles through the owned schema or has an explicit
non-settling/third-party disposition; deliberate hangs produce actionable timeouts.

### W4 — Error correlation and expectations

- Capture server exception chains through a bounded channel tied to test/request identity.
- Capture page errors, console messages, request failures, responses, asset failures, and crashes.
- Define default severity and allow/expect APIs with lexical scope and automatic restoration.
- Keep validation, authorization, and domain failure responses testable without global suppression.
- Correlate browser requests, Hedron operation ids, lifecycle events, route ids, and server errors.
- Make `assert_clean()` deterministic and include unexpected/missing expected failures.

**Exit:** each deliberate failure class is detected at the right boundary, expected failure UI can
pass narrowly, and no ignored failure leaks into a later test.

### W5 — Artifact schema, redaction, and retention

- Implement the frozen failure-bundle schema and deterministic artifact directory layout.
- Retain Playwright trace, screenshot/DOM when policy permits, semantic diagnostic, settle record,
  redacted interaction/server/browser facts, and environment manifest.
- Apply header, cookie, query, form, `Secret`, field-policy, URL, and structured-trace redaction
  before writes; record fields that cannot be safely captured.
- Bound event counts, bodies, screenshots, traces, total bytes, names, path depth, and retention.
- Reject path traversal and unsafe archive/member names derived from test ids or URLs.
- Disable upload/telemetry and define conservative non-loopback capture defaults.
- Supply one command/instruction for opening the retained Playwright trace.

**Exit:** adversarial secret, path, huge-body, repeated-failure, partial-write, and disk-budget tests
pass; every omission/truncation is visible rather than reported as complete evidence.

### W6 — Pytest integration, packaging, and authoring loop

- Add the frozen optional dependencies without importing them from base/core paths.
- Register fixtures, markers, browser/options, artifact policy, timeout, and network policy with
  deterministic precedence across CLI, config, marker, and fixture inputs.
- Compose with pytest-playwright rather than forking its engine/browser lifecycle where possible.
- Support collection without installed browser binaries and provide an actionable installation
  diagnostic; skipped release evidence is never green.
- Make xdist artifact paths, ports, browser contexts, and managed apps worker-safe.
- Extend `hedron new` and optionally `hedron testgen` with a small reviewable browser example.
- Add task-oriented installation, local debug, headed, trace, CI, and troubleshooting guidance.

**Exit:** a clean generated project installs one optional testing surface and runs render, HTTP,
and browser examples with ordinary pytest; core/base installations remain unchanged.

### W7 — Reference behavior and accessibility verticals

- Implement the ten RFC reference behavior families using synthetic data and stable semantics.
- Cover PAGE/fragment/OOB/history, forms/security failures, local/request/combined interactions,
  specialist elements, focus/keyboard, uploads/downloads, action states, no-JS, and failures.
- Exercise reduced motion, forced colors, zoom/reflow, representative viewports, and semantic names.
- Integrate axe with engine/version/scope/incomplete metadata and deliberate violation fixtures.
- Run Chromium as the ordinary default and the bounded corpus on Chromium, Firefox, and WebKit.
- Prove root-path/proxy and external URL paths; add managed adapter rows only at their frozen maturity.

**Exit:** `BEHAVIOR-110`, `A11Y-110`, and the browser/host matrix pass with no blanket accessibility
or managed-adapter parity claim.

### W8 — Compatibility, fleet, and release closure

- Freeze and compare the stable 1.0 testing inventory, signatures, behavior, imports, and extras.
- Run clean base, browser, and testing-extra wheel/sdist/offline-install fixtures.
- Prove package import order and missing-extra messages without optional dependency leakage.
- Adopt the harness in the reference app and a bounded first-party package sample before promotion.
- Verify documentation, scaffold, testgen, testing API, stability, support, and compatibility claims.
- Run security, accessibility, performance, browser, adapter, package, and rollback evidence.

**Exit:** all Required `*-110` rows are Verified and the release packet contains immutable evidence.

## Dependency and delivery order

```text
W0 freeze
  -> W1 managed host
  -> W2 browser session
  -> W3 settle probe -----> W7 behavior/a11y corpus
  -> W4 error policy ----/          |
  -> W5 artifacts -------/          v
  -> W6 pytest/package -----------> W8 release closure
```

W1 and the schema portions of W3–W5 may proceed in parallel after the freeze. W7 requires the
vertical slice from W1–W6. No public promotion occurs before W8.

## Required vertical slice

The first end-to-end slice is a secured profile form in the reference application:

1. managed ASGI host starts on loopback with lifespan, root path, static assets, and synthetic user;
2. the test navigates by URL and locates the form through roles and labels;
3. invalid submission proves field error, focus, announcement, and expected 422 behavior;
4. valid submission triggers one HTMX request, swap, action terminal state, and visible success;
5. `assert_clean()` reports no unhandled failure;
6. an intentional failure proves screenshot/DOM policy, Playwright trace, interaction trace, server
   correlation, redaction, and a useful timeout/error message; and
7. success, failure, timeout, and interruption leave no host, port, context, override, or temp file.

This slice passes Chromium before breadth work begins. Firefox/WebKit and adapter/external rows join
in W7.

## Diagnostics and budgets

Candidate diagnostic families are `HED-TEST-HOST-*`, `HED-TEST-LOCATOR-*`,
`HED-TEST-SETTLE-*`, `HED-TEST-ERROR-*`, `HED-TEST-ARTIFACT-*`, and
`HED-TEST-CONFIG-*`. Stage 0 freezes code ownership, severity, remediation, structured fields, and
suppression/expectation behavior.

Budgets cover startup/readiness, navigation and probe overhead, settle event count/bytes, server and
browser queues, screenshot/DOM/trace size, aggregate artifacts, path/name lengths, shutdown,
parallel workers, memory, processes, and release-matrix duration. Exact-limit and one-over-limit
tests are Required. Moving data from a trace into DOM, screenshots, logs, or archives does not bypass
a budget.

## Compatibility and rollback

- Stable 1.0 test helpers and imports remain source-compatible.
- Disabling/uninstalling the optional testing extra restores the 1.0 base dependency graph and
  runtime output.
- The test observer is injected by the browser context and is not shipped in production assets.
- The managed host binds loopback only and changes no production server defaults.
- Versioned settle and artifact records accept compatible unknown fields and reject incompatible
  schema versions with an actionable diagnostic.
- If browser lifecycle, redaction, or cleanup cannot meet the Required gates, the candidate remains
  Beta/internal or the phase ships only adoption/compatibility documentation; it is not promoted by
  schedule.
- The unassigned HTMX/Alpine transition is not a rollback mechanism and cannot be bundled into 1.1.

## Stop conditions

Stop or narrow the phase if the design requires a fake browser semantics layer, a base Playwright or
pytest dependency, remote access/capture by default, global failure suppression, arbitrary sleeps,
production asset instrumentation, unstable hidden Playwright internals, managed-host privilege
expansion, or a weakening of 1.0 rendering/interaction/security behavior.

Also stop promotion if failures can lose server exceptions, artifacts can expose known secrets or
escape their root, cleanup leaks resources, required browser evidence is skipped, or the supported
matrix cannot be reproduced from clean artifacts.

## Definition of done

The phase is done only when a clean generated application demonstrates the three testing layers;
the managed browser test uses semantic locators and no manual server or sleeps; deliberate failures
produce correlated bounded evidence; the Required browser/host/accessibility/security/performance
matrix passes; optional imports and parallel cleanup are proven; stable 1.0 testing behavior is
unchanged; and every Required release-gate row is Verified.
