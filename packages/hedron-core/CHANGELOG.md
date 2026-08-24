# Changelog

## [0.60.2] — 2026-08-24

### Fixed
- Coordinated Workbench and Connect integration fixes from the 0.60.2 maintenance release.

### Changed
- Coordinated train tip `0.60.2` (in-tree patch; tag/PyPI published).

## [0.60.1] — 2026-08-23

### Fixed
- Isolated cache values and preserved native prepare-tree lifecycle semantics.
- Hardened serializer, URL, secret, upload, and path validation boundaries.

### Changed
- Coordinated train tip `0.60.1` (in-tree patch; tag/PyPI deferred).

## [0.60.0] — 2026-08-23

### Added
- Custom theme platform, typed modern colors, deterministic ThemeSpec packages, accessibility modes, scoped recipes, preference selection, and zero-application-CSS component evidence (RFC-0089 / D-108).

### Changed
- Coordinated train release 0.60.0 (tag and PyPI publication tracked separately).


## [0.59.0] — 2026-08-22

### Added
- Phase 0.59 modern CSS platform, typed controls, responsive containers, shell/workflow primitives, and release evidence (RFC-0087 / D-106 / D-107).

### Changed
- Coordinated train release `0.59.0` (published on PyPI).


## [0.58.1] — 2026-08-22

### Changed
- Coordinated train tip `0.58.1` (in-tree patch; tag/PyPI deferred).

## [0.58.0] — 2026-08-21

### Added
- Phase 0.58 progressive feature and styling authoring (RFC-0085 / D-101 / D-102 / D-105).

### Changed
- Coordinated train tip `0.58.0`, published on PyPI.

## [0.57.0] — 2026-08-21

### Added
- Phase 0.57 unified presentation / zero-application-CSS (RFC-0084 / D-099 / D-100).

### Changed
- Coordinated train tip `0.57.0` (in-tree cut; tag/PyPI deferred). Restores the 0.57
  train entry so package history matches docs/guides/release-notes.md (previously
  omitted between 0.58.0 and 0.56.1).

## [0.56.1] — 2026-08-21

### Changed
- Coordinated train tip `0.56.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- Workspace Python quality upgrade: typing debt burn-down, safer best-effort exception logging, ASYNC/PTH/DTZ/RET ruff rules, and maintainability refactors without public API breaks.


## [0.56.0] — 2026-08-20

### Added

- Security control plane composition under `hedron_core.security_plane` (context, sensitivity, sinks, egress, budgets, intents, posture).

## [0.55.0] — 2026-08-20

### Changed
- Coordinated train tip `0.55.0` (in-tree cut; tag/PyPI deferred).

### Added
- `MasterDetail` responsive master-detail layout with named fragment regions
  (LAYOUT-055 / RFC-0082). FastAPI-owned capability, replay, upload, CSP, and
  upgrade-report helpers live in the `hedron` package.

## [0.54.0] — 2026-08-20

### Changed

- Coordinated train tip `0.54.0` (published on GitHub and PyPI).
- Phase 0.54 authoring loop + application chrome (RFC-0081 / D-093 / D-094).

### Fixed

- Accessibility records reject malformed task/gate arrays and non-boolean flags.
- Job snapshots, media tracks, prediction scores, and Workbench authorization fixtures
  reject ambiguous serialized boolean values instead of coercing strings.

## [0.53.0] — 2026-08-20

### Added

- Coordinated train tip `0.53.0` (in-tree Published; tag/PyPI deferred).
- Application DX contracts (RFC-0080 / D-091 / D-092): assets, diagnostics, routes,
  workflows, testgen, theming, discovery, and fleet doctor.

## [0.52.0] — 2026-08-20

### Changed
- Coordinated train tip `0.52.0` (in-tree Published; tag/PyPI deferred).
- Phase 0.52 conformance authority + Posit lifecycle (RFC-0079 / D-089 / D-090; #522).

## [0.51.2] — 2026-08-20

### Changed
- Coordinated train tip `0.51.2`.

### Fixed
- See flagship `hedron` changelog for the full 0.51.2 quality/typing list.

## [0.51.1] — 2026-08-20

### Changed
- Coordinated train tip `0.51.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- See flagship `hedron` changelog for the full 0.51.1 bugfix list.

