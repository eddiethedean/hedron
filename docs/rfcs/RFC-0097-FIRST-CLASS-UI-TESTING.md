# RFC-0097: First-class UI testing and adoption confidence

**Status:** Proposed; Stage 0 refinement only
**Target:** Hedron `1.1` planning candidate
**Baseline:** Published Hedron `v1.0.0`
**Implementation:** [UI_TESTING_1_1](../implementation/UI_TESTING_1_1.md)
**Acceptance:** [RELEASE_1_1](../acceptance/RELEASE_1_1.md) ·
[release-gate-1.1.toml](../acceptance/release-gate-1.1.toml)

## Summary

Hedron 1.1 should make real user-interface testing an ordinary pytest task. An application author
should be able to supply a Hedron application, open a real browser, interact through accessible
roles and labels, and receive useful failure evidence without manually starting a server or
assembling browser lifecycle, tracing, and cleanup infrastructure.

The phase composes rather than replaces the existing testing layers:

1. deterministic component rendering remains the fastest unit-test path;
2. `AppScenario` remains the request, fragment, CSRF, cookie, and outcome contract path; and
3. a candidate `BrowserScenario` plus pytest fixture owns real-browser behavior.

The browser layer uses Playwright as the browser authority. Hedron adds only framework-specific
value: managed application hosting, semantic Hedron locators, bounded interaction-settle facts,
correlated server/browser diagnostics, safe cleanup, and failure artifacts. It does not implement
a fake DOM, copy Playwright's complete API, or introduce a second application runtime.

This refinement assigns 1.1 to testing and adoption confidence. The older unaccepted
HTMX/Alpine 1.1 transition proposal is therefore unassigned and cannot change 1.1 runtime behavior
without a separate accepted RFC and phase decision.

## Motivation and background

Hedron 1.0 already exposes useful but separate pieces:

- `render_html`, `assert_renders`, and render-result assertions for deterministic output;
- `fragment_client`, portable adapter fixtures, and `AppScenario` for HTTP/HTMX contracts;
- `playwright()` and axe helpers as low-level optional browser hooks; and
- interaction traces, marks, regions, state matrices, and `hedron testgen` as reusable facts.

Those pieces do not yet provide one supported path for starting a live application, obtaining an
isolated browser page, waiting for Hedron-owned work, correlating server and browser failures, or
retaining a bounded diagnostic bundle. Application authors currently have to design those parts
themselves. That makes small UI tests disproportionately expensive and encourages arbitrary sleeps,
fragile CSS selectors, and incomplete failure reports.

The phase addresses an adopter problem, not a missing runtime capability. Production rendering,
routing, interaction, state, and security authorities stay unchanged. The testing package observes
the existing contract from a controlled test process.

## Goals

1. Make the first meaningful browser test short, discoverable, and runnable with ordinary pytest.
2. Exercise the actual browser implementation of native HTML, HTMX, Alpine, and Web Components.
3. Reuse accessibility-oriented roles, labels, names, text, and stable Hedron marks or regions.
4. Remove manual server, port, lifespan, root-path, asset, browser, and teardown plumbing.
5. Replace arbitrary sleeps with bounded Hedron-owned settle facts and Playwright web assertions.
6. Turn a failure into an actionable, correlated, redacted, and size-bounded evidence bundle.
7. Preserve direct Playwright access for behavior outside Hedron's owned semantics.
8. Preserve every stable 1.0 testing API and the no-browser fast path.

## Testing layers and authority

| Layer | Authority | Intended evidence |
|---|---|---|
| Render | Hedron renderer | Deterministic HTML, assets, diagnostics, and metadata without HTTP or a browser |
| Application contract | `AppScenario` and host test client | Page/fragment shape, cookies, CSRF, headers, targets, outcomes, and multi-step HTTP flow |
| User interface | Playwright browser plus candidate `BrowserScenario` | DOM behavior, user actions, HTMX/Alpine/component lifecycle, focus, history, and platform behavior |

