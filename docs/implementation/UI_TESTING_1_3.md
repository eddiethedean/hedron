# Phase 1.3: first-class UI testing and adoption confidence

**Status:** Candidate implementation in progress; local three-engine slice passes; all release gates remain open
**Planning revision:** 2026-10-28
**Planning baseline:** Published `v1.2.0`
**Release predecessor:** `v1.2.0`, published on PyPI and bound to the retained release evidence
**Compatibility baseline:** Stable `v1.0.0` testing inventory plus additive 1.x behavior
**Authority:** [RFC-0097](../rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md)
**Acceptance:** [RELEASE_1_3](../acceptance/RELEASE_1_3.md) ·
[release gate](../acceptance/release-gate-1.3.toml) ·
[planning contract](../acceptance/ui-testing-contract-130.toml)

**Release execution:** [1.3.0 readiness plan](EXECUTION_1_3.md) — ordered work packages,
regression coverage, CI/tooling updates, evidence, and release-candidate exit criteria.

## Outcome and bounded release

Run a real synthetic Hedron profile-form test with ordinary pytest and direct Playwright Page/
Locator/expect, without hand-written host startup or arbitrary waits. Hedron owns only managed
hosting, context integration, semantic mark/region helpers, checkpoint-scoped observation, error
correlation, structured artifacts, and deterministic cleanup. Render and AppScenario remain the
preferred lower-cost layers.

Required scope is sync pytest, a spawned flagship ASGI factory, literal-loopback external URLs,
one small specialist contribution, one packaged/scaffold example, and a bounded existing behavior
corpus. Managed WSGI/Posit, standalone/asyncpytest APIs, remote production testing, browser testgen,
visual golden management, and a fleet of new public testing modules are outside the required cut.
Existing 17 gate ids remain authoritative.

## Current-source inventory

Reviewed on 2026-10-28; source inspection does not verify prototype/runtime/release evidence.

| Seam | Reviewed source | Current finding / implementation action |
|---|---|---|
| Render and HTTP helpers | [fastapi.py](../../packages/hedron/src/hedron/testing/fastapi.py), [AppScenario](../../packages/hedron-core/src/hedron_core/testing/app.py) | Preserve public helpers and portable contract behavior; do not add DOM simulation |
| Browser/axe hooks | [browser.py](../../packages/hedron/src/hedron/testing/browser.py) | Sync lazy Playwright/axe imports; retain `playwright`, deprecated alias behavior, scan/report distinction |
| Root testing facade | [testing exports](../../packages/hedron/src/hedron/testing/__init__.py) | Freeze all existing exports and optional-import behavior before moving ownership |
| Dependency extras | [hedron metadata](../../packages/hedron/pyproject.toml) | `testing` extra now includes pytest, pytest-playwright, Playwright, and Uvicorn; plugin activation remains explicit |
| Private hosting | [shared harness](../../tests/browser/_harness.py), [Alpine fixture](../../tests/browser/test_phase067_alpine.py) | TCP polling, reserve/release port and daemon-thread patterns are migration inputs; do not publish them unchanged |
| Registry isolation | [browser conftest](../../tests/browser/conftest.py), [root conftest](../../tests/conftest.py) | Module/function reset ordering and Explorer registration motivate child-owned app isolation |
| Reuse experiments | [private reuse helper](../../tests/browser/_playwright.py) | Opt-in monkey patch is private; new harness uses supported upstream fixtures |
| Existing corpus | [HTMX lifecycle](../../tests/browser/test_htmx_lifecycle.py), [theme gallery](../../tests/browser/test_builtin_theme_gallery.py) | Choose a bounded reusable subset; route.fulfill/TestClient tests are not evidence for managed live-server lifecycle |
| Observable lifecycle | [UI module](../../packages/hedron-core/src/hedron_core/static/hedron-ui.mjs), [Alpine module](../../packages/hedron-core/src/hedron_core/static/hedron-alpine.mjs) | HTMX lifecycle events and data-hedron action markers exist; Python state objects alone do not prove browser readiness |
| CI/browser installation | [CI](../../.github/workflows/ci.yml), [installer](../../scripts/ci_install_playwright.sh) | Reuse pinned browser/dependency installation and existing browser job; missing browsers cannot satisfy release rows |