## [0.51.0] — 2026-08-19

### Added
- Password visibility toggle, `SwapReveal`, `BusyRegion` / `Hx(busy=...)`.

### Changed
- Coordinated train tip `0.51.0`.

## [0.50.3] — 2026-08-19

### Changed
- Coordinated train tip `0.50.3`.

### Fixed
- HTMX `@command` and compiled refresh/patch responses stay fail-closed for undeclared targets.
- Tabular normalize, secret columns, draft-transfer names, and secret-like redaction no longer leak or false-match.
- Data/chart/patch/CSS/image/collab correctness (see tests/unit/test_bugfix_0503.py).

## [0.50.2] — 2026-08-19

### Changed
- Coordinated train tip `0.50.2` (in-tree patch; tag/PyPI deferred).

### Fixed
- Update-target ownership treats empty `app_id` as foreign when an expected id is set;
  incoming `InteractionResult` refresh/OOB hosts are re-checked.
- Redis cache SET requires transactional `pipeline` (MULTI/EXEC).
- Invalid plugin PEP 440 specifiers raise `HED-PLUGIN-FAILED` instead of incompatible.
- Status 422 retargets `#hedron-errors`.

## [0.50.1] — 2026-08-18

### Changed
- Coordinated train tip `0.50.1`.

### Fixed
- `Hx` / `HtmxLink` accept the HTMX relative target `this`.
- `Button`, `LinkButton`, and `IconButton` accept `id`.

## [0.50.0] — 2026-08-18

### Changed
- Coordinated train tip `0.50.0` (in-tree cut; tag/PyPI deferred).