Browser tests do not replace render or `AppScenario` tests. Scaffolds and documentation teach the
lowest layer that can prove a behavior. Browser tests are reserved for behavior that depends on an
actual user agent or the interaction among browser authorities.

## Proposed design

### Primary pytest experience

The candidate primary surface is an optional pytest fixture backed by a `BrowserScenario` object.
The exact fixture and method names remain a `FREEZE-110` decision, but the target ergonomics are:

```python
def test_profile_save(hedron_ui, app):
    ui = hedron_ui(app)
    ui.goto("/profile")

    ui.get_by_label("Name").fill("Ada")
    ui.get_by_role("button", name="Save").click()

    ui.expect(ui.get_by_text("Saved")).to_be_visible()
    ui.assert_clean()
```

The fixture starts a managed loopback host, waits for readiness, creates an isolated browser
context, installs test-only observation hooks, and guarantees bounded teardown. A direct
constructor remains available for non-pytest consumers, but pytest is the documented runner.

`BrowserScenario` may delegate a small semantic locator subset for convenience, but it must expose
the underlying Playwright `Page`. It must not wrap the complete locator, action, expectation,
network, context, or browser API.

### Application sources

Two sources are required candidates:

- `from_app(app)` or the equivalent fixture form manages the flagship ASGI application on an
  ephemeral loopback listener; and
- `from_url(url)` drives an already running application and is host-neutral.

Managed Flask and Django launchers are admission candidates, not assumed parity. The portable
contract for every supported host is an external URL plus browser behavior; Stage 0 decides which
managed host launchers can be Supported without hidden framework-specific lifecycle behavior.

Non-loopback URLs require explicit remote-test authorization. Remote mode uses a conservative
artifact policy and may not silently capture production pages, cookies, or response bodies.

### Semantic lookup

The preferred order is role and accessible name, associated label, visible text, and other
Playwright semantic locators. `data-hedron-mark` and declared region identity provide explicit
stable identities when user-facing semantics are not unique or are not the behavior under test.
CSS and XPath remain Playwright escape hatches rather than Hedron's recommended default.

Strict locator behavior is preserved. An ambiguous role, label, mark, or region fails with the
matched candidates and remediation; Hedron does not silently select the first element.

### Settle contract

Playwright remains responsible for actionability and retrying web assertions. Hedron adds a narrow
`wait_for_settled()`-style operation for Hedron-owned work only. The candidate settle record covers:

- active Hedron/HTMX request generations;
- the latest request's swap and settle lifecycle;
- pending Hedron action-state transitions;
- registered first-party Web Component initialization/cleanup facts where the ABI exposes them;
- bounded Alpine/Hedron lifecycle handoff queued by the tested interaction; and
- declared polling or asynchronous status only when the test opts into that operation.

It does not claim that arbitrary third-party JavaScript, animations, timers, sockets, analytics,
or the whole network are idle. A timeout reports each remaining owned fact, its age and source,
the last lifecycle events, and the artifact location. First-party examples may not use sleeps to
hide missing settle semantics.

### Error policy

The scenario records server exceptions, page errors, console messages, request failures, asset
failures, and Hedron interaction failures. `assert_clean()` fails on unhandled server exceptions,
uncaught page errors, unexpected error-level console messages, and required asset/network failures.

HTTP 4xx/5xx responses are not universally treated as harness failures: validation, authorization,
and failure UI are legitimate test subjects. Tests can assert or allow expected failures through a
scoped rule. Broad global ignore lists and silent console suppression are not supported defaults.

### Failure bundle

On failure, the pytest integration retains a versioned, bounded bundle. Candidate members are:

- screenshot and DOM snapshot under the active artifact policy;
- Playwright trace;
- console, page-error, request, response, and failed-resource summaries;
- redacted Hedron interaction trace and server exception chain;
- route, root-path, browser, engine, Python, Hedron, dependency, OS, viewport, and test identity;
- settle-state snapshot and the final semantic locator diagnostic; and
- explicit missing/truncated/redacted markers.