The [local vertical-slice record](../acceptance/evidence-130/LOCAL_VERTICAL_SLICE_2026-10-28.md)
records pytest 9.1.1, pytest-playwright 0.10.0, Playwright 1.62.0, Uvicorn 0.52.1, Python
3.12.13, macOS 26.6.2, browser versions, commands, and the 31-test result per engine. Do not
infer supported minimums or Linux release support from this one environment. No performance
budget or release matrix is claimed.

## Candidate implementation status

| Slice | Current state | Remaining evidence or work |
|---|---|---|
| Spawned ASGI host | Implemented and exercised for lifespan, startup failure, root path, static assets, and graceful stop | Forced-stop, timeout interruption, xdist, and broad fixture-failure cases |
| pytest/Playwright integration | Explicit sync plugin, lazy `new_context` lease, option guards, and native Page/Locator usage implemented | Setup/call/teardown matrix, reruns, missing-browser behavior, and clean package matrix |
| Checkpoint and settle | Bounded browser event ring, pre-action checkpoint, target-scoped request correlation, expected HTTP rules, and error collection implemented | Full 204/abort/OOB/removal/supersession/hung-request corpus and capability boundaries |
| Structured diagnostics | Versioned manifest, safe summaries, private per-run paths, atomic writes, and bounded size implemented | Confidential canary sweep, overflow/partial-write cases, and retained immutable artifacts |
| Synthetic native capture | Explicit synthetic marker and upstream trace/screenshot option validation implemented | Recording-time disk limits, overshoot, capture failure ownership, and successful-run cleanup proof |
| Example and browser matrix | Packaged profile app passes the local Chromium/Firefox/WebKit slice; external loopback and JavaScript-off forms pass | Bounded existing Hedron behavior and accessibility corpus on Linux |
| Package extension | Hedron validates versioned contribution objects or JSON-shaped metadata, with explicit marker loading and conflict/resource checks; sample-kit declares a core-only metadata record and optional FastAPI factory using hedron-core without importing flagship Hedron; a draft inventory names all 23 workspace packages | Maintainer review, absence/conflict/version matrix, and fleet import isolation remain |
| Freeze and release | API remains a Beta candidate; all 17 machine-gate rows remain Planned | Accepted exact contract, named maintainers, numeric budgets, v1.2 predecessor, and release evidence |

## Candidate API and ownership lock

Adopt the direct-Page design as the preferred candidate. Keep one function-scoped `hedron_ui`
factory, context-managed `from_app(importable_factory, config=...)` / `from_url(base_url)`,
`page`/`context`, `url`, `mark`/`region`, checkpoint/settle/event snapshots, narrow expected-HTTP
rules, and clean assertions. Native Playwright owns locators/actions/assertions. No `ui.get_by_*`
delegation, `ui.expect`, global idle, or standalone second host/browser lifecycle.

Use explicit root-conftest plugin loading; select an additive testing extra without base-import
side effects. New policy/scenario/schema/protocol surfaces are Beta candidates; existing stable
helpers remain Stable. Freeze final signatures/typing and registration only after probes/user
exercise. Config precedence is package defaults, project config, test marker, explicit session
arguments for Hedron-owned settings; security/capture ceilings intersect and cannot be loosened
by an unrelated marker. Upstream browser CLI/fixture options remain upstream-owned, with conflicts
reported before context creation.

The child owns the constructed app, registry, loop, overrides, DB resources, listener, and lifespan.
The parent owns deadlines, supervision, isolated artifact roots, and teardown reporting. Browser
driver/process reuse remains owned by pytest-playwright; each test leases isolated context state.
Factory config is bounded JSON-compatible synthetic input; live apps/closures/DB connections are
not serialized across the host boundary.

