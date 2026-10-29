# RFC-0097: First-class UI testing and adoption confidence

**Status:** Proposed; candidate implementation in progress, release freeze not complete
**Planning revision:** 2026-10-28
**Target:** Hedron `1.3`
**Planning baseline:** Published `v1.2.0`
**Required release predecessor:** `v1.2.0` (publication evidence retained in the 1.3 gate)
**Compatibility baseline:** Stable `v1.0.0` testing inventory and subsequent additive 1.x behavior
**Implementation:** [UI_TESTING_1_3](../implementation/UI_TESTING_1_3.md)
**Acceptance:** [RELEASE_1_3](../acceptance/RELEASE_1_3.md) ·
[release gate](../acceptance/release-gate-1.3.toml) ·
[planning contract](../acceptance/ui-testing-contract-130.toml)

## Outcome and release scope

An author can run a meaningful browser test with ordinary pytest, direct Playwright locators and
assertions, and Hedron-owned application startup, bounded settling, diagnostics, and cleanup.
Render tests and AppScenario remain the faster layers for HTML and HTTP/security contracts.

The required first release is deliberately bounded: synchronous pytest/Playwright integration,
an isolated managed flagship ASGI application, an externally managed literal-loopback URL,
request-scoped observation, structured failure evidence, explicit capture profiles, and one
small versioned satellite contribution surface. Every coordinated package receives a testing
disposition; creating public testing modules or managed launchers for every package is not Required.

Phase 1.3 remains tooling-only. It does not change production assets, interaction semantics,
security, runtime instrumentation, or defaults. [RFC-0100](RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md)
owns new polling, loading, input-timing, and form/save behavior in 1.4–1.7. Existing behavior may be
tested now; those future features are not prerequisites or implicit 1.3 implementation scope.

## Current-source findings

