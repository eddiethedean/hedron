---
status: verified
---

# Edron release roadmap

**Status:** Edron `0.5.0` implemented in-tree (publication pending); `edron-v0.4.0` is the latest in-tree tag and `edron-v0.3.0` remains the latest published release<br>
**Edron release line:** `0.3` data editing and workspace ergonomics<br>
**Latest release:** Edron `0.3.0`; compatible Hedron train `0.66.x`<br>
**Architecture:** [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Public API:** [Edron 0.3 data workspaces](api/EDRON_03.md)<br>
**State and interaction:** [Edron 0.1 state and interaction](api/EDRON_STATE_INTERACTION.md)<br>
**Packaging:** [Edron 0.1 packaging](api/EDRON_PACKAGING.md)<br>
**Acceptance:** [Edron 0.3 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_003.md)

This is the release roadmap for the separately versioned `edron` distribution. It does not assign
Hedron release numbers, change the Hedron capability roadmap, authorize implementation, or claim
that a planned capability exists. Edron may consume a later compatible Hedron train, but Edron and
Hedron phase numbers do not need to match.

No Edron `1.x` phase is planned. Phase `0.9` is a long-lived `0.x` consolidation phase, not a
countdown or commitment to `1.0`.

## Phase summary

| Edron phase | Theme | Status |
|---|---|---|
| **0.0** | Design acceptance, reusable Hedron enablement, locks, fixtures, and implementation-entry evidence | **Implemented baseline** |
| **0.1** | Complete batteries-included class facade with native Hedron identity, HTMX/HTTP parity, base tables/charts/maps, optional adapters, styling, jobs, and tooling | **Implemented in-tree; Beta** |
| **0.2** | Authoring refinement, diagnostics, source-aware tooling, and evidence-driven vocabulary polish | **Implemented and verified in-tree; Beta** |
| **0.3** | Explicit data editing and data-workspace ergonomics over native Hedron data authorities | **Published** (`edron-v0.3.0`; Beta) |
| **0.4** | Visualization, map, media, and linked-data workflow depth with accessible server-first fallbacks | **Tagged** (`edron-v0.4.0`; publication pending) |
| **0.5** | Resource, state, durable-job, and operational workflow depth without owning application infrastructure | **Implemented in-tree; unreleased Beta** |
| **0.6** | Reusable Edron application composition and deliberate `hedron-*` capability promotion | Candidate after `0.5` |
| **0.7** | Streamlit migration assistance, codemods, examples, and adoption tooling | Candidate after `0.6` |
| **0.8** | Deployment profiles, host integration evidence, and production operations guidance | Candidate after `0.7` |
| **0.9** | Long-lived `0.x` compatibility, selected stable-tier promotion, performance, security, and accessibility consolidation | Candidate after `0.8` |

Candidate phases after `0.1` are directional themes, not accepted API contracts. A capability may
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

Phase `0.6` makes larger Edron applications easier to organize without creating a second component
or plugin ecosystem.

Candidate scope:

- reusable page/feature packages that compile atomically into native `FeatureBundle` and catalog
  entries;
- typed application navigation and shared layout composition over native screen authorities;
- deliberate beginner-facing promotion of high-value `hedron-*` capabilities; and
- stronger mixed Edron/native testing, ejection, provenance, and asset-deduplication tools.

Edron continues to use fixed reviewed adapters and explicit native composition. It does not scan
arbitrary plugins, automatically re-export every installed Hedron package, or maintain a parallel
registry.

## Phase 0.7 — migration and adoption tooling

Phase `0.7` may extend the existing reviewable Streamlit migration work with Edron as an output
target.

Candidate scope:

- conservative AST analysis that never imports or executes untrusted source;
- generated Edron scaffolds with source mappings and explicit unresolved findings;
- vocabulary, state-owner, interaction, styling, and dependency migration reports;
- codemods for accepted Edron API changes; and
- side-by-side Streamlit, Edron, and native Hedron teaching examples.

Generated code requires review. This phase does not promise one-for-one behavior, accept
`import edron as st`, emulate Streamlit reruns, or hide incompatible state and mutation semantics.

## Phase 0.8 — deployment and host integration

Phase `0.8` strengthens production adoption after the core authoring model has accumulated release
evidence.

Candidate scope:

- reviewed ASGI deployment profiles and environment diagnostics;
- proxy/root-path, static asset, build-manifest, secret, worker, and observability guidance;
- native Workbench, Posit, notebook-preview, and remote-tooling composition where their maturity
  claims permit it;
- artifact, SBOM, provenance, upgrade, rollback, and air-gapped installation improvements; and
- evaluation of non-ASGI host authoring only through a separately accepted native lifecycle and
  HTTP/HTMX parity contract.

Flask or Django page-class parity is not promised by this roadmap. A host integration cannot weaken
the native security, state, fallback, or deployment contract.

## Phase 0.9 — long-lived `0.x` consolidation

Phase `0.9` is reserved for sustained compatibility and maturity work across the accepted Edron
surface.

Candidate scope:

- promote a narrow evidence-backed subset from Beta to the repository's stable API tier;
- complete deprecations and migration tooling without retaining contradictory aliases;
- reduce import, compile, request, asset, package, and diagnostic overhead against frozen budgets;
- deepen security, accessibility, browser, platform, multi-worker, and long-duration evidence;
- simplify the public vocabulary where measured usage proves overlap; and
- maintain compatibility across a bounded, supported Hedron train.

Phase `0.9` may receive multiple minor and patch releases. It is not a release candidate for `1.0`,
and finishing it does not create or schedule a `1.x` phase.

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

- [Edron 0.1 public API](api/EDRON.md)
- [Edron state and interaction](api/EDRON_STATE_INTERACTION.md)
- [Edron packaging](api/EDRON_PACKAGING.md)
- [Edron capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)
- [Edron implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)
- [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)
- [Edron acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)
- [Hedron capability roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md)