## W0 — Complete the empirical freeze

Resolve the following concrete probes. The local slice above covers only part of the managed-host
and browser-matrix probes; the remaining results are still open.

| Probe | Required result | Gate owner |
|---|---|---|
| Factory/child hosting | Spawned factory, child-bound port zero retained through serving, owned readiness after lifespan, route/static/root-path parity, startup error, graceful/forced shutdown, xdist isolation | HOST-130 |
| Upstream fixture composition | Preserve engine/headed/context/device/locale/JS options; one context-close/capture owner; setup/call/teardown failure; no monkey patches | PYTEST-130 / CONTRACT-130 |
| Observation coverage | Capture before action; fast/slow request; 204/abort; OOB and nested removal; stale target/epoch; missing event capability clearly unavailable | SETTLE-130 |
| Capture boundary | Structured-only canary corpus; synthetic native trace/screenshots; early flag conflicts; temporary-disk monitoring and declared overshoot/termination; partial-write/permission failures | ARTIFACT-130 / SECURITY-130 |
| API/user exercise | Compare direct Page with disposable thin delegation; record first-test setup/failure comprehension/typing; publish one selected API | FREEZE-130 / LOCATOR-130 |
| Dependency and matrix | Actual pytest/pytest-playwright/Playwright/Uvicorn/xdist bounds, Linux host matrix and browser revisions, core/base isolation | COMPAT-130 / PKG-130 |
| Resource baseline | Repeated cold/warm host/context, request-settle, bounded artifact and teardown/xdist measurements with named hardware and exact commands | PERF-130 |
| Satellite ownership | Every package disposition, one minimal public-use-case contribution, explicit loading, absence/conflict/version behavior | SATELLITE-130 |

The [contract ledger](../acceptance/ui-testing-contract-130.toml) and [package inventory](../acceptance/ui-testing-package-dispositions-130.toml)
are implementation records, not accepted release evidence. Budgets remain Unmeasured with no
numeric thresholds; replace them with measured/frozen values, exact commands/artifact paths, and
actual maintainers before FREEZE-130 can be Verified. The 1.2 release predecessor and detailed
scope freeze are separate conditions.

## W1 — Small managed host and browser core

Implement only the frozen flagship host and context integration first:

- The child binds literal loopback/port zero, retains its socket, and reports startup/lifespan-ready
  through a bounded session-owned channel; no reserve-close port race, public-page readiness probe,
  reload, multiple web workers, or orphan daemon thread.
- Test root-path/mount semantics with real URLs, static requests and actual ASGI scope; construct
  overrides and synthetic auth/DB state inside the test factory.
- Install test-only request/event listeners before navigation. Scope any correlation header/channel
  to the managed origin; never alter application authorization, response bodies, or status.
- Lease isolated contexts via the supported upstream fixture seam and preserve options explicitly.
  Close only owned leases; never stop borrowed session browser/driver fixtures.
- Dispose observers, finish capture, close page/context through its single owner, request graceful
  child stop, then bounded terminate/kill/join. Forced termination remains a failed cleanup outcome.
- External URL mode accepts a declared literal-loopback origin, retains caller server ownership,
  and marks lifespan/server-exception facts unavailable.

**Exit:** HOST-130/CONTRACT-130 vertical evidence passes for the selected managed path, including
startup failure and timeout teardown. This does not require W5 satellite breadth.

## W2 — Checkpoint, errors, and the first end-to-end slice

Implement the smallest event ring and automatic clean checks needed to prove the profile form.
Checkpoint before the action; require an observed matching request start; consume response and
applicable swap/settle phases by target/epoch/generation. A 204 or cancellation has no required swap.
Unsupported readiness needs explicit Playwright assertions; do not change production assets.

Unexpected server/page/crash/console-error, HTTP 4xx/5xx, required-resource failures, or unexpected
blocked traffic fail automatically on context exit/finalization. Permit narrow expected-HTTP
contexts with method/path/status/count/checkpoint and reject unused expectations. Intentional
validation/denial UI remains testable; matching a 422 never ignores an unrelated JS/server error.
Exception summaries omit raw messages/locals by default.