The [implementation seam map](../implementation/UI_TESTING_1_3.md#current-source-inventory)
records reviewed files. The source already provides low-level synchronous Playwright/axe helpers,
AppScenario, marked HTML lookup, and browser CI. Private browser tests also contain reserve/release
port selection, TCP-connect readiness, mutable registry resets, thread-based Uvicorn launchers,
and an opt-in Playwright reuse monkey patch. These are migration inputs, not public host contracts.

The `hedron[testing]` extra and explicit pytest-playwright integration now exist. The
[local vertical-slice record](../acceptance/evidence-130/LOCAL_VERTICAL_SLICE_2026-10-28.md)
reports the managed profile and contribution examples passing 31 tests in each local browser
engine. This does not
establish the Linux matrix, user exercise, timing budget, complete behavior/security/accessibility
corpus, or package/release evidence. All `*-130` release gates remain Planned.

The candidate also includes a v1 contribution metadata type and an explicitly loaded
`hedron-sample-kit` fixture/app contribution. The [23-package disposition inventory](../acceptance/ui-testing-package-dispositions-130.toml)
is a draft pending maintainer review and fleet checks.

## Selected candidate decisions

These remain Beta candidate choices; local implementation exercises the flagship path, while the
accepted freeze and release evidence remain open.

| Concern | Selected candidate | Explicit limit |
|---|---|---|
| Public placement | `hedron.testing.browser_scenario` and `hedron.testing.pytest_plugin` | Existing root/low-level imports stay compatible; core imports no browser/host/pytest dependency |
| Installation | Additive `hedron[testing]` extra | Do not raise the existing browser extra floor merely for new harness features |
| Activation | `pytest_plugins = ["hedron.testing.pytest_plugin"]` in root conftest, or explicit `-p` | No new Hedron pytest11 entry point in the base distribution; no satellite auto-registration |
| Browser authority | Sync pytest-playwright fixtures and native `Page`, `BrowserContext`, `Locator`, `expect` | No locator/action/assertion DSL or monkey-patched browser reuse |
| Scenario construction | Function-scoped `hedron_ui` factory with context-managed `from_app` / `from_url` sessions | Sync first; no standalone second lifecycle/runner or asyncpytest API in Required scope |
| Managed source | Importable ASGI test-app factory in an isolated spawned child | No pickled live app, inherited event loop, parent TestClient/DB connection, or shared mutable registry |
| External source | Explicit literal-loopback origin, caller-owned server | No server-exception or lifespan evidence claim without an admitted channel |
| Lookup | `ui.page` semantic locators; narrow `ui.mark` / `ui.region` helpers return real Locators | Strict ambiguity and re-query preserved; no delegated `get_by_*` or `ui.expect` |
| Settling | Checkpoint-scoped observed request/swap/lifecycle completion | No global idle, networkidle, arbitrary sleeps, or future polling/visibility semantics |
| Default artifacts | Structured metadata only; bodies/DOM/screenshots/video/HAR/raw trace off | Known redaction is not proof that arbitrary content is safe |
| Rich artifacts | Explicit synthetic-only profile, captured during execution and retained on failure | Raw Playwright trace is labeled unredacted, never called sanitized |
| Maturity | New scenario/host/fixture/protocol Beta candidates in 1.3 | Stable 1.x imports remain Stable; no automatic promotion from convenience |

## Candidate pytest experience

The following illustrates the proposed API; it is not runnable against current Hedron.

```python
# root conftest.py — candidate, explicit activation
pytest_plugins = ["hedron.testing.pytest_plugin"]

# test_profile.py — candidate API
from playwright.sync_api import expect


def test_profile_save(hedron_ui):
    with hedron_ui.from_app("myapp.test_support:create_app") as ui:
        ui.page.goto(ui.url("/profile"))
        ui.page.get_by_label("Name").fill("Ada")

        before = ui.checkpoint()
        ui.page.get_by_role("button", name="Save").click()
        ui.settle(since=before, target="profile")
        expect(ui.page.get_by_role("status")).to_have_text("Saved")
```

The factory module is application-owned and importable in the child. Configuration is bounded
JSON-compatible synthetic data, not a transport for live objects or secrets. Overrides, synthetic
authentication, database construction, and temporary roots are created inside that factory. The
application's ordinary authorization/CSRF still runs. External URL sessions make no managed-host
guarantees. Exiting a session and fixture teardown automatically assert clean state; an explicit
`assert_clean()` remains a checkpoint, not something every author must remember.

The scenario exposes `page` and `context`, URL joining, mark/region lookup, checkpoint/settle,
bounded event snapshots, narrow expected-HTTP rules, and clean assertions. Playwright owns all
other browser operations. Exact signatures, exception types, configuration fields, and typing
must be frozen after the documented prototype/user exercise.

## Managed host and resource ownership

A fresh spawned child constructs each managed application. The child binds a literal-loopback
socket on port zero, retains that listener, starts the ASGI server with it, and reports the actual
origin through an owned readiness channel after lifespan/startup is complete. Reserving then
closing a port or treating a successful TCP connection as readiness is not accepted.

The parent owns supervision and a deadline; the child owns its app, listener, lifespan, request
exception channel, and shutdown. Readiness messages carry session identity and bounded facts.
Configure root_path/mount behavior deliberately: the public test URL and ASGI scope must agree,
not merely concatenate a prefix. Disable reload/multiple web workers in this launcher.

On normal close, dispose test observers/capture, close the scenario's page/context lease through
its single documented owner, request graceful child shutdown, wait, then terminate/kill/join after
the frozen deadlines if needed. Forced shutdown is reported as incomplete lifespan cleanup and a
test failure even if the OS process was removed. Startup failure, Ctrl-C, fixture setup failure,
and xdist worker interruption receive the same bounded supervision. No unkillable daemon thread
may be accepted as a successful cleanup.

pytest-playwright owns its driver/browser fixtures and option semantics. The Hedron adapter must
lease an isolated context through a supported fixture path, preserve browser/context arguments,
and coordinate a single actual close with plugin finalizers. Never close a borrowed browser or
share cookies/storage between tests. W0 must prove this integration, including tracing ownership,
instead of assuming `browser.new_context()` inherits plugin CLI flags.

## Observed-work settling

A checkpoint records session, navigation epoch, and an event sequence before the triggering action.
A settle call waits for a matching request to have actually started after that checkpoint, then
for that request's response/abort/error and applicable swap/settle phases. Capture events before
the action so a fast response cannot be missed. Cursors from another session or navigation epoch
are invalid; absence of a matching start is a diagnostic timeout, not immediate success.

Scope by the declared target and existing operation/generation identities where observable. Newer
requests may supersede old generations only under existing application policy. A canceled or 204
response must not wait for a nonexistent swap. Account for OOB/cleanup work only when exposed by a
documented causal/lifecycle fact. Unobservable first-party or third-party work is recorded as
unavailable and tested with an explicit Playwright predicate, never fabricated as completed.

Do not include future polling ticks, unrelated targets, animation frames, open streams, third-party
timers, or queued user actions in a global idle calculation. For local-only/no-JS behavior, use
native Playwright assertions. Explicit job-terminal predicates remain caller-owned. The test-only
observer cannot add shipped runtime events merely to satisfy itself.

The v1 record contains bounded source capability/availability, checkpoint/epoch, observed request
and operation identities, target, generation, pending/terminal facts, ages, truncation, and the
completion/timeout reason. The contract does not claim a browser freeze or atomic snapshot.

## Failure policy and correlation

| Observation | Default outcome |
|---|---|
| Unhandled managed server exception, pageerror, crash, console error | Fail; structured summaries omit arbitrary message/body content |
| Unexpected application 4xx/5xx | Fail unless a narrow expected-HTTP rule matches; ordinary validation/denial tests declare their expected response |
| Required script/style/asset failure or unexpected blocked external request | Fail with resource/capability facts |
| Known superseded-request abort | Record as cancellation under the existing policy; do not treat all requestfailed events as errors |
| Optional resource | Ignore only through a recorded exact policy; no universal favicon/third-party wildcard suppression |
| Missing expected response, capture/probe failure, queue overflow | Fail or explicit incomplete evidence; never silently clean |
| External-server exception details | Unavailable; browser-visible failures remain testable |

An expected-HTTP context is armed before an action and matches method, route/path, status, count,
and the current checkpoint/session. It does not suppress a pageerror, different server exception,
other request, or later test. Teardown calls clean checks automatically. Preserve the original
assertion/exception as primary; append cleanup and evidence-write problems rather than replacing it.

A managed test-only ASGI wrapper may emit opaque session/request correlation through the owned
channel. It must not change response bodies, swallowed exceptions, status, auth, CSRF, or production
middleware. Correlate existing operation ids when available; a synthetic test id is not application
authority. External sessions explicitly mark server correlation unavailable.

## Capture, privacy, and network boundaries

Structured capture is the default: no raw bodies, headers/cookies/storage, URL values, form values,
exception messages/locals, arbitrary console text, DOM, screenshots, traces, HAR, or video. Retain
allowlisted route/resource identifiers, safe metadata, event categories, counts, bounded stacks
without source locals/messages, correlation, policy, and omission markers. Unknown free text stays
withheld unless an admitted policy can make it safe.

The explicit synthetic profile can start native tracing before the test and retain it on failure,
plus bounded permitted screenshots/DOM. Trace recording may use private temporary files during a
successful test; failure-only retention is not failure-only recording. These native captures are
not generically redactable. Label them as synthetic/unredacted; do not promise post-hoc zip rewriting
removes secrets. A confidential-value corpus runs under structured-only capture with canary scans.
A separate synthetic corpus proves trace/viewer/screenshot behavior. Every bundle records omitted,
unavailable, truncated, capture-failed, or disabled members; a missing required synthetic capture
remains a failed artifact row.

One capture authority validates effective upstream `--tracing`, `--screenshot`, `--video`,
artifact directory, and context options before creation. Reject incompatible flags instead of
letting upstream finalizers write forbidden captures outside Hedron's policy. Raw captures cannot
be guaranteed within a hard byte cap by checking their final size alone; W0 must prove monitored
private temporary storage/termination limits or leave that capture disabled. Structured bundle
limits, safe paths, atomic manifests, no upload, and best-effort expiry remain Required.

Browser traffic is restricted to the scenario's literal-loopback origin by default, with declared
exact additional origins where needed. Redirects are denied because Playwright cannot safely recheck
each redirect hop. Service workers are blocked
in this controlled profile because they can bypass routing observation. This is test determinism,
not a complete network sandbox or a restriction on server-side application egress. WebSocket,
download, popup, and browser-origin capability limits must be stated per pinned browser version.
Non-loopback/production targets, remote browser attachment, and raw remote capture are Deferred.

## Satellite and host boundary

Inventory every coordinated/optional package, preserve stable flagship testing imports, and assign
module/facade/provider/testing-product/private/non-fit dispositions. Require one minimal admitted
specialist contribution and absence/conflict/version tests to prove the central protocol. Other
packages may remain private or Deferred without creating public testing modules merely for breadth.

V1 contributions carry package identity/version, supported schema versions, declared capabilities,
and bounded synthetic fixture/event summaries. An executable hook must be explicitly registered,
trusted test code with a bounded lifecycle; it is not sandboxed. No host, browser, locator, artifact
root, global error policy, or pytest plugin may acquire duplicate ownership. Managed WSGI/Posit
launchers, broad provider capabilities, and ownership moves are optional admission candidates;
caller-managed loopback URLs are the portable path.

## Delivery, matrix, and acceptance

Deliver the flagship vertical slice before satellite breadth: inventory/probes and freeze; managed
host/context/checkpoint/error core; one synthetic secured form plus intentional failure; artifact
and pytest hardening; minimal satellite contribution; bounded compatibility/release matrix.

Use Linux as the required initial OS, default-build CPython 3.11–3.14 for core/import/host/package
checks, and a bounded Chromium/Firefox/WebKit release corpus at the frozen integration runtime.
Cross Python and browser dimensions only where an integration risk needs it; do not silently imply
a full Cartesian matrix. macOS/Windows have explicit pilot dispositions until host/context/capture
probes pass. Browser install failure or an unexpectedly skipped Required row fails release evidence.

The [contract ledger](../acceptance/ui-testing-contract-130.toml) records candidate decisions,
scope, matrix, and Unmeasured budget rows. It cannot mark FREEZE-130 Verified. Freeze numeric
limits, dependency bounds/browser revisions, user-exercise results, commands, expected artifacts,
and named maintainers before release. Keep the existing 17 gate ids.

## Alternatives and deferred work

Reject a simulated DOM, complete Playwright wrapper, second runner, shared live app/loop/database
objects, thread-leak-as-success, raw-trace-redaction promises, and global-idle waits. Prefer the
thin direct-Page prototype; compare bounded delegation only in W0 to test whether it materially
helps novice authors. Record results rather than retaining two APIs.

Asyncpytest integration, standalone non-pytest lifecycle, managed WSGI launchers, non-loopback
testing, broad executable satellite hooks, browser testgen, testing-doctor commands, visual golden
baseline management, record/replay, and automatic migration of every historical browser test are
optional or Deferred. Keep one packaged/scaffold example Required and convert a bounded existing
reference subset; do not make historical sleep removal a whole-repository migration.

## Open feasibility evidence

W0 must still prove forced-stop/timeout cleanup, full pytest-playwright context and capture
ownership, observable request/lifecycle coverage without runtime modification, private capture
resource limits, dependency bounds/browser revisions, candidate typing, fresh-user comprehension,
and measured budgets. Preferred API choices above resolve direction, not those empirical questions.

All 17 Required release rows remain Planned. A cut needs accepted contracts, the 1.2 predecessor,
immutable evidence, compatibility, security, accessibility, package and rollback proof, and an
explicit release decision. Publication, release facts, production APIs, and 1.4–1.7 runtime behavior
remain unchanged by refinement.

## Sources

Design evidence: [Playwright pytest fixtures/options](https://playwright.dev/python/docs/test-runners),
[native tracing](https://playwright.dev/python/docs/api/class-tracing),
[trace viewing](https://playwright.dev/python/docs/trace-viewer),
[BrowserContext routing limits](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-route),
and [explicit pytest plugin loading](https://docs.pytest.org/en/stable/how-to/writing_plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file).
These support the tool boundaries; the selected Hedron API and release choices are this proposal.
