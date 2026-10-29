# What’s next

Hedron `v1.2.0` is verified and published on PyPI. See
[Current release and support](current-release.md) for the exact channel status.

There is no committed 1.3 calendar or commercial SLA. The maintainer roadmap contains a proposed
1.X sequence, but these are planning candidates rather than release promises. The 1.2 Python
baseline is published. Future work must preserve the stable inventory and pass the same evidence-driven compatibility,
security, accessibility, packaging, and migration review used for the 1.0 cut.

## Shipped in 1.1

- Canonical `@app.page`, `@app.view`, and `@app.action` authoring roles.
- Static 0.67 migration diagnostics and conservative source migration tooling.
- A frozen stable inventory with SemVer compatibility protection.
- One explicit HTMX/Alpine/Web Component authority boundary.
- Stable `hedron-core`, `hedron`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`
  platform; Beta satellites, including `hedron-posit`, remain outside that boundary;
  `hedron-workbench` was removed.
- Python 3.10–3.14, FastAPI, Flask, Django, HDJ, browser, security, and package evidence.
- Polling as the Supported production fallback for asynchronous status.

## Proposed 1.X sequence

These are planning candidates, not release promises. The sequence starts with open
enhancements, then the published Python support transition, adoption confidence, four focused interaction
improvements, and later runtime/ecosystem expansion. The October 28, 2026 planning revision keeps
1.3 testing intact, inserts 1.4–1.7, and moves the former 1.4–1.9 themes to 1.8–1.13.
Later evaluation phases can end in promotion, continued experimentation, or non-admission:

| Phase | Theme | Primary question |
|---|---|---|
| **1.1** | Open enhancement completion and complementary application features | **Shipped in `v1.1.1`; complete application flows are supported** |
| **1.2** | Python 3.11+ support and typing baseline | **Published** (`v1.2.0`) |
| **1.3** | First-class UI testing and adoption confidence | Candidate implementation; required freeze and release evidence remain open |
| **1.4** | Visibility-aware polling | Can hidden/offscreen and failing status regions avoid unnecessary requests? |
| **1.5** | Viewport and on-demand loading | Can expensive regions defer queries and rendering until needed? |
| **1.6** | Typed input timing and request policies | Can search/validation issue fewer requests and keep the newest result correct? |
| **1.7** | Dirty-form and confirmed-save integration | Can forms protect newer edits and reconcile uncertain saves? |
| **1.8** | Production async and durable workflows | Is anything beyond polling ready for production? |
| **1.9** | Inclusive and international UX | Can the stable surface work for more users and locales? |
| **1.10** | Visualization and media graduation | Which optional adapters meet the first-party contract? |
| **1.11** | Stateful browser composition | Can partial updates retain local state safely? |
| **1.12** | Controlled ecosystem expansion | Which advanced integrations have a trustworthy operating model? |
| **1.13** | Evidence-gated large-application build scalability | Can large applications rebuild quickly while preserving reproducible output? |

See the [full 1.X planning sequence](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md#proposed-1x-sequence)
for scope and shared entry/exit policy.

### Shipped 1.1 focus

Phase 1.1 implements all **20 open enhancement requests** inventoried on 2026-09-18, including
unlabeled identity and pagination requests. Scope covers external identity/presentation hooks,
server-side pagination, trusted interaction error sinks, app-aware sealed builds, Posit URLs,
guided forms and write-only secrets, unsaved guards, structured validation/help, Dialog/elevation
parity, refined native shell/Brand/ProcessFlow/color-mode presentation, and computed-style checks.

Required complementary work makes those features compose: authorized collection states and URL
restoration, coherent form commit/reset and focus recovery, shared shell geometry, and asset
provenance. One packaged reference flow proves the combined result using existing tests. The
future managed browser harness follows in 1.3. See the
[issue inventory and implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/OPEN_ENHANCEMENTS_1_1.md)
and [acceptance plan](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_1_1.md).
The implementation and release evidence are recorded in the linked packet.

### Implemented 1.2 focus: Python 3.11+ support

Python 3.10 has reached end of security support and will receive no further CPython security fixes.
The 1.2.0 release raises the minimum supported version to CPython 3.11 across all maintained
packages and generated applications, with 3.11–3.14 as the target matrix. Package versions and
requirements, CI/release matrices, native wheel selectors, and release tooling now target this
train. BasedPyright targets 3.11 in `all` mode; Ruff targets `py311`. `Self` and `NotRequired` now
come from the standard library; `typing_extensions` remains a direct dependency for newer
`override` and `TypeIs` forms. Stdlib enum/TOML APIs replace the 3.10 fallbacks.

The repository changes are implemented under accepted decision D-120 and published in 1.2.0. The
1.1.3 release metadata remains historical; its Python 3.10 claim does not provide security fixes
for the EOL interpreter. See
[RFC-0099](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0099-PYTHON-311-BASELINE.md),
the [implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PYTHON_311_1_2.md),
and the [acceptance plan](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_1_2.md).
No 1.1 support-window extension is implied.

### Proposed 1.3 focus: first-class UI testing

The refined candidate preserves render tests and AppScenario, then adds an optional testing extra
with explicit pytest-plugin activation and direct Playwright Page/Locator/expect usage. A managed
ASGI test-app factory runs in an isolated child; caller-managed literal-loopback URLs remain the
portable host path. Request-scoped checkpoints avoid missing fast interactions or waiting on
unrelated polling, and fixture teardown detects unexpected failures automatically.

Structured diagnostics are the default. Screenshots/DOM/native traces require an explicit
synthetic-data profile and are labeled unredacted; trace retention on failure still requires
recording during the test. The first secured-form/intentional-failure slice precedes satellite
breadth. All packages get dispositions, with one minimal useful contribution required rather than
new public testing modules throughout the fleet. New surfaces are Beta candidates.

The release predecessor is 1.2; the 1.0 Stable testing inventory remains the compatibility baseline.
All 17 gates stay Planned pending real host/context/capture/settle probes, exact dependency/browser
matrices and measured budgets. See
[RFC-0097](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md)
and the [acceptance plan](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_1_3.md).
Phase 1.3 supplies test capabilities without implementing the runtime features in 1.4–1.7.

### Proposed 1.4–1.7 interaction improvements

- **1.4 — Poll only when useful:** opt-in hidden-tab/viewport eligibility, bounded jitter/backoff,
  one refresh on return, and terminal-job stopping over existing HTMX polling.
- **1.5 — Load when needed:** immediate, viewport, or user activation for Lazy regions, including
  deferring expensive data preparation, accessible placeholders, recovery, and an ordinary URL.
- **1.6 — Declare request timing:** typed debounce/throttle/minimum-length and blur/change policies
  that compile to existing transport; generation checks protect newer results and submitted values.
- **1.7 — Protect edits through saving:** extend existing guards with dirty/validated/submitted/
  committed revisions, keep edits made during save dirty, and reconcile response-loss uncertainty.

The [interaction efficiency RFC](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md)
links each phase's implementation and acceptance packets. All gates are Planned; candidate
policies are opt-in Beta, current defaults remain compatible, and no runtime implementation or
availability is claimed. General morphing and durable draft/offline mutation queues are excluded.

### Proposed 1.8–1.13 outcomes

- **1.8 — Durable work:** submit an export, observe progress, cancel or retry under an explicit
  policy, and retrieve an authorized result across worker restarts. Polling remains the baseline;
  live observation graduates only for a proven deployment matrix.
- **1.9 — Inclusive flows:** evaluate forms, navigation, dialogs, data, and job status with people
  using assistive technology, then verify remediation. Exercise RTL, text expansion, and
  locale/timezone formatting in a complete reference flow.
- **1.10 — Visualization and media:** evaluate one optional adapter at a time through a usable
  analysis/export flow, with accessible alternatives, bounded data, controlled assets, and
  reliable cleanup. Each adapter receives its own maturity decision.
- **1.11 — State retention:** try one opt-in path that preserves declared focus, selection, or
  disclosure state across partial updates, with clear reset rules and ordinary replacement as
  the fallback. Server state remains authoritative.
- **1.12 — Ecosystem:** choose individual integrations with a clear maintenance and authorization
  model. Prove useful operations, denied access, failure recovery, isolation, and package
  compatibility before promoting a satellite or capability.
- **1.13 — Build feedback:** reproduce large-application build measurements, define a supported
  size ceiling, and optimize only demonstrated rebuild bottlenecks. Incremental output must match
  a fresh build; meeting the budgets can close the evaluation without a runtime change.

### How delivery is sequenced

Phase 1.1 is published. Phase 1.2's Python support implementation is in the candidate workspace;
its runtime and artifact evidence remains to be collected. Phase 1.3 owns the UI testing foundation,
followed by the 1.4–1.7 interaction improvements and the 1.8 durable workflow contract.
Human-evaluation preparation and build measurements can start in parallel. Visualization uses
the relevant accessibility evidence; state retention uses the job/interaction and focus contracts.
An integration depends only on the contracts it actually consumes, so unrelated satellite work
does not hold up a proven improvement. Maintenance fixes continue independently of feature phases.

Each phase moves through a scope freeze, one useful reference-app flow, hardening, and an explicit
release decision. Phases 1.1–1.7 have detailed acceptance packets; 1.1 is published, 1.2 is
implemented with release verification pending, and all 1.3–1.7 gates remain Planned. Phases 1.8–1.13 are proposals
whose APIs, support matrices, and measured budgets must be
settled before implementation.
Phase 1.1 requires the inventoried enhancements and their declared complements; moving a required
item needs a recorded scope amendment. Later phases may defer optional candidates while completing
their declared required scope.

## Deliberately not planned as defaults

- A required Node.js toolchain for ordinary Hedron applications.
- A client-side application store or virtual DOM as a second source of truth.
- Automatic plugin discovery in production without explicit risk acceptance.
- Explorer enabled by default in production.
- In-memory jobs or cache presented as multi-worker durable infrastructure.
- Hedron acting as an identity provider, ORM, or application authorization engine.
- Unqualified WCAG, SLA, LTS, or “all APIs are stable” claims.

## How future changes are accepted

1. Start from a documented adopter problem and identify the existing fallback.
2. Classify the proposed surface as stable, beta, experimental, internal, or deferred.
3. Prove compatibility with the 1.0 stable inventory and provide migration guidance for any
   changed beta/experimental contract.
4. Add security, accessibility, browser, performance, package, and rollback evidence in
   proportion to the claim.
5. Update [What’s ready](whats-ready.md), [Compatibility](../COMPATIBILITY.md), and the
   [release notes](release-notes.md) only after the evidence passes.

The long historical phase ledger remains available in
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md), but it is
not an adopter roadmap.