**Required slice, before breadth work:**

1. Start a synthetic app with real lifespan/static/root-path support.
2. Navigate and fill by native role/label.
3. Declare an expected invalid response; verify inline error, focus, and announcement.
4. Checkpoint and submit valid data; settle the matching request and assert visible success.
5. Inject one deliberate server/browser/settle failure and retain structured diagnostic evidence.
6. Prove failure/timeout does not leak the child, context, listener, overrides, or temporary roots.

Run in Chromium first. The early slice is partial gate evidence, not a phase release or a reason
to skip the eventual three-browser corpus.

## W3 — Artifacts and pytest hardening

Implement a versioned structured failure manifest, bounded event/exception summaries, capability/
availability markers, environment/provenance, deterministic safe paths, atomic writes, and failure
phase. Preserve the original exception and append capture/teardown failures. Resource-policy
breaches and a missing required artifact do not become successful omissions.

Default structured capture records no raw trace, DOM, screenshot, video, HAR, bodies, header/cookie/
storage/form/URL values, arbitrary console text, or exception locals/messages. Canary scans validate
this profile. Synthetic capture is explicit: record native traces during execution if enabled,
retain failed-test captures, delete successful private temporaries, and label captures unredacted.
Do not promise trace archive redaction or capture-before-failure retroactively.

Integrate upstream trace/screenshot/video/output options before creating a context. Reject flags
that bypass the selected capture ceiling; one owner writes capture output. Freeze resource limits
with observed monitoring granularity and bounded overshoot for native artifacts; a final-size check
alone cannot establish a hard maximum during recording.

Use a function/session/xdist-aware artifact path with retry/phase identity. Required release runs
fail on missing binaries or unexpected skips. Collection can succeed without browser binaries;
base tests and unselected browser tests must not start a host/browser. Central activation is
explicit, and adding a satellite cannot alter collection or options. Reruns cannot erase earlier
failed-attempt evidence.

**Exit:** ERROR-130, ARTIFACT-130, PYTEST-130, and SECURITY-130 pass their declared core corpus;
timing/resource evidence remains bound to the frozen measurement plan.

## W4 — Bounded behavior, compatibility, and access corpus

Reuse the existing 1.1 reference flows and a selected browser subset rather than migrate every
historical test. Required families are page/native navigation; fragment/OOB/history; validation/
CSRF/auth; local/request/combined; one admitted specialist lifecycle; synthetic upload/download;
current polling/action terminal/cancel/stale behavior; no-JS/required-asset fallback; focus/keyboard/
announcements and mode/viewport checks; deliberate failures.

Run the bounded integration corpus on Chromium, Firefox, WebKit at a pinned Linux integration
runtime. Check default-build CPython 3.11–3.14 for host/import/package compatibility. Freeze exact
minimum/maximum upstream dependency rows and any risk-based Python/browser intersections.
macOS/Windows and managed adapter launchers remain pilot/Deferred unless admitted separately with
evidence; external loopback behavior is the portable adapter path.

Capture axe version/scope/incomplete/error provenance; automated results do not close human AT
obligations. Reject runtime-instrumentation requirements and keep no-JS semantics observable through
native Playwright. Preserve stable test signatures/imports, and baseline current defaults.

**Exit:** LOCATOR-130, SETTLE-130, BEHAVIOR-130, A11Y-130, COMPAT-130 and relevant assurance rows
have a complete declared matrix. Missing capability is explicit, not fabricated settled evidence.

## W5 — Minimal satellite proof and downstream handoff

Inventory all 23 current workspace members and reconcile actual release/optional membership at
freeze. Assign a machine-readable module/facade/host-provider/protocol-provider/testing-product/
private/non-fit disposition. Do not require public modules for all packages.

