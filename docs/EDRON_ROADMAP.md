---
status: verified
---

# Edron release roadmap

**Status:** Edron `1.0.1` implemented, verified, tagged, and published<br>
**Edron release line:** `1.0` canonical Hedron 1.0 adoption<br>
**Latest in-tree release:** Edron `1.0.1`; Hedron `>=1.0.0`<br>
**Latest published release:** Edron `1.0.1` on PyPI (`v1.0.1`)<br>
**Architecture:** [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Public API:** [Edron 1.0 API by task](api/EDRON_REFERENCE.md)<br>
**State and interaction:** [Edron 1.0 state and interaction](api/EDRON_STATE_INTERACTION.md)<br>
**Packaging:** [Edron 1.0 packaging](api/EDRON_PACKAGING.md)<br>
**Acceptance:** [Edron 0.3 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_003.md)

This is the release roadmap for the separately versioned `edron` distribution. It does not assign
Hedron release numbers, change the Hedron capability roadmap, authorize implementation, or claim
that a planned capability exists. Edron may consume a later compatible Hedron train, but Edron and
Hedron phase numbers do not need to match.

Edron `1.0` is the first release that directly adopts Hedron's canonical 1.0 interface. Historical
0.x phases remain immutable evidence for their original package trains.

## Phase summary

| Edron phase | Theme | Status |
|---|---|---|
| **0.0** | Design acceptance, reusable Hedron enablement, locks, fixtures, and implementation-entry evidence | **Implemented baseline** |
| **0.1** | Complete batteries-included class facade with native Hedron identity, HTMX/HTTP parity, base tables/charts/maps, optional adapters, styling, jobs, and tooling | **Implemented in-tree; Beta** |
| **0.2** | Authoring refinement, diagnostics, source-aware tooling, and evidence-driven vocabulary polish | **Implemented and verified in-tree; Beta** |
| **0.3** | Explicit data editing and data-workspace ergonomics over native Hedron data authorities | **Published** (`edron-v0.3.0`; Beta) |
| **0.4** | Visualization, map, media, and linked-data workflow depth with accessible server-first fallbacks | **Tagged** (`edron-v0.4.0`; publication pending) |
| **0.5** | Resource, state, durable-job, and operational workflow depth without owning application infrastructure | **Implemented in-tree; unreleased Beta** |
| **0.6** | Reusable Edron application composition and deliberate `hedron-*` capability promotion | **Tagged** (`edron-v0.6.0`; publication pending) |
| **0.7** | Streamlit migration assistance, codemods, examples, and adoption tooling | **Implemented in-tree; release evidence required** |
| **0.8** | Deployment profiles, host integration evidence, and production operations guidance | **Implemented and release-verified in-tree; publication pending** |
| **0.9** | Long-lived `0.x` compatibility, selected stable-tier promotion, performance, security, and accessibility consolidation on Hedron `0.67.0` | Implemented and release-verified in-tree; publication pending |
| **1.0** | Canonical Hedron 1.0 page/view/action/include adoption and removal of duplicate route-handle ownership | **Published Stable API** (`edron-v1.0.0`) |

Historical phases after `0.1` were directional themes until their contracts were accepted. A capability may
move, narrow, remain native-only, or be rejected during its design review. Patch releases fix and
harden an owning phase; they do not silently introduce the next phase's public surface.

## How Edron phases work

Edron phases are cumulative capability releases:

- phase `0.N` normally produces initial package release `0.N.0`;
- `0.N.x` releases maintain that phase and may add compatible evidence-backed fixes;
- every phase retains one native Hedron renderer, router, interaction catalog, state authority,
  style/asset system, job system, and security boundary;
- every new facade method must lower to an existing or separately accepted public native contract;
- a later phase cannot be used to excuse a missing Required `0.1` capability; and
- no phase number represents a calendar date or progress toward `1.0`.

Each release freezes its compatible Python and Hedron package train. Extras remain installation
shortcuts only: a directly installed compatible optional dependency activates the same adapter,
and Edron never installs packages at runtime.

## Phase 0.0 — design and native enablement

Phase `0.0` was the pre-release program. It published no Edron distribution. In the
implementation specification, this roadmap phase spans Stage 0 design and Stage 1 reusable Hedron
enablement; roadmap phases describe releases, while implementation stages describe work order.

Required outcomes:

- accept RFC-0094 and the public API, state/interaction, packaging, capability, implementation, and
  golden-application documents as one coherent design;
- deliver the five focused native workstreams (`HEDRON-WS-CLASS`, `HEDRON-WS-INTERACTIONS`,
  `HEDRON-WS-PROVENANCE`, `HEDRON-WS-JOBS`, and `HEDRON-WS-STYLING`) while resolving each
  constituent `UP-001` through `UP-011` row as Existing or Shipped;
- freeze the capability, package, public API, lowering, state/interaction, fixture, performance,
  security, and accessibility locks;
- implement reusable Hedron enablement in the owning Hedron packages under their own acceptance
  evidence; and
- record Decisions A and B before any `packages/edron` runtime implementation begins.

Exit is Decision B in the Edron acceptance packet. Completing design documents alone does not
authorize the Edron runtime.

## Phase 0.1 — complete initial facade

Phase `0.1` delivers the complete contract already frozen by the Edron `0.1` packet. It is not a
reduced preview that can defer Required features to later roadmap phases.

The release includes:

- `import edron as ed`, `App`, class-based `Page`, fragments, actions, typed dependencies, and fresh
  request-local page instances;
- explicit output, layout, safe input, coherent GET filter, Pydantic form, outcome, download,
  session, cache, and job vocabulary;
- exact projection to native Hedron screens, handles, bound references, feature bundles, routes,
  effects, styles, assets, diagnostics, HTTP responses, and HTMX behavior;
- ordinary HTTP and no-JavaScript fallbacks with equivalent authoritative meaning;
- base tables/dataframes, first-party charts, maps, safe Markdown, server tooling, and direct access
  to the installed native data editor without claiming an Edron editor method;
- Plotly, Altair, Matplotlib, pandas, Polars, PyArrow, and SQLAlchemy activation from compatible
  direct installations, with named Edron extras only as equivalent installation shortcuts;
- simple themes and variants plus full native recipes, scopes, registered CSS, and escape hatches;
  and
- `run`, `check`, `register`, `explain`, `doctor`, and style tooling with explicit static versus
  trusted-import boundaries.

Exit requires Decision C and every Required release gate Verified against built wheel and sdist
artifacts. No partial set may be published as Edron `0.1.0` while still described as the accepted
full contract.

## Phase 0.2 — authoring refinement and tooling

Phase `0.2` uses real `0.1` application feedback to improve clarity without introducing magical
execution behavior.

Candidate scope:

- clearer source-mapped diagnostics, editor/type-checker feedback, and bounded explanation views;
- scaffolds and teaching templates derived from the golden applications;
- evidence-driven naming and signature refinements under the `0.x` compatibility policy;
- evaluation of a secondary function-page convenience when it preserves fresh-instance ownership,
  exact native projection, typing, and source identity; and
- evaluation of safe explicit inheritance ergonomics for fragments/actions without implicit
  exposure or ambiguous registration.

This phase does not add `write`, whole-script reruns, Boolean mutation buttons, global output,
magic callback argument bags, or a global session dictionary.

## Phase 0.3 — data editing and workspace ergonomics

Phase `0.3` promotes a small, explicit subset of native data-workspace behavior into Edron.

The release includes:

- an Edron data-editor facade with explicit schema, typed edit intent, authorization, validation,
  concurrency/conflict, audit, accessibility, and ordinary-form fallback contracts are accepted;
- simpler native `DataSource` and `DataWorkspace` composition for common read/filter/edit flows;
- bounded large-table paging, selection, current-page export, and diagnostics; and
- verified pandas, Polars, PyArrow, and SQLAlchemy adapter ergonomics.

Edron does not become a database, ORM, transaction manager, repository, or durable-state owner.
Applications continue to own data authorization and persistence.

## Phase 0.4 — visualization and linked-data workflows

Phase `0.4` is now a refined implementation candidate, not an availability claim. It may begin
only after the native chart, map, media, asset, and interaction contracts below are verified in the
compatible Hedron train. Edron will add small authoring spellings and provenance only; the owning
native packages remain responsible for rendering, sanitization, assets, and browser behavior.

### Proposed contract

| Workstream | Candidate outcome | Native owner and required evidence |
|---|---|---|
| `VIS-04` presentation | A single explicit chart/map composition path that accepts a reviewed native spec or a bounded beginner form, preserves title/description metadata, and exposes the owning native projection for inspection | `hedron-charts` / `hedron-maps`; first-party and optional-adapter parity, payload limits, redaction, and package-pin tests |
| `LINK-04` selection links | Typed chart/map selections can submit only to a registered native filter or action handle; selection cardinality and payload size use the native limits; unknown fields, callbacks, and arbitrary URLs fail closed | `ChartInteraction`, map interaction contracts, native router/command/filter authorities; HTTP, HTMX, no-JavaScript, CSRF, authorization, and race evidence |
| `ALT-04` accessible fallback | Every interactive visualization has a server-rendered text/table or static-image alternative, a meaningful accessible name/description, keyboard-reachable controls, and an explicit offline/error representation | native visualization accessibility contracts; automated HTML/a11y checks, keyboard/forced-colors/reduced-motion coverage, and offline/browser fixtures |
| `MEDIA-04` export and media | Chart/map export and image/audio/video composition use opaque authorized references, safe media types, bounded downloads, captions/transcripts where applicable, and ordinary HTTP fallbacks | `hedron` media/download responses and `hedron-core` media/a11y surfaces; authorization, range/cache, filename, CSP, and no-path-disclosure tests |
| `ASSET-04` cross-cutting policy | Theme tokens, asset activation, CSP origins, explanation metadata, and source provenance are consistent across first-party and optional adapters; no adapter silently adds network access | native style/asset/security registries; projection, static-check, dependency, and ejection evidence |

The beginner-facing API remains deliberately small. The intended shape is an explicit visualization
method plus typed `selection=`, `alternative=`, and `export=` values, rather than implicit event
callbacks or a second Edron registry. Exact names and signatures are not frozen until the native
contract and acceptance packet are approved.

### Bounds and ownership

- Visualizations are server-owned projections. Edron never introduces a client-side chart, map,
  component, event, or state runtime.
- Selection values are untrusted input. They must be validated by native typed payloads, bounded by
  the owning interaction contract, and lowered to a registered filter/action; they must not invoke
  arbitrary Python callables or carry executable JavaScript.
- Data, authorization, filtering, persistence, transactions, download authorization, and durable
  media storage remain application-owned. A visualization may display only the rows/features the
  application has already authorized.
- First-party static/offline alternatives are required before browser enhancement is considered
  complete. Optional adapters may remain Experimental or unavailable when they cannot meet the same
  fallback, CSP, and accessibility contract.

### Entry and exit gates

Phase `0.4` implementation entry requires a dedicated acceptance packet that freezes the public
surface, native package pins, selection/download limits, supported adapter matrix, and security/a11y
fixtures. Release exit requires, at minimum:

1. native chart/map/media contracts are published and their Edron projections preserve object
   identity and source provenance;
2. chart and map selections pass typed HTTP, HTMX, no-JavaScript, authorization, CSRF, and
   concurrency tests with bounded payloads;
3. every supported visualization has a text/table or static/offline alternative and keyboard,
   forced-colors, reduced-motion, and failure-state evidence;
4. export/media paths pass authorization, range/cache, safe-filename, CSP, and redaction checks;
5. optional adapters remain lazy, directly-installed, version-pinned, and explicitly diagnosed;
   and
6. built wheel/sdist, documentation, upgrade fixtures, and the complete Edron 0.3 regression suite
   pass before a `0.4.0` tag is considered.

## Phase 0.5 — state, resources, and operational workflows

Phase `0.5` is implemented in-tree but remains pending publication. It began after the `0.4`
acceptance packet was closed; the native state, resource, job, and operations contracts below are
verified in the compatible Hedron train. Edron adds authoring ergonomics and diagnostics only;
native hosts remain responsible for lifetimes, persistence, transport, and production enforcement.

### Proposed contract

| Workstream | Candidate outcome | Native owner and required evidence |
|---|---|---|
| `RES-05` resource lifetimes | Explicit request/application resource declarations with sync and async setup/cleanup, deterministic teardown on success/error/cancellation, and test/deployment overrides; no implicit global resource cache | native dependency/lifespan and adapter DI contracts; cleanup ordering, exception, cancellation, override, and leak tests |
| `STATE-05` typed state and cache | Small typed session/cache spellings that declare owner, lifetime, sensitivity, version/expiry, scope partition, and invalidation; restart and multi-worker behavior is explicit | native session, cache, and durability authorities; cross-user/tenant isolation, expiry, migration, restart, and process-local diagnostics |
| `JOB-05` durable job workflows | `JobFlow` projection for bounded progress, cancellation, retry/idempotency, terminal result/download, and operator-safe diagnostics while preserving one authorized `JobScope` | native `JobBackend`/`TaskFlow`; payload/result limits, authorization, replay, race, cancellation, retention, and no-enumeration evidence |
| `LIVE-05` progressive observation | Optional SSE/WebSocket observation over the native status handle; polling, ordinary HTTP, and no-JavaScript remain canonical and semantically equivalent | native live transport and response/HTMX contracts; reconnect/backoff, stale generations, disconnect, rate/budget, CSP, and extension-absent browser fixtures |
| `OPS-05` deployment diagnostics | Deterministic `check`/`doctor` facts for process-local state, durable backend readiness, worker topology, graceful shutdown, and configured limits, with redacted output and fail-closed production findings | `hedron-core` production gates plus Flask/Django/ASGI adapters; multi-worker, restart, secret-redaction, import isolation, and operator remediation evidence |

The beginner-facing API remains deliberately small. The intended shape is explicit
`dependency=`/resource declarations, typed state/cache values, and a `JobFlow` policy object rather
than a global `session_state` dictionary, hidden persistence, magic reruns, or an Edron-owned worker
runtime. Exact names and signatures are not frozen until the native contracts and acceptance packet
are approved.

### Bounds and ownership

- Every resource has one declared lifetime and one cleanup owner. Cleanup runs at most once, is
  ordered by the native host, and never leaves an object reachable from a detached task or page
  instance after request completion.
- State and cache keys are typed, scope-partitioned, and bounded. Session values never contain
  dependencies, open connections, job results, secrets, or unbounded collections; cache loss may
  affect performance only and never becomes durable truth.
- Job input, progress, status, result, retry, retention, and poll budgets are frozen numerically in
  the acceptance packet. Progress and diagnostics are value-redacted; job IDs are opaque and never
  authorize observation without the native scope check.
- Polling/no-JavaScript behavior is the correctness baseline. Live transports are opt-in native
  enhancements and must fall back on unsupported hosts, reconnect exhaustion, stale generations,
  or policy denial without changing authoritative state.
- Applications own databases, repositories, transactions, object/media storage, queues, schedulers,
  workers, distributed caches, authorization, and audit records. Edron never provisions or selects
  those services at runtime.

### Entry and exit gates

Phase `0.5` implementation entry requires a dedicated acceptance packet that freezes the public
surface, compatible native package pins, supported resource/session/cache/job backends, live
transport matrix, numeric budgets, and operator redaction fixtures. Release exit requires, at
minimum:

1. sync/async resource setup, teardown, cancellation, error ordering, and explicit overrides pass
   under every supported host;
2. typed session/cache scope, expiry, invalidation, migration, restart, and multi-worker tests
   prove no cross-user or cross-tenant leakage and diagnose process-local claims;
3. durable job progress, cancel, retry/idempotency, result/download, retention, and operator
   surfaces pass authorization, CSRF, race, replay, no-enumeration, and no-JavaScript evidence;
4. optional SSE/WebSocket observation passes reconnect, stale-generation, disconnect, rate, CSP,
   and browser tests while polling and ordinary HTTP remain equivalent without the transport;
5. deployment checks fail closed for non-durable production backends and produce deterministic,
   redacted remediation facts without importing or executing application code;
6. optional adapters remain lazy, directly installed, version-pinned, and explicitly diagnosed;
   and
7. built wheel/sdist, documentation, upgrade fixtures, and the complete Edron `0.4` regression
   suite pass before an `edron-v0.5.0` tag is considered.

The phase does not add a worker, scheduler, queue, database, object store, distributed cache,
global resource registry, implicit rerun model, or client-side state authority.

## Phase 0.6 — reusable composition and package depth

Phase `0.6` is implemented in-tree and remains unreleased. It makes larger
Edron applications easier to organize while preserving one native renderer, router, catalog,
lifespan, security boundary, and asset authority. The phase may begin only after the `0.5`
acceptance packet is closed and the native composition contracts below are accepted in the
compatible Hedron train.

### Implemented contract

| Workstream | Candidate outcome | Native owner and required evidence |
|---|---|---|
| `COMP-06` package composition | A reusable Edron feature package declares pages, fragments, actions, dependencies, assets, and projections; registration compiles atomically into native `FeatureBundle`/catalog entries with deterministic duplicate detection | native bundle/catalog and app registration contracts; import isolation, duplicate IDs, partial-registration rollback, and package-boundary fixtures |
| `NAV-06` navigation and layout | Typed navigation targets and shared layouts compose over native routes/screens, preserve ordinary HTTP and no-JavaScript fallbacks, and reject unregistered or cross-application targets | native router, screen, link, and fallback contracts; authorization, root-path, stale-target, accessibility, and cross-app isolation evidence |
| `PROMO-06` capability promotion | A small reviewed allowlist promotes selected mature `hedron-*` capabilities into Edron spellings with version/train checks, explicit provenance, and an ejection path to the native API | native package manifests, capability registry, and compatibility contracts; absent/old/new package, provenance, and ejection fixtures |
| `EVID-06` mixed-surface verification | Applications can inspect Edron/native lowering, compare route/catalog/asset manifests, and run bounded conformance checks without importing arbitrary application callbacks | native explanation, manifest, testing, and asset contracts; redaction, deterministic fingerprints, import isolation, and budget evidence |
| `PKG-06` package and asset depth | Feature packages ship typed metadata, documentation, upgrade notes, and deduplicated assets without copying native packages or creating a second registry | native packaging and asset pipeline contracts; wheel/sdist, static path, asset collision, lazy optional dependency, and upgrade fixtures |

The beginner-facing API remains explicit package composition, typed navigation/layout declarations,
and reviewed capability helpers. Every declaration lowers to a native registration or projection;
package imports never execute application callbacks, and diagnostics report provenance without
secrets, source payloads, or filesystem paths.

### Bounds and ownership

- A feature package has one application owner and one registration transaction. Failed validation
  leaves no partially registered route, catalog entry, dependency, or asset.
- Logical IDs, route names, asset names, and navigation targets are bounded, deterministic, and
  unique within an application. A collision fails closed with the owning package and source
  provenance identified.
- Shared layouts are composition only: they do not own sessions, resources, queues, workers,
  authorization, persistence, or a second render tree. Navigation never bypasses native scope or
  security checks.
- Promoted capabilities remain optional and directly installed. Edron checks the native package
  manifest and compatible train before import, exposes the native escape hatch, and never scans or
  re-exports arbitrary installed plugins.
- Explanations, manifests, and conformance reports are bounded and redacted. Asset deduplication
  may reduce bytes but cannot change cache, CSP, route, or authorization semantics.

### Entry and exit gates

Phase `0.6` implementation entry requires the dedicated [Edron 0.6 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_006.md)
and machine-readable [phase gates](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/edron-phase06.toml). Release exit requires, at
minimum:

1. package composition is atomic, import-isolated, provenance-preserving, and duplicate-safe;
2. typed navigation and shared layouts preserve authorized native routes, accessibility,
   root-path behavior, ordinary HTTP, and no-JavaScript fallbacks;
3. promoted capabilities pass absent/present/version/train checks, remain lazy, and provide a
   documented native ejection path;
4. mixed Edron/native explanations, manifests, fingerprints, and conformance checks are bounded,
   deterministic, redacted, and callback-free;
5. package wheels/sdists, metadata, documentation, optional dependencies, and deduplicated assets
   pass upgrade and collision fixtures; and
6. the complete Edron `0.5` regression suite plus the new phase `0.6` contract suite pass before
   an `edron-v0.6.0` tag is considered.

The phase does not add a plugin marketplace, arbitrary plugin discovery, automatic package
re-exports, a global registry, a second renderer/router/catalog/asset system, hidden navigation
state, or a new worker/deployment runtime.

## Phase 0.7 — migration and adoption tooling

Phase `0.7` is implemented in-tree; release availability still requires the acceptance gates below. It may begin only
after the `0.6` acceptance packet is closed and the reviewable migration contracts from
[RFC-0061](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0061-STREAMLIT-AST-MIGRATOR.md) are reconciled with Edron's class, request,
state, package, and capability vocabulary. Edron is an output target for migration assistance;
the existing Hedron migrator remains a separate tool and authority.

### Proposed contract

| Workstream | Candidate outcome | Native owner and required evidence |
|---|---|---|
| `ANALYZE-07` static source analysis | A bounded AST analyzer accepts a Streamlit entrypoint or project, resolves only local modules beneath an explicit project root, and never imports, executes, opens application paths, or contacts a network | `hedron-core` diagnostics and source-location contracts; file/byte/node/import/time limits, symlink containment, malformed-source, and no-execution fixtures |
| `MAP-07` migration catalog | A versioned, inspectable mapping catalog translates a locked Streamlit subset to Edron pages, layouts, controls, fragments, actions, data, charts, and media with `translated`, `scaffolded`, `report_only`, or `unsupported` dispositions | RFC-0061 mapping registry and Edron public API; no-drop coverage, version-boundary, alias, dynamic-symbol, and unknown-API evidence |
| `GENERATE-07` Edron scaffold | `edron migrate streamlit SOURCE --out DIR` creates a fresh Edron project with bounded pins, secure defaults, tests, `REVIEW.md`, report JSON, and source maps; generated code is reviewable and never overwrites source or a non-empty destination | Edron scaffolds and native package metadata; atomic output, path redaction, secret absence, import isolation, wheel/sdist, and clean-consumer fixtures |
| `OWNERSHIP-07` state and side-effect plan | Reports identify widget dependencies, callbacks, rerun/stop flow, cache/resource use, files, secrets, auth, custom components, and writes, then recommend URL, request/form, session, cache, resource, browser, or durable owners | Edron state/interaction and native security/lifecycle contracts; control-flow, mutation, authorization, tenancy, and explicit-manual-decision fixtures |
| `CODEMOD-07` safe codemods | Opt-in codemods apply only accepted, semantics-preserving Edron API changes to generated or Edron-owned source, with a preview/diff, idempotency, source maps, and refusal on ambiguity | Python AST/CST boundary and Edron compatibility policy; no-source-mutation, formatting, comments, import, idempotency, and unsafe-pattern fixtures |
| `REPORT-07` adoption reports | Text, deterministic JSON, and shared SARIF reports summarize coverage, unresolved decisions, dependencies, risk, and next actions; thresholds are usable in local development and CI | Native diagnostics/SARIF adapter; stable codes, redaction, bounded output, schema/version negotiation, and terminal/Markdown injection tests |
| `EXAMPLES-07` migration teaching kit | Side-by-side Streamlit, Edron, and native Hedron examples cover a read-only dashboard, validated filters, an explicit write, data workspace, and a long-running job, each with outcome tests and a cutover note | Edron golden applications and migration guide; fixture parity, accessibility, no-JavaScript, HTTP, and deployment-review evidence |

The beginner-facing workflow is deliberately two-stage: analyze first, then generate into a new
directory. The report is the authority on what was translated and what still needs a developer
decision. Edron may reuse the RFC-0061 migration IR and mapping evidence where compatible, but it
must not create a second analyzer, silently fork mapping semantics, or present a clean report as
behavioral equivalence.

### Supported first slice

The first Supported catalog is intentionally narrow:

- titles, headings, text, safe Markdown, metrics, ordinary tables, and bounded dataframes;
- columns, containers, sidebar, tabs, and expanders when semantic order is reviewable;
- simple select, multiselect, slider, checkbox, text, number, and date controls as validated GET
  inputs, with POST forms only where mutation evidence requires them;
- `st.form` and submit buttons as explicit Edron forms/actions with CSRF and validation review;
- statically declared pages/navigation and common first-party charts with accessible alternatives;
- direct mapping of framework-free calculations, Pydantic models, data access, and domain services;
  and
- report-only findings for dynamic imports, custom components, raw HTML, uploads/downloads,
  authentication, secrets, external services, rerun/stop flow, and ambiguous state ownership.

No mapping may infer authorization, turn arbitrary HTML trusted, copy `st.session_state` into one
global dictionary, or claim that a cache is durable state. A generated action with unresolved
mutation findings must be unreachable or fail closed until reviewed.

### Bounds and ownership

- The source is untrusted text. Analysis is bounded by file count, bytes, AST nodes, import depth,
  recursion depth, and elapsed time; local resolution cannot escape the project root through paths
  or symlinks.
- The source application is read-only. Generation writes only to an absent or empty destination
  through an atomic staging process and never copies secrets, absolute machine paths, or source
  files into generated output.
- Every recognized call receives a disposition and stable source span. Unsupported or ambiguous
  constructs produce findings rather than speculative code or silent drops.
- Generated Edron code uses public APIs, explicit routes, request/form boundaries, safe defaults,
  and the current compatible package train. It does not import Streamlit at runtime or add a
  compatibility shim, rerun engine, second state store, or client runtime.
- Codemods are opt-in and reviewable. They may change only accepted Edron-owned syntax; ambiguous,
  dynamic, or framework-semantic changes are refused with a source-mapped finding.
- Applications retain ownership of domain logic, authorization, tenancy, persistence, transactions,
  secrets, files, external services, deployment, and cutover. Migration output is a proposal, not a
  deployment authorization or equivalence certificate.

### Entry and exit gates

Phase `0.7` implementation entry requires the [Edron 0.7 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_007.md)
and [machine-readable phase gates](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/edron-phase07.toml), plus closure of the `0.6`
release evidence. Release exit requires, at minimum:

1. bounded analysis proves no source import/execution, no path/network access, project-root
   containment, deterministic limits, and actionable refusal diagnostics;
2. the versioned mapping catalog covers every recognized call with no-drop dispositions and agrees
   with the maintained Streamlit migration matrix and RFC-0061 compatibility window;
3. generated Edron projects use public APIs and secure pins, contain report/source-map/review/test
   artifacts, refuse overwrite, preserve source bytes, and contain no Streamlit runtime dependency;
4. state, side-effect, dependency, styling, accessibility, and hosting decisions are surfaced as
   stable findings rather than hidden in generated code;
5. codemods provide preview/diff, idempotency, source provenance, and fail closed on ambiguity or
   unsafe framework semantics;
6. text/JSON/SARIF reports are redacted, bounded, schema-versioned, deterministic, and thresholdable
   in CI;
7. side-by-side examples pass outcome, HTTP, accessibility, no-JavaScript, package, and upgrade
   fixtures; and
8. the complete Edron `0.6` regression suite plus the phase `0.7` migration, adversarial, and clean
   consumer suites pass before an `edron-v0.7.0` tag is considered.

The phase does not promise one-for-one Streamlit behavior, accept `import edron as st`, emulate
Streamlit reruns, auto-extract `domain.py`, execute an AI converter, rewrite in place, or hide
incompatible state, mutation, security, accessibility, or deployment semantics.

## Phase 0.8 — deployment and host integration

Phase `0.8` is implemented and release-verified in-tree; publication remains pending. Its release
contract is Edron `0.8.0` on Hedron `0.66.2` (`>=0.66.2,<0.67`).
It makes an Edron application reviewable and repeatable at the deployment boundary after the `0.7`
migration and adoption contracts are closed. The phase standardizes evidence and diagnostics around
the existing ASGI application; it does not turn Edron into a process supervisor, cloud provisioner,
or host abstraction layer.

### Proposed contract

| Workstream | Candidate outcome | Native owner and required evidence |
|---|---|---|
| `PROFILE-08` deployment profiles | A small versioned profile vocabulary covers local development, single-process production, reverse-proxy/root-path, container/orchestrated, and approved Workbench/Posit handoffs; each profile records bind, mount, static, worker, state, job, and trust assumptions | `hedron-core`, `hedron-posit`, and Edron launcher/CLI contracts; profile schema, precedence, unknown-field, loopback/external-bind, and deterministic-diagnostics fixtures |
| `EDGE-08` proxy and asset boundary | Profile-aware URL, redirect, cookie, CSRF, CSP, static-asset, build-manifest, compression, and cache guidance remains correct under a mounted path and a real proxy; invalid or missing production manifests fail closed | native routing, security, asset, and response authorities; root-path, forwarded-header, cookie-path, cache, integrity, stale-asset, and no-JavaScript HTTP/HTMX evidence |
| `HOST-08` host integration matrix | Edron's ASGI flagship and any directly supported Hedron host handoff have explicit Supported, Tooling, Experimental, or Deferred dispositions with version floors, launch order, limits, and ejection paths | `hedron` and `hedron-posit` host contracts; clean-process, import-order, mount, public-link, restart, worker, and package-pin matrices |
| `OPS-08` production diagnostics | `edron check`/`doctor` or the native equivalent reports effective configuration, readiness, graceful-shutdown, worker topology, durable-state/job assumptions, limits, and redacted remediation facts without importing arbitrary application code | native production gates and Edron diagnostics; fail-closed secret handling, multi-worker/restart, signal, timeout, health/readiness, and redaction evidence |
| `SUPPLY-08` release artifacts | Edron release artifacts include reproducible metadata sufficient to identify package versions, compatible Hedron train, wheel/sdist hashes, dependency licenses, SBOM/provenance records, and the exact verification commands; no runtime installation is required | package metadata and release-evidence contracts; clean wheel/sdist, offline install, dependency isolation, license, hash, and provenance fixtures |
| `UPGRADE-08` upgrade and recovery | A pinned-train upgrade guide covers preflight, manifest rebuild, schema/state compatibility, smoke checks, rollback boundaries, and air-gapped promotion; rollback never pretends to reverse application-owned data migrations | Edron compatibility policy and application-owned persistence boundary; two-version fixtures, failed-start recovery, asset-cache invalidation, migration refusal, and operator-runbook evidence |

The phase has three maturity lanes:

- **Required baseline:** ASGI deployment, explicit reverse-proxy/root-path behavior, production
  build-manifest enforcement, secure configuration diagnostics, ordinary HTTP/HTMX smoke paths,
  and package/artifact verification.
- **Conditional host support:** Workbench/Posit and other Hedron host handoffs may be Supported
  only when their native adapter supplies the lifecycle, URL, cookie, worker, and version evidence.
  Notebook preview and remote tooling remain tooling-grade or Experimental unless a separate host
  packet proves a production boundary.
- **Evaluation only:** Flask/Django Edron page-class parity, new process managers, cloud-specific
  provisioning, and non-ASGI authoring require a separately accepted native lifecycle and
  HTTP/HTMX parity contract. A research matrix or launcher recipe is not a support claim.

The beginner-facing workflow is deliberately inspectable: build the application assets, run the
profile-aware checks, deploy with the host's normal ASGI mechanism, and smoke-test the same routes
through the real proxy. Profiles describe and validate a deployment; they do not discover arbitrary
infrastructure, install packages, infer secrets, or silently select a worker, queue, database, or
public URL.

### Bounds and ownership

- Edron owns authoring, projection, diagnostics, and bounded release metadata. The ASGI server,
  reverse proxy, TLS termination, process supervisor, orchestrator, secrets manager, observability
  backend, database, object store, queue, and durable job backend remain application or platform
  owned.
- Every profile has one explicit source of truth for mount, external URL, static/build directory,
  worker mode, and state/job durability. Conflicting environment, CLI, and host values fail closed
  or produce a stable finding; they are never resolved from an untrusted `Host` or forwarded header.
- Production checks may inspect declared configuration and package metadata, but must not import or
  execute arbitrary application callbacks, contact external services, print secret-shaped values, or
  claim that a process-local resource/session/cache is durable.
- Root-path, cookies, CSRF, redirects, asset URLs, and HTMX requests are one native mounted-path
  contract. A host adapter cannot weaken authorization, CSP, trusted-proxy, safe-download,
  no-JavaScript, or error/fallback semantics.
- Multi-worker and restart guidance must state which features require shared native backends or
  sticky routing. Edron never silently upgrades process-local state, live transport, or job status
  into a distributed guarantee.
- Rollback covers application artifacts and package pins only. Data migrations, secrets rotation,
  external side effects, queued work, and user-owned files require an application runbook and are
  never reversed by Edron automatically.
- Supply-chain records are bounded and verifiable, but they do not certify a deployment, third-party
  dependency, cloud account, or application security posture.

### Entry and exit gates

Phase `0.8` implementation entry requires closure of the `0.7` release evidence, a dedicated
acceptance packet that freezes the supported profile/host matrix, compatible package pins, numeric
diagnostic and artifact budgets, and the required security/upgrade fixtures. Release exit requires,
at minimum:

1. every Required profile has deterministic precedence, explicit trust assumptions, versioned
   configuration, and actionable refusal diagnostics;
2. production builds fail closed for missing or invalid manifests, while mounted static assets,
   redirects, cookies, CSRF, CSP, cache behavior, ordinary HTTP, HTMX, and no-JavaScript fallbacks
   pass proxy fixtures;
3. the ASGI host and each conditionally Supported handoff pass clean-process, import-order,
   root-path, public-link, restart, worker, graceful-shutdown, and package-pin evidence;
4. `check`/`doctor` findings are bounded, deterministic, redacted, callback-free, and distinguish
   process-local from durable state/job claims, with health/readiness and remediation coverage;
5. wheel/sdist, offline-install, dependency-isolation, license, SBOM/provenance, hash, and exact
   verification-command artifacts are complete for the pinned Edron/Hedron train;
6. upgrade, failed-start, rollback, stale-asset, and application-owned migration boundaries are
   exercised in two-version fixtures and documented as an operator runbook;
7. every non-Required host or capability has an explicit maturity disposition, version boundary,
   fallback, and ejection path; and
8. the complete Edron `0.7` regression suite plus the phase `0.8` profile, proxy, host, artifact,
   security, and recovery suites pass before an `edron-v0.8.0` tag is considered.

The phase does not add a cloud deployment service, Docker/Kubernetes/Workbench operator, process
supervisor, runtime package installer, secret manager, distributed state/job backend, automatic
public-URL discovery, arbitrary forwarded-header trust, Flask/Django page-class parity, notebook
production hosting, or a new renderer, router, asset, security, or observability authority.

## Release 1.0 — canonical Hedron 1.0 adoption

Edron 1.0 requires `hedron>=1.0.0,<2.0` and `hedron-data>=1.0.0,<2.0`. Its class-oriented
authoring vocabulary remains small, while native registration is now exclusively owned by
Hedron's canonical `page`, `view`, `action`, and `include` roles. Edron no longer constructs
parallel view/action handles or synchronizes Hedron's private root router.

The 1.0 release retains the native interaction, outcome, browser-plan, lifecycle, component,
style, data, cache, resource, TaskFlow, and specialist host contracts already admitted by 0.9,
but exercises them against Hedron 1.0 as the minimum runtime. Scaffolds and Streamlit migration
output declare the same bounded 1.x requirements. See
[EDRON_100.md](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_100.md) and
[edron-100.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/edron-100.toml).

## Phase 0.9 — long-lived `0.x` consolidation on Hedron `0.67.0`

Phase `0.9` is the Edron consolidation and compatibility phase on the Hedron `0.67.0` train. Its
release target is Edron `0.9.1` with `hedron>=0.67.0,<2.0` and a baseline lockfile that resolves
`hedron==0.67.0` (including the coordinated `hedron-core` and `hedron-data` 0.67.0 packages when
those capabilities are exercised). The same Edron 0.9 source and public contract must remain
forward-compatible with Hedron `1.0.0`; its compatibility fixture passes against the release
candidate. The 0.9.1 patch declares that verified range while retaining the 0.67.0 baseline
evidence train. Edron `0.8.x` remains pinned
to the Hedron `0.66.2` train; no Phase 0.9 planning change widens or retrofits the already released
0.8 contract. Phase 0.9 turns the accepted `0.1`–`0.8`
surface into a deliberately classified, measurable, and maintainable `0.x` contract. The
implementation is accepted in-tree; publication and the `edron-v0.9.1` tag remain maintainer-controlled.

The release must be built and tested from the Hedron `v0.67.0` baseline or an equivalent immutable
source/lock snapshot. A moving `main` checkout, an unbounded `hedron` requirement, or evidence
collected against Hedron `0.66.x` cannot satisfy the Phase 0.9 compatibility gate. The human packet
is [EDRON_009.md](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_009.md); its machine-readable gate lock is
[edron-phase09.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/edron-phase09.toml), and the transition fixture is
[upgrade-fixtures-09.md](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-09.md).

The phase has one governing rule: maturity is earned by evidence, not by age or usage. A capability
that cannot meet the phase contract remains `beta`, `experimental`, `deferred`, or
`application-owned`; it is not promoted merely to make the roadmap look complete.

### Implemented contract

The candidate contract is split into three release layers:

1. **Train boundary:** Edron `0.9.0` consumes Hedron `0.67.0`; clean installs, the workspace lock,
   built metadata, and all native identity fixtures must agree on that train. A second forward-
   compatibility matrix must run against Hedron `1.0.0` after it is released.
2. **Maturity boundary:** only the explicitly promoted beginner subset may become `stable`; every
   other surface keeps a visible `beta`, `experimental`, `deferred`, `internal`, or
   `application-owned` disposition.
3. **Maintenance boundary:** 0.9.x may fix or clarify the accepted contract, but cannot add a new
   authority or silently change a maturity, dependency, security, accessibility, or fallback claim.

### Hedron 0.67 feature integration

Hedron `0.67.0` is not only a dependency floor. It supplies the native browser and interaction
contracts that Edron 0.9 must consume when those capabilities are admitted. Edron remains a
beginner-facing facade over those authorities; it does not fork their registries, asset plans,
request lifecycle, component engines, or outcome algebra.

| Hedron 0.67 capability | Edron 0.9 candidate integration | Boundary and required proof |
|---|---|---|
| Demand-driven Alpine document feature plans | Edron components and interaction declarations contribute native feature demands; the page plan computes the initial and reachable-fragment closure and local assets | No page-level plugin lists, remote scripts, response-time registration, or feature-on assets when the capability is unused; prove CSP, integrity, fragment-subset, and feature-off fixtures |
| Closed `Interaction` forms (`local`, `request`, `combined`) | Edron's interaction helpers lower to the single Hedron interaction contract, preserving one request maximum and the ordinary HTTP fallback | Alpine may own disposable local presentation; HTMX/Hedron owns requests and server truth; prove invalid cross-lane combinations fail and exact fallback behavior remains usable |
| Role-indexed `Outcome` values | Edron action results and refresh helpers map to native success, refresh, patch, redirect, job, validation/conflict, and download outcomes where supported | Do not keep parallel response/update semantics or let a Boolean action hide mutation; prove status, target identity, authorization, and no-JavaScript parity |
| HTMX lifecycle and Alpine coordination | Edron deployment and page diagnostics expose native init, cleanup, swap, settle, history, focus, announcement, and stale-result facts through `explain`/`doctor` | One writer owns each state, focus, busy, and announcement concern; prove exactly-once cleanup, replacement/reset behavior, and redacted traces |
| Component-engine dispositions and accessible widgets | Common Edron controls use native HTML plus Alpine; charts, maps, data editors, and other specialist subsystems remain in their owning Web Component/package | No parallel `Alpine*` facade or copied widget runtime; every promoted widget needs keyboard/focus, semantic fallback, browser, provenance, and performance evidence |
| 0.67 warning and migration inventory | Edron diagnostics and generated examples surface Hedron compatibility warnings with the native code, replacement/disposition, and release window | Warnings are deterministic and actionable; Edron does not suppress native 0.67 warnings or promise 1.0 removals without a fixture |

The source of truth for these integrations is Hedron's [0.67 Alpine implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/ALPINE_INTEGRATION_067.md),
[HTMX/Alpine boundary](https://github.com/eddiethedean/hedron/blob/main/docs/api/HTMX_ALPINE_BOUNDARY_1_0.md), and [component-engine dispositions](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md).
The Edron candidate does not automatically promote every Hedron 0.67 widget: a provider-owned or
specialist capability remains native-only, optional, Progressive, Experimental, Deferred, or
application-owned until its Edron evidence is accepted.

#### Deprecated-feature exclusion

Edron 0.9 consumes only the canonical Hedron 0.67 paths. It must not import, emit, document as a
beginner path, or depend on any Hedron feature that 0.67 marks as a compatibility path with a
warning or a planned 1.0 removal. This includes the direct `hedron-disclose` path, duplicate
`hedron-elements` common-widget wrappers, direct `hedron-dialog`, `hedron-field-text`,
`hedron-field-choice`, `hedron-field-file`, and `hedron-action-async` compatibility paths, and
delegated common-widget controllers where the 0.67 inventory selects native plus Alpine.

Those paths may appear only in migration input, static findings, or a narrowly scoped warning
fixture. They must never be the implementation dependency, generated output, example authoring
path, browser asset requirement, or runtime fallback for Edron 0.9. The clean-surface gate is
separate from deprecation support: Edron may help an application identify and migrate an old path
without using that path itself.

| Workstream | Candidate outcome | Required evidence and owner |
|---|---|---|
| `NATIVE-09` Hedron 0.67 bridge | Edron's accepted projections use the Hedron 0.67 application, interaction, outcome, lifecycle, asset, and component authorities without a duplicate runtime | Native identity, lowering, warning, import-order, browser-plan, and ejection fixtures; Edron plus Hedron core owners |
| `BROWSER-09` browser feature integration | The admitted Edron browser surface uses Hedron 0.67's demand-driven Alpine/CSP/lifecycle model and its explicit native/Web Component dispositions | Chromium/Firefox/WebKit, CSP/SRI, feature-off, fragment, keyboard/focus, cleanup, and specialist-host fixtures; Hedron browser owners |
| `CLEAN-067` deprecated-feature exclusion | Edron runtime code, generated projects, examples, docs, and package metadata use only canonical Hedron 0.67 paths; deprecated 0.67 compatibility paths are warning/migration inputs only | Static forbidden-symbol/tag/asset scan, generated-output scan, import graph, browser asset manifest, and negative runtime fixtures; Edron plus Hedron core owners |
| `STABILITY-09` public maturity | A narrow Edron beginner surface is classified as `stable`; every other exported or documented surface has an explicit maturity and owner | Symbol-level catalog, `__all__`/import checks, typed signatures, native-object identity fixtures, and a reviewed stable-promotion decision; Edron plus the owning Hedron package |
| `COMPAT-09` supported train | One bounded Python, Edron, Hedron 0.67, adapter, browser-asset, and host matrix is published as Supported, with a forward-compatibility matrix for Hedron 1.0 once released; declared-but-untested ranges are labeled unsupported | Clean-install, import-order, lockfile resolving 0.67.0, 1.0 forward-compatibility, upgrade, and cross-adapter matrices; release engineering and native package owners |
| `DEPRECATE-09` vocabulary cleanup | Overlapping names, aliases, and transitional paths have one canonical replacement, a diagnostic code, a migration path, and a numeric support window | Inventory of public names and warnings, idempotent migration fixtures, docs/search checks, and removal review; Edron tooling plus API owners |
| `PERF-09` bounded performance | Import, compile, render, request, asset, diagnostic, and package-install budgets are measured and protected without weakening semantics or security | Reproducible baseline, percentile thresholds, cold/warm runs, memory/size records, and regression CI; Edron plus native render/package owners |
| `SEC-09` security maintenance | Accepted security boundaries are exercised across profiles, adapters, downloads, redirects, cookies, CSRF, CSP, proxy trust, secrets, and diagnostics | Threat-model delta, negative corpus, redaction assertions, dependency/security review, and fail-closed HTTP evidence; native security owners |
| `A11Y-09` accessibility maintenance | Supported page and interaction primitives preserve Hedron 0.67 semantic HTML, keyboard/focus behavior, names/roles, reduced motion, contrast guidance, and no-JavaScript fallbacks | Automated checks plus manual keyboard/screen-reader and browser fixtures for representative Edron applications; native rendering and interaction owners |
| `PLATFORM-09` lifecycle evidence | Supported hosts and adapters have explicit version floors, launch/restart behavior, worker limits, fallback paths, and ejection paths | Clean-process, mounted-path, multi-worker, shutdown, and long-duration smoke matrices; host and adapter owners |
| `DOCS-09` adoption clarity | The public vocabulary, examples, diagnostics, compatibility policy, and upgrade guidance agree with the machine-readable contracts | Link/API/example checks, beginner walkthroughs, changelog review, and a two-version upgrade rehearsal; Edron documentation owner |

The stable candidate is intentionally small. It must be portable across the supported ASGI baseline,
retain direct native Hedron composition, have a documented return and error contract, and pass the
HTTP, HTMX, no-JavaScript, concurrency, security, accessibility, packaging, and upgrade checks
appropriate to its scope. Stable classification does not promote optional extras, framework adapters,
live transports, host-specific behavior, or internal serializer details automatically.

### Maturity and compatibility rules

- `stable` means compatibility-protected across Edron `0.x`; an incompatible change requires an
  accepted decision, migration guidance or tooling, a deprecation diagnostic when feasible, and at
  least one intervening minor phase.
- `beta` remains a supported-for-evaluation contract that may change at a minor phase boundary only
  with a changelog entry, migration impact, diagnostics, and evidence. It is not a promise that every
  optional host or dependency combination works.
- `experimental` and `deferred` surfaces must be visibly labeled in docs and reports. Experimental
  behavior cannot be the only path for an ordinary HTTP, no-JavaScript, security, or recovery flow.
- `internal` symbols, private serializer nodes, generated implementation details, and undocumented
  transitive imports are not compatibility promises, even when users can import them today.
- A deprecation has a stable identifier, replacement or non-fit explanation, first-release marker,
  and removal review. The minimum removal window is one intervening minor phase unless an accepted
  security or correctness decision records why that is unsafe.
- Package metadata may declare a wider range than CI proves. The phase packet must distinguish
  Supported, installable-but-untested, and incompatible combinations and must pin the release train
  used for its evidence.

### Entry and exit gates

Phase `0.9` implementation entry requires the `0.8` acceptance packet to be release-verified, a
frozen public-surface inventory, named native owners, a compatibility baseline for Hedron `0.67.0`
and a forward-compatibility target for Hedron `1.0.0`, and the machine-readable [phase 0.9 gate
lock](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/edron-phase09.toml). The lock must carry the exact 0.67.0 evidence target, the
future 1.0.0 compatibility policy, package requirement bounds, supported Python/host/browser matrix,
budget units, deprecation windows, and explicit deferred dispositions. Release exit requires, at
minimum:

1. every exported and documented Edron capability has one maturity, owner, package disposition, and
   public-vs-internal classification;
2. no Edron runtime, generated project, example, documentation beginner path, package metadata, or
   browser asset plan depends on a deprecated Hedron 0.67 compatibility path; migration tooling may
   recognize such input only to emit a warning and replacement;
3. the promoted stable subset has exact signatures, deterministic diagnostics, native identity,
   ordinary HTTP/HTMX and no-JavaScript behavior, security, accessibility, and upgrade evidence;
4. the Supported dependency and host matrix passes in clean environments, with unsupported ranges
   clearly labeled and no accidental dependency widening;
5. every deprecated or contradictory path has a warning/migration fixture, a numeric support window,
   and an explicit removal or retention decision;
6. import, compile, render, request, asset, diagnostic, artifact, and installation measurements meet
   the published budgets, with no benchmark-only semantic shortcuts;
7. security and accessibility regression suites cover representative pages, interactions, adapters,
   mounted paths, production profiles, and negative cases;
8. wheel/sdist, offline-install, dependency-isolation, browser-asset, provenance, and upgrade/rollback
   evidence are retained for Edron `0.9.0` on the Hedron `0.67.0` lock target; and
9. the Edron 0.9 source and accepted public contract pass the Hedron 0.67.0 matrix and, once
   released, the Hedron 1.0.0 forward-compatibility matrix without deprecated-path dependencies;
10. the complete preceding regression suite plus the Phase `0.9` compatibility, maturity, performance,
   security, accessibility, documentation, and recovery suites pass before an `edron-v0.9.0` tag is
   considered.

If a gate fails, the affected capability keeps its prior maturity or is narrowed in the acceptance
packet. The phase does not gain a compatibility promise by silently removing a failing test.

### Release shape and non-goals

`0.9.0` establishes the reviewed maturity and compatibility baseline. `0.9.x` releases are for
compatible fixes, security updates, dependency updates within the declared matrix, and documentation
or migration corrections. Additive work that introduces a new authority, host, renderer, interaction
model, live transport, or broad framework parity belongs in a separately accepted phase or RFC.

Phase `0.9` does not:

- create or schedule Edron `1.x`, freeze every Beta API, or turn the package's Beta distribution
  classifier into a stable product guarantee;
- provide `import edron as st`, a whole-script rerun runtime, a global session dictionary, or a
  second renderer, router, state, job, asset, browser, or security authority;
- add a new framework/host adapter solely to enlarge the support table, or claim Flask/Django,
  notebook, Workbench, Posit Connect, or live-transport parity without a native lifecycle packet;
- remove a public path without the deprecation and migration rules above, except where an earlier
  accepted decision explicitly records a different boundary; or
- conceal regressions by changing semantics, weakening security/accessibility checks, dropping
  no-JavaScript fallbacks, or narrowing the tested matrix while leaving broader claims in metadata.

Phase `0.9` may receive multiple minor and patch releases. Completion means that the surviving public
surface is easier to classify, measure, upgrade, and support—not that every Edron capability becomes
stable or that a future major release is implied.

## Permanent boundaries across all phases

The following remain architectural boundaries unless a future accepted RFC explicitly supersedes
RFC-0094 and supplies migration, security, state, HTMX, accessibility, and compatibility evidence:

- no `import edron as st` compatibility contract;
- no module-global output, whole-script rerun runtime, or persistent page instance;
- no global untyped `session_state` dictionary;
- no mutation hidden behind a Boolean-returning display button;
- no second renderer, router, endpoint registry, interaction catalog, state store, style/asset
  system, job queue, browser runtime, or security authority;
- no arbitrary raw HTML, runtime CSS injection, or magic object dispatcher as the beginner path;
- no runtime package installation, `edron[all]`, or extra-based runtime feature flag; and
- no loss of direct native Hedron composition or exact native-object identity.

## Promotion and release gates

Before a candidate capability enters a release contract, its phase packet must record:

1. the user problem and why native composition alone is insufficient for the beginner path;
2. the exact public Edron vocabulary, typing, return values, diagnostics, and compatibility impact;
3. the owning public Hedron object, package, registry, route, state, style, asset, or response
   authority;
4. HTTP, HTMX, no-JavaScript, concurrency, security, accessibility, performance, packaging, and
   native-identity evidence appropriate to the capability;
5. base, optional direct-install, shortcut-extra, native-only, or application-owned disposition;
   and
6. migration and rollback behavior.

Every phase requires its own accepted delta contract, implementation plan, machine-readable locks,
built-artifact evidence, and explicit release decision. A roadmap row cannot satisfy an acceptance
gate and cannot be cited as proof that a feature is available.

## Related documents

- [Edron user guide](guides/edron-user-guide.md)
- [Edron 0.8 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_008.md)
- [Edron deployment guide](guides/edron-deployment.md)

- [Edron 0.1 public API](api/EDRON.md)
- [Edron state and interaction](api/EDRON_STATE_INTERACTION.md)
- [Edron packaging](api/EDRON_PACKAGING.md)
- [Edron capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)
- [Edron implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)
- [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)
- [Edron acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)
- [Hedron capability roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md)