Known secret headers, cookies, query values, form fields, and Hedron `Secret` values are redacted
before persistence. DOM and screenshots can contain application content that is not mechanically
recognizable as secret; managed tests therefore require synthetic fixtures, and remote capture is
conservative and explicit. Artifacts are test outputs, never telemetry, and are not uploaded by
Hedron.

### Packaging and pytest integration

Stage 0 evaluates an additive `hedron[testing]` extra containing the supported pytest and browser
integration. The existing `hedron[browser]` extra and low-level imports remain compatible.
An auto-discovered pytest plugin may add fixtures, markers, and options only; importing Hedron in a
non-pytest process must not import pytest or Playwright.

The ordinary command remains `pytest`. Hedron may extend `hedron testgen` to emit reviewable
browser-scenario stubs and may add a read-only testing doctor, but it does not add a competing test
runner.

## Reference behavior corpus

The release corpus includes at least:

1. full-page navigation and ordinary links/forms;
2. HTMX fragment, OOB, retarget, redirect, push-url, history, abort, and error paths;
3. schema-derived form fill, validation, CSRF, authorization denial, and success;
4. local-only Alpine state plus server-only and combined interactions;
5. retained specialist Web Components and their initialization/cleanup contract;
6. focus movement/return, keyboard operation, announcements, reduced motion, forced colors,
   zoom/reflow, and representative viewport changes;
7. uploads, downloads, redirects, cookies, sessions, and dependency overrides using synthetic data;
8. polling/action-state terminal success, validation, failure, cancel, and stale-result paths;
9. JavaScript-disabled and required-asset-failure fallback; and
10. deliberate server, page, console, locator, settle, and network failures proving diagnostics.

Chromium is the local/default engine candidate. Chromium, Firefox, and WebKit are required for the
bounded release corpus, not necessarily for every application test on every commit.

## Alternatives considered

### Expand `AppScenario` into a DOM simulator

Rejected. `AppScenario` is valuable because it tests HTTP contracts without pretending to execute
native browser behavior, HTMX, Alpine, Web Components, focus, or history. A partial simulator would
create false confidence and a second frontend semantics implementation.

### Expose raw Playwright only

Retained as the advanced escape hatch but insufficient as the complete Hedron experience. Raw
Playwright does not own Hedron application startup, interaction-settle facts, server exception
correlation, marks/regions, redaction, or framework-specific failure evidence.

### Build a complete Hedron locator and assertion DSL

Rejected. Playwright already owns robust locators, actionability, auto-waiting, and web assertions.
Hedron adds a small semantic convenience surface and framework diagnostics, not a shadow API.

### Add a `hedron test ui` runner

Rejected. Pytest is already the project and ecosystem runner. A second runner would split fixture,
plugin, selection, parallelism, and CI configuration.

### Make visual golden comparisons Stable in 1.1

Deferred. Screenshots are Required failure evidence. Baseline management, platform-font variance,
pixel thresholds, review workflows, and intentional-update provenance require a separate maturity
decision before visual comparisons can be Stable.

## Security implications

- Managed hosts bind to loopback only and use validated ephemeral listeners.
- External network requests are denied or reported by the deterministic default policy and require
  an explicit allowlist where application behavior needs them.
- Remote/non-loopback targets require explicit authorization and conservative capture defaults.
- Cookies, authorization headers, CSRF values, secrets, and configured sensitive fields are
  redacted from logs and traces before persistence.
- Artifact paths, names, sizes, counts, retention, and archive behavior are bounded; test names and
  URLs cannot escape the artifact root.
- Browser contexts, dependency overrides, registries, temporary files, processes, threads, ports,
  and credentials are isolated and cleaned up after success, failure, cancellation, and timeout.
- The harness does not bypass application authorization, manufacture a principal, or infer that a
  browser-visible control grants server authority.