Prove one specialist contribution through explicitly loaded v1 metadata: package id/version,
schema ranges, capability names, bounded synthetic event/assertion summaries, declared fixture
resources, and conflict rules. Reject duplicate session/host/locator/artifact/error ownership.
Executable test hooks are trusted application test code, not a security sandbox. Host-launcher
extensions and broad hooks remain optional. Preserve stable flagship imports and optional-package
isolation; packaged public resources cannot be loaded from private repository tests paths.

Handoff only the checkpoint/event schema, declared capability availability, clean/error rules,
context isolation, and fixture extension seams to phases 1.4–1.7. Provide future scenario recipes:

| Consumer | What 1.3 supplies | What remains downstream-owned |
|---|---|---|
| 1.4 polling | Bounded request observations, isolated pages, upstream clock/event controls | Actual hidden-tab/viewport/backoff/terminal scheduling |
| 1.5 loading | Request/query observation supplied by synthetic app, stable region lookup | Viewport activation, deferred preparation and assets |
| 1.6 timing | Controlled server response order, checkpoint/epoch facts, semantic controls | Debounce, IME, latest-result and submit/validation runtime policies |
| 1.7 forms | Controlled save outcomes, native form assertions, response-loss fixtures | Dirty/save revisions, guards, unknown-save reconciliation |

Do not claim a virtual clock proves genuine OS background-tab suspension. Future visibility tests
need real browser/lifecycle evidence at their owning phase. The harness observes current behavior;
it does not implement these features or invent their production events.

**Exit:** SATELLITE-130 is Verified for the complete disposition inventory and minimal admitted
contribution, with absence/disabled/version/conflict/fleet install evidence. This work does not
block the earlier flagship vertical slice.

## W6 — Packaging, documentation, and release

Ship one synthetic importable test factory and one scaffold browser example. Teach render/
AppScenario/browser selection, explicit plugin activation, browser installation, direct Page usage,
expected failure, checkpoint settling, local debugging, capture profiles, and cleanup limitations.
Browser testgen and testing doctor remain optional.

Verify clean base/browser/testing-extra wheels/sdists, typing and optional-import boundaries,
upstream plugin options, CI entry/selected tests, immutable artifacts and versions. Preserve existing
scaffolds unless a user chooses generation; retain browser.py aliases and stable exports.

Opt-out is removal of the explicit plugin/scenario while render/AppScenario/raw Playwright remain
available. A context failure cannot change app data semantics or clear an application's dirty state.
Record a clean install/upgrade/opt-out rehearsal; never treat removal of artifacts or disabling clean
checks as rollback.

**Exit:** DOCS-130, PKG-130 and all other Required rows Verified; recorded 1.2 predecessor and
explicit release decision are required for RELEASE-130.

## Delivery order and checkpoints

```text
W0 empirical freeze
  -> W1 managed host/context
  -> W2 secured profile + intentional failure in Chromium
  -> W3 diagnostics/capture/pytest hardening
  -> W4 bounded behavior and three-browser/compatibility corpus
  -> W5 minimal satellite proof (can overlap W4 after protocol freeze)
  -> W6 release closure
```

| Candidate | Required result |
|---|---|
| `1.3a0` | Empirical freeze, selected API, source inventory, matrices, actual maintainers, schema and measured limits |
| `1.3a1` | W1/W2 flagship slice and bounded structured evidence; no satellite breadth prerequisite |
| `1.3b1` | W3–W5, capture boundaries, bounded three-browser/host corpus, minimal satellite conformance |
| `1.3rc1` | Clean packages/docs/upgrade/opt-out, predecessor evidence, every non-release gate Verified |

## Stop conditions

Do not enter implementation with unmeasured/unowned required budgets or unresolved host/context/
capture/settle authority. Do not promote a phase whose Required rows skip, lose failures, leak owned
resources, dump confidential captures, claim unavailable facts, alter base imports/defaults, or
require production instrumentation. The [acceptance packet](../acceptance/RELEASE_1_3.md) keeps the
17 gate ids and their precise descriptions; a documented prototype alone cannot verify them.