### Added
- Explorer architecture services/views split, ExplorerProvider v1, query pagination,
  diffs, headless CLI parity, bounded lab, and HTMX authoring primitives (#496–#500, #502, #503).

### Fixed
- ``Select.depends_on`` sanitizes parent field ids the same way as ``dom_id_part``.
- ``hedron-ui.mjs`` handles toast dismiss and ``data-hedron-after-load`` GET after swap.

## [0.49.1] — 2026-08-18

### Changed
- Coordinated train tip `0.49.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- Directory-upload paths reject raw CR/LF/TAB, not only percent-encoded forms (#393).
- Strip Hedron ``Field()`` metadata from TypeSchema v2 instead of failing closed (#394).
- Copy OpenAPI discriminator objects instead of sanitizing them as nested schemas (#395).
- Prefix ``data-hx-*`` URLs with the mount path at serialize time (#398).
- Redis cache values use ``v:`` keys and tag indexes use ``t:`` so ``tag:`` cannot collide (#254).
- ``inspect_data`` raises ``HED-DATA-0005`` on mismatched column-oriented lengths (#258).
- ``is_local_path`` rejects raw ``://`` / leading ``//`` in query strings (#273).
- Unscoped ``JobBackend.request_cancel`` fails closed via ``job_authorized_http`` (#266).
- ``InferencePolicy.release`` requires matching caller auth (#279).
- CSRF tokens compare as UTF-8 bytes (#402).
- ``DependsOn`` lifetime strings coerce to the enum; write-only fields drop from output ``required`` (#386, #385).
- OpenAPI registers ``hedronScopes`` and projects TypeSchema (#387).

## [0.49.0] — 2026-08-17

### Added
- Phase 0.49 FastAPI/Pydantic convergence (D-081 / D-084 / RFC-0076).

### Changed
- Coordinated train tip `0.49.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- TypeSchema sanitizer allowlists JSON Schema keywords and fail-closes unknown keys
  and ``json_schema_extra`` secrets (#384).


## [0.48.0] — 2026-08-17

### Added
- Closed `HtmxExtension` / `ExtensionSet` / `Page.htmx_extensions` with demand-driven pinned local HTMX extension assets (`sse`, `head-support`, `preload`).
- Portable `SseRegion` / `SseTrigger`, registered `AssetRef` head merge, and GET-only preload authoring on `HtmxLink`.

### Changed
- Coordinated train tip `0.48.0` (in-tree cut; tag/PyPI deferred). Idiomorph / morph swap stays Deferred.

### Fixed
- Head-support admits only `is_local_path` hrefs, HTML-escapes them, and rejects
  quote/breakout/`..` values instead of interpolating a second unescaped copy
  (#374). FRAGMENT inject now runs `reject_invented_fragment_scripts`.

## [0.47.0] — 2026-08-17

### Added
- Phase 0.47 first-class maps (`hedron-maps` 0.1.0) on the coordinated train (D-078 / D-082 / RFC-0074).

### Changed
- Coordinated train tip `0.47.0` (in-tree cut; tag/PyPI deferred).

## [0.46.0] — 2026-08-16

### Added
- Phase 0.46 FeatureBundle / FeatureRequirement / FeatureConflictError / FeatureProvider (D-075 / D-079 / RFC-0073).

### Changed
- Coordinated train tip `0.46.0`.

### Fixed
- FeatureBundle include fails closed with ``HED-BUNDLE-0008`` when a handle is
  already claimed by an included bundle (#335).
- ``include_bundle`` fails closed with ``HED-BUNDLE-0007`` when views or commands
  are still factories, so Flask/Django cannot silently store an unmaterialized
  DataWorkspace (#339).


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 catalog/manifest/projection types, TypeSchema.stable_fingerprint, HED-CATALOG / HED-PROJECTION codes (D-074 / D-077 / RFC-0072).

### Changed
- Coordinated train tip `0.45.0` (in-tree cut; tag/PyPI deferred).

## [0.44.0] — 2026-08-16

### Added
- Phase 0.44 type-driven authoring (D-072 / D-076 / RFC-0071).

### Changed
- Coordinated train tip `0.44.0` (in-tree cut; tag/PyPI deferred).


## [0.43.0] — 2026-08-16

### Added
- Phase 0.43 refreshable views, command handles, and typed updates (D-071 / RFC-0070).

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).
- Internal module split; public imports unchanged.

### Fixed
- Redis tag indexes with PTTL ``-1`` are not given a finite TTL by a later tagged write.
- SafeUrl / ``contains_dangerous_scheme`` / icon scans NFKC-normalize like EVAL-020
  so fullwidth ``javascript:`` / ``data:`` schemes fail closed (#281).
- ``RedisStatusStore`` reclaims idempotency pointers with the same Lua/WATCH
  compare-and-delete as ``RedisJobBackend`` so concurrent ``SET NX`` cannot
  drop a live key (#269).
- ``InferencePolicy.request_cancel`` requires caller ``auth_subject`` /
  ``tenant_id`` matching the request (``job_authorized_http``) and never replays
  stored owner credentials to ``JobBackend`` (#264).
- SMIL remote-href scanning ignores attribute order and rejects ``values=``
  keyframes the same as ``to=`` (#261).
- Production security gate treats a missing ``session_secret`` as insecure when
  sessions are enabled; pass ``sessions_enabled=False`` to skip (#260).
- Redis cache overwrite and ``ttl<=0`` drop previous tag memberships so stale
  indexes cannot delete the live value (#253).
- Redis cache keys use ``h1:c:`` so they cannot read or delete ``h1:job:``
  status records on a shared client (#252).

## [0.41.0] — 2026-08-15

- Phase 0.41 browser composition, bounded draft transfer, navigation, tracing, failure isolation, and regression closure (D-069).

## [0.40.0] — 2026-08-14

### Added
- Phase 0.40 authoring kit, metadata parity, React migration matrix, and remediation packet (D-068).

## [0.39.0] — 2026-08-14

### Added
- Phase 0.39 rich data ABI, OptimisticMutation, chartlink, and remediation packet (D-067).

## [0.38.0] — 2026-08-14

- Phase 0.38 high-fidelity charts / train alignment (D-066 / RFC-0069).


## [0.37.0] — 2026-08-14

- Coordinated train cut for phase 0.37 (D-065).

## [0.36.0] — 2026-08-13

- Coordinated Beta train cut for Web Component ABI foundation (D-064 / RFC-0060).

## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

### Fixed

- ``is_production_env`` and CSRF Secure env helpers strip whitespace so padded
  ``HEDRON_ENV`` / ``FLASK_ENV`` values cannot silently disable production gates (#195).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).

## [0.33.0] — 2026-08-13

- Coordinated train bump for phase 0.33 (`hedron-posit` unified Posit adapter; D-061 / RFC-0066).

## [0.32.0] — 2026-08-12

- Coordinated train bump for phase 0.32 MCP production-grade graduation.

### Fixed

- Async cache single-flight no longer publishes owner ``CancelledError`` into the
  shared future; sibling waiters retry and take ownership instead of being
  cancelled (#158).
- Celery/RQ bridges skip broker enqueue on idempotent replay and only
  ``mark(FAILED)`` when this call created the job body (#157).

## [0.31.0] — 2026-08-12

- Coordinated `0.31.0` train: tooling-grade conformance/sim/notebook/sample-kit/Node+Java evaluators and `hedron migrate streamlit` (D-059 / RFC-0064 / RFC-0061).

## [0.30.0] — 2026-08-12

- Coordinated `0.30.0` train; `hedron-workbench` depends on `fastapi-workbench` 1.0.0 (phase 0.30 / D-058).


## [0.29.0] — 2026-08-11

### Changed

- Coordinated 0.29 train bump. HED-WB diagnostic catalog for hedron-workbench.


## [0.28.2] — 2026-08-11

### Fixed

- Authorize ``HX-Retarget`` / ``HX-Reselect`` against declared ``FragmentRegion``s
  (plus reserved sinks ``#hedron-toast`` / ``#hedron-errors`` / ``#hedron-auth``)
  so outbound retarget cannot land outside the route allowlist (#76).
- Authorize ``HX-Location`` JSON ``target`` / ``select`` with the same region
  allowlist so location payloads cannot bypass retarget controls.
- Validate ``OobUpdate`` / ``oob_swap`` with ``safe_hx_swap``; fail closed when
  ``resolve_fragment_region`` is called with a missing target; reject
  ``select_oob`` / ``OobUpdate`` same-target conflicts and non-``#id`` tokens at
  materialize / construction time.
- ``HtmxLink`` / ``NavLink`` default ``hx-swap`` is ``innerHTML`` (landmark-safe).
- Shared ``csrf_cookie_should_be_secure`` helper for host adapters.

### Changed

- Coordinated Beta patch to `0.28.2` (pin `>=0.28.2,<0.29`).

## [0.28.1] — 2026-08-10

### Fixed

- Mount-aware static path helper for adapters; live native-disable honor on escape
  paths; plugin remediation pin stays train-scoped from release metadata.

### Changed

- Coordinated Beta patch to `0.28.1` (pin `>=0.28.1,<0.29`).
- Charts / sample-kit floors raised to `>=0.1.9,<0.2`; native to `>=0.1.2,<0.2`.

## [0.28.0] — 2026-08-10

### Added

- Production-grade graduation for `hedron-charts` / `hedron-native` Supported
  inventories (D-056 / RFC-0059): static/Matplotlib beginner charts, optional
  native escape acceleration with `HEDRON_NATIVE_DISABLE` fallback, interactive
  Auto quarantine, and SUPPLY-028 pin/SBOM evidence.

### Changed

- Coordinated Beta train bump to `0.28.0` (pin `>=0.28.0,<0.29`).
- Charts / sample-kit floors raised to `>=0.1.8,<0.2`; native to `>=0.1.1,<0.2`.


## [0.27.0] — 2026-08-10

### Added

- Production-grade graduation for the declared Supported satellite inventory
  (D-055 / RFC-0058): inventory freeze, `v0.26.0` upgrade fixtures, host-only
  adapter/data/HDJ/extras evidence, portable parity, and REVIEW-027 disposition.

### Fixed

- Allow safe accessibility attributes on `MainPanel`, `OobHost`, and `AttrHost`,
  merging caller `data` with internal `data-hedron-*` markers (`#56`).
- Default unnamed `AppShell` navigation to `aria-label="Primary"`.
- Accept additive `class_` theme hooks on `Button` / `LinkButton` / `SubmitButton` /
  `IconButton`, `Text` / `Heading`, `Alert` / `Badge` / `Status`, and primary form
  controls (`TextInput` / `TextArea` / `Select` / `Checkbox`) (`#29`).
- Detect `select_oob` conflicting with the same-target `OobUpdate`, document
  one-OOB-mechanism shell guidance, and allow optional landmark
  `OobUpdate(tag=...)` as defense in depth (`#57`).
- Surface non-`#id` `select_oob` tokens via `unparsed_select_oob_tokens`.

### Changed

- Own bundled `/hedron-static` assets and shared PAGE inject helpers
  (`hedron_core.page_assets`) for FastAPI/Flask/Django hosts.
- `OobUpdate` / `oob_swap` default `swap` is `innerHTML` so landmark hosts keep
  their tag when applying out-of-band updates.
- Coordinated Beta train bump to `0.27.0` (pin `>=0.27.0,<0.28`).

## [0.26.1] — 2026-08-10

### Changed

- Coordinated Beta patch release.

## [0.26.0] — 2026-08-10

### Added

- Production-grade graduation packet for the declared Supported CRUD/admin inventory
  (D-054 / RFC-0057): machine-readable inventory, `v0.25.2` upgrade fixtures, secured
  Explorer evidence, FastAPI ops smoke, and REVIEW-026 security disposition.

### Changed

- Coordinated Beta train bump to `0.26.0` (pin `>=0.26.0,<0.27`).

## [0.25.2] — 2026-08-10

### Fixed

- Validate `InteractionResult.oob` items are `OobUpdate` instances in `__post_init__`.
- `Hx.as_html_attrs` keeps `SafeUrl` instances for `url` / string `push_url`.
- `HtmxLink(external=True)` renders as a plain link without rejected absolute `hx-*` URLs.
- Reject `..` path traversal and bare path-relative tokens for NAVIGATION / FORM_ACTION / REDIRECT SafeUrls (root-relative required).
- `run_prepare` fails closed when an event loop is already running; shared `cookie_path_for_mount` lives in core.
- `normalize_mount_path` rejects `.` / `..` / `%2e` segments.
- RedisJobBackend **and** RedisStatusStore CAS fail closed without pipeline/WATCH; Celery/RQ cancel restore is CAS-only.
- Reserved OOB `#select` always forces `hx-swap-oob` wrapping; WebSocket `RegionUpdate.swap` validated.
- Redis `cleanup_expired` prefers `SCAN` over `KEYS`.
- Add `apply_allow_undeclared_targets` helper for host adapters.

### Changed

- Coordinated Beta patch with `hedron` 0.25.2.

## [0.25.1] — 2026-08-09

### Changed

- Coordinated Beta patch release with `hedron` 0.25.1; no core contract changes.

## [0.25.0] — 2026-08-09

### Changed

- Coordinated Beta train bump with `hedron` 0.25.0.

## [0.24.0] — 2026-08-09

### Changed

- Coordinated Beta train bump with `hedron` 0.24.0.
- Live-transport disposition `polling_only` (D-053): polling Supported; live helpers remain experimental.
- Default `vary-htmx` InteractionResult cache emits `Cache-Control: private, no-store`.
- Multi-region policies add `HX-Target` to `Vary` automatically.
- `InMemoryJobBackend` logs a multi-worker warning on `set_job_backend` (still refused in production).

### Security

- OOB updates without declared fragment regions are rejected unless the target is a
  reserved id (`hedron-toast`).
- HTMX requests with declared regions require `HX-Target` (no implicit first-region auth);
  `HX-History-Restore-Request` may omit `HX-Target` for full-page restore.
- Job auth scopes use exact match (tenant-only jobs do not authorize arbitrary subjects).
- `InteractionResult.status_code` must be an `int` (bool rejected; int-like strings coerced).

## [0.23.0] — 2026-08-08

### Changed

- Promotes locked CRUD/admin facade to API `stable`.

### Security

- HTMX fragment region auth is selector-based: exact `#id` selector or HTMX bare-id
  header form; rejects `##…` collapsing and divergent `region.id` matching.
- Public `validated_extra_headers()` allowlists approved HTMX / cache response headers.
- Inference cancel passes scoped `auth_subject` / `tenant_id` to the job backend and does
  not free concurrency or claim cancel on authz denial.

## [0.22.0] — 2026-08-08

### Added

- `CsrfStrategy` protocol with `DoubleSubmitCookieCsrf` and `SessionTokenCsrf`.
- `SecurityPolicy.csrf` / `resolve_csrf_strategy()` and `SecurityHeadersPolicy` merge in
  `response_headers()` (`False` / `"app"` emit no Hedron security headers).
- `CsrfField`, `Hx`, and `Form(..., hx=Hx(...))` for validated HTMX form attributes.

## [0.21.0] — 2026-08-08

### Added

- Phase 0.21 human AT packet types (`HumanAtRecord`, evidence inventory hook) and
  engineering prep for D-052 / RFC-0055 (sessions remain Planned).

### Fixed

- Coordinated Beta train with FastAPI/Flask/Django fragment allowlist parity and
  DataEditor Escape/403 JSON hardening (see `hedron` / `hedron-data` / adapters).

## [0.20.0] — 2026-08-07

- Production security floor and adapter parity (phase 0.20 / D-051).


## [0.19.0] — 2026-08-07

### Added

- Phase 0.19 accessibility engineering and inclusive authoring (RFCs 0023 / 0051–0055, D-050):
  - `AccessibilityContract` catalog, standards profile, waiver/statement governance
  - Landmark safe attrs / real types, allowlisted `Page` scripts, PE form paths
  - Explorer accessibility review workspace, ATAG inspect/eject metadata
  - `AccessibilityScenario`, tree snapshots, axe/SARIF helpers; automated AT matrix


## [0.18.0] — 2026-08-06

### Added

- Phase 0.18 model demos and inference workflows (RFCs 0045–0050, D-049):
  - `InferenceInterface` / `ModelDemo` / `ActionRegistry` (fail-closed registered actions only).
  - `ExampleSet`, `PredictionFeedback`, presentation builtins (`PredictionLabel`,
    `ParameterViewer`, `Dialogue`).
  - `InferencePolicy` over `JobBackend` (admission, queues, concurrency groups, batching,
    cancelable streaming); `ModelDemoScenario` synthetic kit.
  - `InferenceWorkflow` with structured non-canvas editor, publish/rollback, adversarial
    host-code/path rejection.
  - Diagnostic codes `HED-DEMO-*`, `HED-INFER-*`, `HED-FEEDBACK-*`, `HED-WORKFLOW-*`.

## [0.17.0] — 2026-08-06

### Added

- Phase 0.17 reactive dashboards and agent interfaces (RFCs 0040–0044):
  - `DashboardBinding` / `InteractionGraph` / `TriggerContext` and lifecycle envelope.
  - `PropertyPatch` / `CollectionPatch` with collection selectors and full-fragment fallback.
  - Shell builtins: `HtmxLink`/`NavLink`, `OobHost`/`AttrHost`, `AppShell`/`MainPanel`;
    `class_` on content Link via ElementProps.
  - Markup asserts: `assert_dialog_markup`, `assert_tabs_markup`, `assert_pagination_markup`,
    `assert_lazy_markup`.
  - Expanded `error-codes.md` alignment for registered `HED-*` codes.

## [0.16.0] — 2026-08-06

### Added

- Workbench-flow testing helpers (`assert_transform_plan`, fixtures) for AppScenario.
- FeatureManifest registration helpers for plugin packages (`PluginContext.register_feature`).
- Coordinated Beta train with phase 0.16 curated extras.

## [0.15.0] — 2026-08-05

### Added

- Phase 0.15 data-app surface completeness: typed controls and surface chrome, Map/GeoJSON,
  media Range/downloads, BrowserContext/Storage, Math/IFrame, scenario marks, and testing
  helpers (`AppScenario`, HTMX asserts).

## [0.14.0] — 2026-08-05

### Added

- Phase 0.14 portable runtimes and acceleration (conformance kit hooks, optional native
  acceleration, HDJ instrumentation where applicable).

## [0.13.0] — 2026-08-05

### Added

- Phase 0.13 advanced async and observability.


## [0.12.0] — 2026-08-05

### Added

- Phase 0.12 data and visualization scale contracts and adapters.



## [0.11.0] — 2026-08-04

### Added
- Phase 0.11 native framework depth (Flask Blueprint/`init_app`, Django AppConfig/forms/QuerySet,
  portable adapter harness, HDJ manifests/CSP inventory, Celery/RQ bridges, live helpers).

### Fixed
- Celery/RQ bridges implement the full `JobBackend` protocol (idempotency, cancel, cleanup, mark).


## [0.10.1] — 2026-08-04

### Fixed
- Reject unsafe HTML attribute names and spaced `meta refresh` URL forms.
- Scope job idempotency by tenant/auth; authorize cancel; harden Redis cancel/mark races.
- Tighten SVG/icon active-markup scans (unquoted remote href, SMIL `on*` handlers).
- Reject control characters in HTMX approved header values.
- Always emit HTMX `Vary` for private/no-store interaction cache hints.

## [0.10.0] — 2026-08-04

### Added
- Live transport contracts: SSE framing, focused streaming, page/session channels, media sessions, navigation preload (RFC-0032).
- `Dialog` and `ChatMessage` built-ins; pinned HTMX SSE and head-support extension digests.

## [0.9.0] — 2026-08-04

### Added

- `RenderSession` for request-scoped rendering that shares deterministic identity,
  diagnostics, cycle detection, and node/depth budgets across multiple component renders.

### Removed

- The experimental HDN parser, evaluator, formatter, render program, discovery metadata, and
  public APIs.

### Changed

- Build manifests use format 2 and no longer contain HDN program entries.

## [0.8.0] — 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.
- Use the canonical `template.hdn` filename during component discovery.

## [0.7.0] — 2026-08-03

- Phase 0.7 portable adapters, operations, and jobs train.


All notable changes to `hedron-core` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.6.0] — 2026-08-03

Visualization contracts, trusted content boundaries, and Auto chart hooks for phase 0.6.

### Added

- `VisualizationAdapter`, `ChartOutput`, `ChartAccessibility`, and `VisualizationLimits`.
- Trusted icon/SVG registry (`register_icon`, `get_icon`, `trusted_svg`).
- `TrustedHtml.nh3(...)` sanitizer constructor (optional `nh3`).
- Auto chart-stub remediation points at `hedron-charts` (no longer “phase 0.6”).

### Security

- Icon SVG registration rejects script URLs and common event-handler / `foreignObject` patterns.

### Changed

- Default plugin `hedron_version` gate is `>=0.6,<0.7`.

## [0.5.0] — 2026-08-03

Data application foundations in core: `Auto()` renderer registry, cache protocols,
utility components, and ColorMode.

### Added

- `Auto`, renderer registry, and bounded Data Intelligence inspection.
- Cache protocols, in-memory backend, key builder, single-flight, and Explorer traces.
- Utility built-ins: Metric, CodeViewer, JSONViewer, Progress, Status, Toast,
  Expander, Tabs, Sidebar.
- `ColorMode`, `ColorModeToggle`, `color_mode_script`, and `resolve_color_mode`.
- `Page(data_theme=...)` for explicit `data-theme` on `<html>`.

### Fixed

- Theme CSS: system dark uses `:root:not([data-theme="light"])`; explicit light preference
  overrides system dark.
- Cache single-flight keeps results until waiters finish (no waiter `KeyError` race).
- `Sidebar` uses `aria={"label": ...}` (render no longer crashes).
- `ColorModeToggle` emits a hidden `csrf_token` when provided.
- Native attributes match HTMX 2: `hx-disinherit`, `hx-inherit`, and `hx-validate` are accepted;
  removed `hx-sse` / `hx-ws` and non-core `hx-href` are rejected.

## [0.4.0] — 2026-08-03

Developer platform: JSON/SARIF diagnostics, suppressions, source spans, and plugin
metadata contracts in core.

### Added

- `Diagnostic.as_json`, `diagnostics_to_sarif`, `Suppression`, `SourceSpan`,
  `apply_suppressions`, `meets_severity_threshold`.
- Framework-neutral plugin metadata and Explorer panel registration helpers.

### Fixed / hardened

- Suppression scopes use exact or PurePath prefix matching (suffixes like `.css` no longer match).
- SARIF `tool.driver.version` comes from package `__version__`.
- Registry builder snapshot/restore helpers for plugin rollback.

## [0.3.0] — 2026-08-03

Authoring, scoped styles, themes, and assets for the phase 0.3 release train.

### Added

- HDN lexer/parser/expression engine, typed render programs, formatter, and
  source maps (`compile_hdn`, `format_hdn`, `run_program`).
- Scoped CSS AST compiler with stable symbols, `:global(...)`, keyframes,
  cascade layers, and typed `styles` bindings.
- `Theme` API with required accessibility tokens, light/dark modes, and token
  CSS emission into the `tokens` cascade layer.
- Fingerprinted asset pipeline and versioned build/CSS/asset manifests.
- Component-folder discovery for colocated HDN, CSS, and browser modules.
- Web Component registration metadata and custom-element HTML support.

### Fixed / hardened

- Compile-time rejection of arbitrary HDN calls; `{#for}` / expression failures
  raise `HedronError`; `??` rewrite respects parentheses/calls/indexes and strings,
  and chains (`a ?? b ?? c`) rewrite recursively without treating call commas as
  operands.
- CSS URL policy resolves registered roots, rejects empty-root relative URLs,
  absolute/`file:` paths, missing files (`HED-ASSET-0004`), symlinks, and remote URLs
  when disallowed; ERROR diagnostics fail `compile_css`; declarations without trailing
  `;` are preserved.
- Discovery uses `cls.distribution` when present; browser-only folders register a
  component stub; duplicate browser-module registration warns.
- Unknown configured themes fail build with `HED-THEME-0001`.
- `write_json_atomic` uses a unique same-directory temp file + `os.replace`.
- `RenderProgram.from_dict` / `load_hdn_program` validate format (`HED-HDN-0008`);
  digests include style-symbol maps.
- Production compile gate on `compile_hdn`/`compile_css` (`HED-BUILD-0004`) with
  force-allow for `hedron build`.

[0.4.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.4.0
[0.3.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.3.0

## [0.2.0] — 2026-08-03

Framework-neutral support for the FastAPI MVP release train.

### Added

- `@addressable` and immutable `AddressableDescriptor` for reusable resource
  factories that remain unreachable until explicitly exposed.
- Registry kinds for addressable factories and adapter-populated `RouteMeta`
  entries shared by routing, OpenAPI, CLI, and Explorer.
- Public exports: `addressable`, `AddressableDescriptor`, `AddressableMeta`,
  `RouteMeta`, `register_addressable`, and `register_route`.

### Fixed / hardened

- Render cycle detection uses component instance identity so nested same-type
  composition is valid; `__hedron_node__` / `ComponentNode` are honored by `render`.
- URL attrs `srcset`, `ping`, `hx-push-url`, and `hx-replace-url` require SafeUrl
  policy (with validated `srcset` candidates).
- `FormField` binds controls without mutating shared props; Checkbox aria lands on
  the input; `Secret[T]` validates the inner type `T`.

## [0.1.0] — 2026-08-03

Initial public release of the framework-neutral typed rendering core.

### Added

- `Model`, `Props`, `FormModel`, `EventPayload`, and `Field` with construction-time
  validation and supported-annotation guardrails.
- Trust boundary types: `Secret`, `TrustedHtml`, `SafeUrl`, and `UrlPurpose`.
- Component protocol, children/slots/fragments, deterministic identity, and sealable
  registry.
- Private context-aware HTML serializer with XSS-hardening defaults (blocked active
  tags/attrs, SafeUrl purpose checks, unknown-attribute rejection).
- `render(...) -> RenderResult` with PAGE and FRAGMENT modes and frozen result maps.
- Phase 0.1 built-ins for document, content, forms, layout, landmarks, surfaces,
  and controls, including FormField accessibility contracts.
- Typed package marker (`py.typed`) and offline reference-app static rendering proof.

### Security

- Contextual escaping for text and attributes.
- Secret redaction in diagnostics and identity records.
- Adversarial escaping corpus covering XSS smuggling paths exercised in CI.

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0
[0.1.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.1.0

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0