## Accessibility implications

Semantic role/name and label locators reward accessible application markup and expose ambiguous or
missing names early. The release corpus covers keyboard, focus, announcements, reduced motion,
forced colors, zoom/reflow, and JavaScript-disabled behavior where automated evidence is meaningful.

axe results retain engine/version, scope, incomplete, skipped, and error metadata. An empty
violation list is not an accessibility or WCAG conformance claim. Human assistive-technology
evaluation remains owned by its separate protocol and phase.

## Performance implications

Browser startup is inherently more expensive than render or `AppScenario` tests. Documentation and
scaffolds preserve the testing pyramid and do not make browser tests the default for pure rendering
or HTTP behavior.

`FREEZE-110` records measured budgets for managed-host readiness, first navigation, settle overhead,
memory/process cleanup, artifact size/count, parallel workers, and release-matrix duration. No exact
threshold is invented before the baseline probe. On-success tracing and screenshots are disabled or
minimal by default; failure evidence is bounded.

## Compatibility and migration

The phase is additive to the stable 1.0 testing inventory. `AppScenario`, adapter fixtures,
`fragment_client`, render assertions, browser helpers, marks, and existing imports remain valid.
The optional browser/testing extra cannot become a base dependency, and render/HTTP tests retain a
no-browser and no-Node path.

Generated scaffolds may add a new browser-test example but do not rewrite existing projects.
`hedron testgen` output remains review-first and never executes generated tests or overwrites a file
without explicit authorization.

The previous `HTMX_ALPINE_REFINEMENT_1_1_2_0` proposal is recorded as unassigned design input. Its
runtime changes, compatibility shims, deprecations, and proposed 2.0 removals are not part of this
phase. Any subset later proposed for a release needs its own accepted authority and compatibility
packet.

## Open questions for `FREEZE-110`

1. Is `BrowserScenario` the stable class name, and is `hedron_ui` the stable fixture name?
2. Does the scenario delegate common Playwright locators or expose them only through `.page`?
3. Which managed launchers beyond the flagship ASGI host can meet the lifecycle contract?
4. Is `hedron[testing]` the additive installation name, and how does it compose with
   `hedron[browser]`?
5. Which console and request failures fail `assert_clean()` by default, and what is the scoped
   expected-failure API?
6. Which first-party events constitute the exact settle schema and version?
7. What capture profile is safe and useful for local, CI, and explicitly authorized remote tests?
8. Which budgets and supported OS/browser revisions are justified by the Stage 0 measurements?

Implementation does not begin until these decisions, the evidence schema, and the reference corpus
are frozen. Resolving an open question may narrow the phase; it may not silently broaden runtime or
remote-testing authority.

## Acceptance criteria

1. One optional install and ordinary pytest run a managed-app browser test without manual server
   setup.
2. The public candidate composes with Playwright instead of emulating browser behavior or copying
   its full API.
3. Semantic locators, marks, regions, strict ambiguity, and direct Playwright escape hatches pass.
4. Hedron-owned settle facts eliminate sleeps from maintained browser examples and diagnose every
   timeout.
5. Unhandled server/browser failures cannot silently pass, while expected HTTP failure UI remains
   testable through scoped assertions.
6. Every failed release-corpus test creates a bounded evidence bundle with explicit redaction,
   truncation, provenance, and missing-data markers.
7. The reference corpus passes its declared Chromium/Firefox/WebKit and host/root-path matrix.
8. Accessibility checks are provenance-bearing and make no automated conformance claim.
9. Parallel execution leaves no ports, processes, threads, browser contexts, overrides, registries,
   or temporary artifacts active after the test session.
10. Stable 1.0 testing imports and behavior remain compatible, and non-browser tests gain no
    browser, pytest, Node.js, or service dependency.
11. Documentation teaches the testing layers, failure workflow, security limits, and lowest-cost
    appropriate test.
12. Every Required row in `release-gate-1.1.toml` is Verified before any release claim.
