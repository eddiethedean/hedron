# Changelog

## [0.27.0] — 2026-08-10

### Added

- Production-grade graduation for the declared Supported satellite inventory
  (D-055 / RFC-0058): inventory freeze, `v0.26.0` upgrade fixtures, host-only
  adapter/data/HDJ/extras evidence, portable parity, and REVIEW-027 disposition.

### Fixed

- Allow safe accessibility attributes on `MainPanel` and `OobHost`, merging caller
  `data` with internal `data-hedron-*` markers (`#56`).
- Accept additive `class_` theme hooks on `Button` / `LinkButton` / `SubmitButton` /
  `IconButton`, `Text` / `Heading`, and `Alert` / `Badge` / `Status` (`#29`).

### Changed

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

- Coordinated Beta train bump to `0.26.0` (pin `>=0.27.0,<0.28`).

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


## [0.10.1] - 2026-08-04

### Fixed
- Reject unsafe HTML attribute names and spaced `meta refresh` URL forms.
- Scope job idempotency by tenant/auth; authorize cancel; harden Redis cancel/mark races.
- Tighten SVG/icon active-markup scans (unquoted remote href, SMIL `on*` handlers).
- Reject control characters in HTMX approved header values.
- Always emit HTMX `Vary` for private/no-store interaction cache hints.

## [0.10.0] - 2026-08-04

### Added
- Live transport contracts: SSE framing, focused streaming, page/session channels, media sessions, navigation preload (RFC-0032).
- `Dialog` and `ChatMessage` built-ins; pinned HTMX SSE and head-support extension digests.

## [0.9.0] - 2026-08-04

### Added

- `RenderSession` for request-scoped rendering that shares deterministic identity,
  diagnostics, cycle detection, and node/depth budgets across multiple component renders.

### Removed

- The experimental HDN parser, evaluator, formatter, render program, discovery metadata, and
  public APIs.

### Changed

- Build manifests use format 2 and no longer contain HDN program entries.

## [0.8.0] - 2026-08-03

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

## [0.6.0] - 2026-08-03

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

## [0.5.0] - 2026-08-03

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

## [0.4.0] - 2026-08-03

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

## [0.3.0] - 2026-08-03

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

## [0.2.0] - 2026-08-03

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

## [0.1.0] - 2026-08-03

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
