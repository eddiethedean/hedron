# Changelog

## [0.66.0] — 2026-08-25

### Changed
- Coordinated development train for Phase 0.66 HDJ parity and registry integration.

## [0.65.0] — 2026-08-25

### Added
- Integrated application styling platform: registered custom CSS, cascade layers, stable hooks, bounded recipes, diagnostics, and provenance-preserving ejection.

### Changed
- Coordinated train cut for Phase 0.65.

## [0.64.1] — 2026-08-25

### Fixed
- Maintenance fixes for the 0.64.x release train.

## [0.64.0] — 2026-08-24

### Added
- Bounded presentation contracts and opt-in Hedron HTMX lifecycle projection for the 0.64 train.

### Changed
- Coordinated train cut for Phase 0.64; extension behavior remains explicitly declared and fallback-safe.

## [0.63.0] — 2026-08-24

### Added
- Theme contract completion, deterministic theme export/inspection/conformance checks, portable
  component state matrices, interaction profiling, static safety checks, and bounded component
  interoperability from Phase 0.63.

### Changed
- Coordinated train cut for Phase 0.63; Progressive bundle, visualization, and React-island
  extensions remain explicitly bounded and opt-in.

## [0.62.0] — 2026-08-24

### Added
- Starlette navigation identity/response headers and safe-prefetch evaluation helpers.

## [0.61.0] — 2026-08-24

### Added
- Unified action state and server-first async boundaries across forms, jobs, fragments, supported elements, and composed surfaces.
- Added bounded operation identity, stale-result rejection, explicit retry policy, trace projection, and ordinary HTML fallback.

## [0.60.2] — 2026-08-24

### Fixed
- Corrected Workbench mount handoff for full `rserver-url` URLs and mismatched listener ports.

### Changed
- Coordinated train tip `0.61.0` (in-tree patch; tag/PyPI published).

## [0.60.1] — 2026-08-23

### Fixed
- Hardened path, URL, secret, serializer, upload, and MCP boundaries against traversal,
  scheme-smuggling, state pollution, and authorization regressions.
- Fixed `UploadFlow` route identity and authorization handling, including reliable
  multi-file result aggregation.

### Changed
- Coordinated train tip `0.61.1` (in-tree patch; tag/PyPI deferred).

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
- Secure upgradeable workflow primitives (master-detail, capabilities, replay,
  uploads, CSP reporting, offline upgrade-report) under RFC-0082 / D-095 / D-096.

## [0.54.0] — 2026-08-20

### Changed

- Coordinated train tip `0.54.0` (published on GitHub and PyPI).
- Phase 0.54 authoring loop + application chrome (RFC-0081 / D-093 / D-094).

### Fixed

- Configuration loading rejects coercive booleans, malformed string arrays and tables,
  invalid scalar types, and boolean format versions instead of silently accepting them.
- Type-authored checkbox controls reject non-boolean current values instead of rendering
  truthy strings as checked.

## [0.53.0] — 2026-08-20

### Added

- Coordinated train tip `0.53.0` (in-tree Published; tag/PyPI deferred).
- Application DX Stage 1 (RFC-0080 / D-091 / D-092): `ApplicationAssetSpec` /
  `compile_application_asset_plan`, `ApplicabilityInterval` / `RemediationAction` /
  `normalize_severity_alias`, `export_routes_document` / `export_effect_graph`,
  `OperationWorkflow` / `is_terminal_job_state`, `generate_interaction_tests`,
  `run_visual_conformance`, `discover_public_api`, `diagnose_installed_fleet`.

## [0.52.0] — 2026-08-20

### Changed
- Coordinated train tip `0.52.0` (Published; `v0.52.0` on PyPI).
- Phase 0.52 conformance authority + Posit lifecycle (RFC-0079 / D-089 / D-090; #522).

## [0.51.2] — 2026-08-20

### Changed
- Coordinated train tip `0.51.2`.

### Fixed
- Runtime asserts replaced with typed validation errors across adapters, Gradio, hosts, and jobs.
- Host-integration typing tightened (`handles`, pages, router, Explorer); fail-soft exceptions log context.
- HDJ document-shape helpers moved to `hedron_jinja._document_shape`.

## [0.51.1] — 2026-08-20

### Changed
- Coordinated train tip `0.51.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- Adaptive concurrency cancels in-flight siblings when any task returns `HED-CONC-0001` (#103).
- FastAPI fragment render honors `allow_htmx_eval` on `InteractionPolicy` (#74).
- Job SSE no longer re-emits an acknowledged non-terminal snapshot (#207).
- HTMX `select_oob` accepts comma-separated `#id` lists (#70); duplicate OOB element ids fail closed (#85).
- WebSocket channel rejects valid non-object JSON without crashing (#98).
- Connection registry single-flights concurrent first `get` (#106).
- Adapter URL reversal uses boundary-safe mount-prefix matching (#202).
- `SessionState` refreshes after direct session mutation and shares one cache across duplicate dependencies (#149, #150).
- Workbench resolver preserves an extra public-base prefix; `check`/`run` skip mount rediscovery when Uvicorn set `root_path` (#135, #186).
- TreeView rejects `javascript:` data sources; HTMX busy clears on send/response errors.
- Login CSRF accepts a valid cookie when session state differs (#138); auth rate limiter evicts stale IP keys (#139).
- Flask route CSRF covers non-POST unsafe methods (#187); Workbench cookie `Path` check rejects substring matches (#160).
- Packaged asset paths cannot escape the static directory (#220); simulator browser captions are HTML-escaped (#204).

## [0.51.0] — 2026-08-19

### Changed
- Coordinated train tip `0.51.0` (in-tree; tag/PyPI deferred).

## [0.50.3] — 2026-08-19

### Changed
- Coordinated train tip `0.50.3`. See satellite
  changelogs for Flask/Django/Explorer-owned rows.

### Fixed
- HTMX `@command` and compiled refresh/patch responses stay fail-closed for undeclared targets.
- Tabular normalize, secret columns, draft-transfer names, and secret-like redaction no longer leak or false-match.
- Data/chart/patch/CSS/image/collab correctness (see tests/unit/test_bugfix_0503.py).

## [0.50.2] — 2026-08-19

### Changed
- Coordinated train tip `0.50.2` (in-tree patch; tag/PyPI deferred).

### Fixed
- Login CSRF and OIDC state/nonce comparisons no longer 500 on length mismatch.
- OIDC `extra_params` cannot override protocol fields; logout redirect URIs are allowlisted.
- `include_component` rolls back the Starlette route when registry registration fails.
- Handle ownership fail-closes on empty `app_id`; mapped outcomes pass `expected_app_id`.
- ActionHandle effect merge keeps effect headers and does not OR-in undeclared HTMX targets.
- FragmentHandle initial render no longer swallows `HedronError`.
- HTMX 422 handlers retarget `#hedron-errors` without authorizing arbitrary `HX-Target`.
- Missing `HX-Target` on `h-view-*` hosts fails closed.
- `process_image` requires `root=` for filesystem paths.

## [0.50.1] — 2026-08-18

### Changed
- Coordinated train tip `0.50.1`.

### Fixed
- HTMX relative target `this`, control `id`s, formula/CSV injection prefixes, and Explorer 0.50 wiring (see satellite changelogs).

## [0.50.0] — 2026-08-18

### Changed
- Coordinated train tip `0.50.0` (in-tree cut; tag/PyPI deferred).

### Added
- Explorer architecture services/views split, ExplorerProvider v1, query pagination,
  diffs, headless CLI parity, bounded lab, and HTMX authoring primitives (#496–#500, #502, #503).

### Fixed
- Command success applies ``ActionHandle.effect`` / ``after`` (OOB refresh and
  ``HX-Trigger-After-Swap``).
- ``InteractionPolicy.history_restore`` selects PAGE vs FRAGMENT restore.
- Lazy keeps error templates outside the HTMX swap target.
- Danger toasts include a dismiss control.
- Requested ``explorer="development"`` in production is risk-gated, then still force-off.

## [0.49.1] — 2026-08-18

### Changed
- Coordinated train tip `0.49.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- Django ``@hedron_view`` validates CSRF before the handler (#392).
- Directory-upload paths reject raw CR/LF/TAB (#393).
- ``hedron.Field()`` metadata no longer crashes TypeSchema v2 (#394).
- OpenAPI discriminator objects are copied as metadata, not sanitized as schemas (#395).
- ``Field(default_factory=...)`` compiles as optional FastAPI params (#396).
- ``DependsOn(streaming=True)`` fail-closes without RESPONSE lifetime (#397).
- ``data-hx-*`` URLs receive the mount-path prefix (#398).
- Form-associated ``hedron-field-*`` elements no longer double-submit (#399).
- Flask session cookies set Secure when ``FLASK_ENV=production`` (#400).
- Flask and Django hosts run production security and durability gates (#401).
- CSRF tokens compare as UTF-8 bytes (#402).
- OutcomeMap unwraps ``Annotated`` unions, applies function-command maps, and honors case status/effects (#403, #322, #331).
- ``generate_form`` honors ``Control.label`` / ``Control.help`` (#323).
- Refresh and command buttons forward ``class_`` / ARIA kwargs and reject ``on*`` (#314).
- Job SSE ``Last-Event-ID`` uses the closed 0.48 grammar (#378).
- Flask/Django adapters pass ``expected_app_id`` (#315).
- Optimistic patches reject dangerous URL schemes (#291).
- Whitespace-only CSP is treated as missing in production (#286).
- ``RefreshableView`` / ``CommandHandler`` empty, cache, and class effects apply (#330, #332).

## [0.49.0] — 2026-08-17

### Added
- Phase 0.49 FastAPI/Pydantic convergence (D-081 / D-084 / RFC-0076).

### Changed
- Coordinated train tip `0.49.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- Query-only native-model ``ViewParams`` keep compiled ``Query()`` markers through
  endpoint wrapping so GET does not 422 as a JSON body (#381).
- Page and nested-router registration after OpenAPI cache or registry seal fail
  closed instead of serving stale schema or live routes (#382).
- Required ``FormBody`` commands reject non-form Content-Types with HTTP 415
  ``HED-TYPE-0003`` before FastAPI bind (#383).


## [0.48.0] — 2026-08-17

### Added
- Phase 0.48 first-class HTMX extension integration (D-080 / D-083 / RFC-0075).

### Changed
- Coordinated train tip `0.48.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- FastAPI fragment responses reject invented ``<script>`` tags before returning
  HTML, matching HEAD-048 ``fragment_invents_scripts = false`` (#374).

## [0.47.0] — 2026-08-17

### Added
- Phase 0.47 first-class maps (`hedron-maps` 0.1.0) on the coordinated train (D-078 / D-082 / RFC-0074).

### Changed
- Coordinated train tip `0.47.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- Map origin policy, DataWorkspace paging/authz, MCP authorize isolation, and
  MapInteraction command POSTs land in this first 0.47 registry cut
  (#351–#357).

## [0.46.0] — 2026-08-16

### Added
- Phase 0.46 FeatureBundle include_feature, HED-BUNDLE diagnostics (D-075 / D-079 / RFC-0073).

### Changed
- Coordinated train tip `0.46.0`.

### Fixed
- MCP tool registration runs only after a successful FeatureBundle include,
  so ``McpExposure.to_bundle()`` is side-effect free (#337).
- ``eject_feature`` removes FastAPI routes materialized for the bundle, not
  only handle descriptors (#336).
- ``include_feature`` passes already-claimed bundle handle ids into include so
  a second FeatureBundle cannot override an existing handle (#335).


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 sealed InteractionCatalog, interactions.json, Hedron.interactions, inspect/build consumers (D-074 / D-077 / RFC-0072).

### Changed
- Coordinated train tip `0.45.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- ``FormBody`` commands allowlist ``urlencoded`` / ``multipart`` Content-Types and
  reject every other media type (including ``text/plain``) with HTTP 415 instead of
  executing on model defaults (#329).

## [0.44.0] — 2026-08-16

### Added
- Phase 0.44 type-driven authoring (D-072 / D-076 / RFC-0071).

### Changed
- Coordinated train tip `0.44.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- ``ActionHandle.form()`` CSRF tokens resolve at render time so no-JS POSTs
  succeed (#319).
- Modeled ``Field.alias`` names match FastAPI Path/Query/Form parameters and
  bind URLs (#320).
- ``FormBody`` commands reject ``application/json`` with HTTP 415 instead of
  executing on model defaults (#321).


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
- ``Hedron(session_secret=None)`` is refused when sessions are enabled instead of
  installing ``SessionMiddleware(secret_key=None)`` (#260).

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

- Coordinated train cut for phase 0.37 (D-065): form-associated Alpha
  `hedron-elements`, `InteractionState`, semantic primitives, and
  `GestureOverlayCatalog`.
- Closes high-severity remediations #230–#237 and follow-on #244.

## [0.36.0] — 2026-08-13

- Coordinated Beta train cut for Web Component ABI foundation (D-064 / RFC-0060).

## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).

## [0.33.0] — 2026-08-13

- Coordinated train bump for phase 0.33 (`hedron-posit` unified Posit adapter; D-061 / RFC-0066).

## [0.32.0] — 2026-08-12

- Coordinated train bump for phase 0.32 MCP production-grade graduation.

### Fixed

- Optional session reads in ``install_authenticated_from_session`` and
  ``read_color_mode_preference`` no longer raise when ``SessionMiddleware`` is
  absent; gate on ``\"session\" in request.scope`` instead of ``getattr`` (#170).

## [0.31.0] — 2026-08-12

- Coordinated `0.31.0` train: tooling-grade conformance/sim/notebook/sample-kit/Node+Java evaluators and `hedron migrate streamlit` (D-059 / RFC-0064 / RFC-0061).

## [0.30.0] — 2026-08-12

- Coordinated `0.30.0` train; `hedron-workbench` depends on `fastapi-workbench` 1.0.0 (phase 0.30 / D-058).

### Fixed

- SSE polling rejects non-positive `poll_interval_seconds` instead of busy-looping (#143).


## [0.29.0] — 2026-08-11

### Changed

- Coordinated 0.29 train bump. Hedron(root_path=...), resolve_mount_path_from_environ re-export, color-mode cookie Path, optional hedron[workbench] extra.


## [0.28.2] — 2026-08-11

### Fixed

- Authorize ``HX-Retarget`` / ``HX-Reselect`` against declared fragment regions so
  handlers cannot redirect swaps outside the route allowlist (#76; via
  ``hedron-core``). Also authorize ``HX-Location`` JSON ``target`` / ``select``.
- `hedron new` scaffolds and the published-quickstart release checker share
  `docs/release.toml` `pin_floor` (release verify no longer expects train `.0`).
- Release workflow creates the GitHub Release only after quickstart verify succeeds
  and omits plain `linux_*` native wheels from attach.
- `render_component_response` authorizes HTMX targets (Flask/Django parity); empty/204
  InteractionResult responses apply authenticated private cache headers.
- Flask/Django honor `SecurityPolicy.allow_htmx_eval`; Flask/Django PAGE
  `interaction_response` injects page assets; Django scaffold sets portable
  `CSRF_HEADER_NAME`; async connection dispose no longer swallows close errors.
- `hedron check` escalates non-`#id` `select_oob` tokens to ERROR.

### Changed

- Coordinated Beta patch to `0.28.2` (pin `>=0.28.2,<0.29`).
- Charts floor for `hedron[charts]` raised to `hedron-charts>=0.2.1,<0.3` (Plotly/Vega
  destroy-before-remount; tip charts `0.1.11` for OOB lifecycle).

## [0.28.1] — 2026-08-10

### Fixed

- Tip honesty and adapter parity: native floor/docs, Auto Experimental remediation,
  optional chart HTMX dispose, Flask/Django mount-aware static prefixes, live
  `HEDRON_NATIVE_DISABLE`, and tip-hub/SSOT/CI footguns.

### Changed

- Coordinated Beta patch to `0.28.1` (pin `>=0.28.1,<0.29`).
- Charts / sample-kit floors raised to `>=0.1.9,<0.2`; native to `>=0.1.2,<0.2`
  (PyPI immutability for HTMX lifecycle / live native-disable fixes).

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

- Inject the HTMX core runtime before bundled extensions in PAGE document order so
  deferred `head-support` / `sse` scripts can register (`#55`).
- Scope `hedron check` Django / Plotly-Altair compatibility notices to detected adapters
  and chart extras; add `--all-compat` for the global summary (`#54`).
- Escalate `hedron check` (`HED-HTMX-0002`) to ERROR when the same id appears in both
  `select_oob` / `hx-select-oob` and `OobUpdate`, scanning `Hx` / `Form` / raw
  `hx-select-oob` literals in addition to `HtmxLink`/`NavLink` (`#57`).
- Always inject HTMX extensions on request-less PAGE renders.

### Changed

- PAGE responses inject shared core page assets (HTMX before extensions) via the
  flagship static mount backed by `hedron-core` assets.
- Default toast `OobUpdate` uses `swap='innerHTML'`.
- Charts / sample-kit extras floor raised to `>=0.1.7,<0.2`.
- Coordinated Beta train bump to `0.27.0` (pin `>=0.27.0,<0.28`).

## [0.26.1] — 2026-08-10

### Fixed

- Require the mount-path-safe `hedron-explorer>=0.26.1` in the `dev` extra.
- Make FastAPI, Flask, and Django projects generated by `hedron new` depend on the
  current `>=0.26.0,<0.27` train instead of the obsolete 0.25 range.
- Correct optional integration install guidance so flagship extras use the 0.26 train
  while independent Alpha satellite packages retain their 0.1 compatibility range.

### Changed

- Add runnable OIDC and interactive model-demo adoption examples with integration tests.
- Make release CI checksum every asset and install the exact published PyPI artifact,
  scaffold an app, and import it before creating the GitHub Release.

## [0.26.0] — 2026-08-10

### Added

- Production-grade graduation packet for the declared Supported CRUD/admin inventory
  (D-054 / RFC-0057): machine-readable inventory, `v0.25.2` upgrade fixtures, secured
  Explorer evidence, FastAPI ops smoke, and REVIEW-026 security disposition.

### Changed

- Coordinated Beta train bump to `0.26.0` (pin `>=0.26.0,<0.27`).

## [0.25.2] — 2026-08-10

### Fixed

- Propagate route `allow_undeclared_targets` into `render_interaction` / InteractionResult conversion.
- `retarget()` prefers the CSS selector for HX-Target agreement when region id differs.
- Seed CSRF cookies on safe-method HTTP 204 InteractionResult responses.
- SessionState raises when writing without SessionMiddleware; sync connection dispose fails closed on awaitables (use `close_all_async`).
- Mount CSRF cookie Path no longer forces a trailing slash (`/app` matches `/app` and `/app/...`).
- `normalize_mount_path` rejects `.` / `..` / `%2e` segments; `prefix_local_path` re-validates with `is_local_path`.
- SSE / streaming responses force `Cache-Control: no-store` after caller header merge.
- Explorer `/api/simulate` always requires CSRF (ignores `csrf_enabled=False`).
- `install_authenticated_from_session` requires a non-empty string session subject.

### Changed

- Coordinated Beta patch with workspace packages at `0.25.2`.

## [0.25.1] — 2026-08-09

### Fixed

- Restore a resolvable `hedron[charts]` install by requiring the compatible
  `hedron-charts>=0.1.6,<0.2` satellite release.
- Re-export `FragmentRegionError` from the beginner-facing package facade.
- Correct the session-auth and SQLAlchemy adopter recipes: failed sign-in feedback is
  visible, blank notes are rejected, and malformed delete identifiers return 422.
- Repair reference-app simulator expectations and formatting drift introduced by the
  post-0.25 documentation adoption pass.

### Changed

- Expand and reorganize onboarding, API, deployment, and Streamlit migration guidance.
- Harden release preparation so a failed PyPI publish cannot create a GitHub Release.

## [0.25.0] — 2026-08-09

### Added

- Production archetype packet for `examples/reference-app` (multi-worker, Redis,
  reverse-proxy subpath, `HEDRON_ENV=production`, CSP, Explorer off).
- CI critical-path budgets `W-025-FRAGMENT`, `W-025-JOB-POLL`, `W-025-DATAEDITOR`.
- Release CI attaches SBOM / evidence bundles on train tags (`SUPPLY-025`).

### Changed

- Coordinated Beta train bump with workspace packages at `0.25.0`.
- `hedron[extras]` no longer registers specialty landmine UI
  (`CodeEditor` / `TerminalView` / joystick / device); use `hedron[experimental-ui]` and
  `hedron_extras.experimental`.
- Matplotlib remains the Supported charts default; Plotly / Altair stay experimental.
- `hedron new` scaffolds continue to pin `hedron` / adapters at `>=0.25.0,<0.26`.

## [0.24.0] — 2026-08-09

### Changed

- Accepts live-transport disposition `polling_only` (D-053 / RFC-0056): polling is the
  Supported production story; SSE/WebSocket/streaming/preload remain experimental.
- `hedron new` scaffolds pin `hedron` / adapters at `>=0.25.0,<0.26`.
- Supersedes prior Deferred live-ops IDs `BROWSER-10-001`, `PERF-10-001`, and
  `LIVE-011-BROWSER` via waive ledgers.
- Root `hedron.<live>` attribute access emits `DeprecationWarning` (import
  `hedron.experimental`).

### Security

- CSRF cookies are Secure under `HEDRON_ENV=production` / `prod` (STANDARD profile).
- HTMX responses strip/override `Cache-Control: public` toward `private, no-store`.
- Deduplicated `CsrfField` / `LoginCsrfField` in `hedron.__all__`.
- History-restore HTMX requests may omit `HX-Target` when fragment regions are declared.

## [0.23.0] — 2026-08-08

### Changed

- Promotes locked CRUD/admin facade to API `stable`.
- `hedron new` scaffolds pin `hedron` / adapters at `>=0.23.0,<0.24`.
- Django scaffold defaults: CSRF + sessions middleware, `DJANGO_DEBUG` off by default,
  tightened `ALLOWED_HOSTS`.
- Production `STANDARD` sessions use `https_only` cookies.

### Security

- CSRF `Secure` honors `X-Forwarded-Proto: https` only from `HEDRON_TRUSTED_PROXIES` /
  `app.state.hedron_trusted_peers` (not arbitrary clients).
- `X-Hedron-Prepare-Deadline` is ignored unless the peer is on the same trusted-proxy
  allowlist.
- Mount paths reject protocol-relative (`//…`), absolute URL, and backslash values.
- Bundled `/hedron-static/…` asset hrefs respect the app mount prefix.
- Unapproved / evil `InteractionResult` and `extra_headers` fail closed (HTTP 403).
- `FileComponentResponse` filenames use upload sanitization (no path segments / CRLF).
- `render_interaction` authorizes HTMX targets (and rejects OOB) on 204 responses.

## [0.22.0] — 2026-08-08

### Added

- FastAPI CSRF helpers dispatch through `SecurityPolicy.resolve_csrf_strategy()`.
- Re-exports: `CsrfStrategy`, `DoubleSubmitCookieCsrf`, `SessionTokenCsrf`,
  `SecurityHeadersPolicy`, `CsrfField`, `Hx`, `LoginCsrfField`, `unsign_login_csrf`.
- RenderContext seeds CSRF tokens for bare `CsrfField()` on PAGE/FRAGMENT renders.
- `hedron new` scaffolds pin `>=0.22.0,<0.23`.

## [0.21.0] — 2026-08-08

### Added

- `@action` / `include_component` / page+component accept `fragment_regions` and
  `allow_undeclared_targets` (parity with Flask/Django).
- Human AT engineering prep on the reference app (PE create/update/delete, ErrorState).

### Fixed

- Chart OOB / fragment host layout; HTMX mutation validation ErrorState parity.
- Docs: `@action` + `fragment_regions` contract aligned with code.

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

- Phase 0.18 model demos and inference workflows (RFCs 0045–0050):
  - `InteractionRecorder` for redacted public-endpoint Python/HTTP snippets.
  - Re-exports of core model-demo / inference / workflow surfaces.
  - Optional extra `hedron[gradio]` → Alpha `hedron-gradio`.

## [0.17.0] — 2026-08-06

### Added

- Phase 0.17 reactive dashboards and agent interfaces (RFCs 0040–0044):
  - Public `render_interaction` (InteractionResult → Response); private
    `_convert_interaction_result` remains a thin delegate.
  - Optional extras `hedron[notebook]` / `hedron[mcp]` (Alpha packages).
  - Shell primitives re-exported from core (`HtmxLink`/`NavLink`, `OobHost`/`AttrHost`,
    `AppShell`/`MainPanel`).
  - Markup asserts for Dialog / Tabs / Pagination / Lazy.

## [0.16.0] — 2026-08-06

### Fixed

- Ship `hedron.build` in the flagship wheel/sdist again. A broad `**/build/` gitignore
  pattern caused Hatchling to omit the package from published artifacts, so
  `compose_lifespan` raised `ModuleNotFoundError: No module named 'hedron.build'`
  even when no manifest was required (#32). Lifespan now imports the loader only when
  a manifest is present or production mode requires one.

### Added

- Re-export workbench-flow testing helpers from `hedron-core`.
- Coordinated Beta train with optional `hedron[extras]` / `hedron-extras`.

## [0.15.0] — 2026-08-05

### Added

- Phase 0.15 data-app surface completeness:
  - `AppScenario` / HTMX testing helpers (#22–#26)
  - `region` / `@fragment` / `swap` interaction ergonomics (RFC-0039)
  - typed controls and surface chrome (docks, popover, carousel, timeline, chips)
  - media Range/download helpers (RFC-0034)
  - Map/GeoJSON with table alternative (RFC-0033)
  - `BrowserContext` / `BrowserStorage`, Math, IFrame
  - OIDC / session hardening helpers
  - named connection registry

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
- `python -m hedron` entry via `__main__.py` (PATH-independent CLI fallback).



## [0.11.0] — 2026-08-04

### Added
- Phase 0.11 native framework depth (Flask Blueprint/`init_app`, Django AppConfig/forms/QuerySet,
  portable adapter harness, HDJ manifests/CSP inventory, Celery/RQ bridges, live helpers).

### Fixed
- Flask `include_component` CSRF on unsafe methods; portable harness cookie order.
- Fail-closed QuerySet allowlists and HDJ CSP reconcile; full Celery/RQ `JobBackend` protocol.
- CLI/Explorer HDJ inventory reporting; Django forms radio/number/file widget mapping.


## [0.10.1] — 2026-08-04

### Fixed
- Require `vary_on` for default private `cache_data` scopes.
- Reject credentialed URLs in `redirect_external`.
- Validate SSE/stream/preload header names and values for control characters.
- Job SSE returns HTTP 403/404 on authz/missing; sanitize bad `Last-Event-ID`.
- Poll `job_status_response` enforces the same job authz contract as SSE.

## [0.10.0] — 2026-08-04

### Added
- Official SSE helpers (`SseResponse`, job status SSE), focused `StreamingComponentResponse`, WebSocket page/session channels, navigation preload, and `ChatInput`.
- Bundled `/hedron-static/ext/sse.js` and `head-support.js`.

## [0.9.0] — 2026-08-04

### Added

- Optional `hedron-jinja` extra for strict trusted-template composition.

### Removed

- All HDN CLI, discovery, build, and public API integration; 0.8 is the final HDN-capable line.

## [0.8.0] — 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.
- `hedron eject` creates `template.hdn`, and `hedron dev` watches `.hdn` templates.

## [0.7.0] — 2026-08-03

- Phase 0.7 portable adapters, operations, and jobs train.


All notable changes to `hedron` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.6.0] — 2026-08-03

Visualization extras, typed HTMX interaction envelope, first-party content/auth helpers,
and 0.6 behavioral closure hardening.

### Added

- `HtmxRequest`, `InteractionResult`, `InteractionPolicy`, `FragmentRegion`, OOB helpers.
- Semantic HTMX status handlers (422 validation fragments; JSON for non-HTMX).
- Declared fragment regions on `@page` / `@component`, `Vary` for page/fragment(/target),
  form `hx-sync` defaults.
- Extras: `charts`, `markdown`, `code`, `images`, `email`, `sanitize`, `auth`.
- `Markdown`, email/code/image helpers, Authlib conveniences, icon re-exports.
- `htmx_vary_dimensions` for cache/response variation documentation.

### Security

- `InteractionResult.headers` revalidated through approved local-URL / selector checks
  (no raw `HX-*` bypass).
- Route-declared fragment regions and OOB destinations enforced at runtime.
- Chart/SVG/Markdown adversarial corpus; icon registry rejects event-handler SVG.

### Fixed

- `cache="private"` / `"no-store"` emit `Cache-Control` on interaction responses.

## [0.5.0] — 2026-08-03

Data application toolkit on the FastAPI flagship: caching decorators, upload/download
helpers, ColorMode persistence, and re-exports for `hedron-data` / Auto / utilities.

### Added

- `cache_data` / `cache_component` with scoped keys and single-flight.
- `FileUpload`, `DownloadButton`, `safe_download_response`, `validate_upload_size`.
- ColorMode cookie/session helpers.
- Optional extra `hedron[data]` → `hedron-data==0.5.0`.
- Lazy `DataTable` / `DataEditor` imports with install guidance when `hedron-data` is absent.
- Re-exports for DataTable, DataEditor, Auto, utilities, and ColorMode.

### Fixed

- Cache rejects `user` / `tenant` / `session` scopes without `vary_on`, and public-scope
  request/session positional args.
- Build fingerprints registered plugin CSS assets (DataEditor host stylesheet).
- HTMX 2 context exposes every official request header, including history restores without
  `HX-Request`; response helpers cover replace/reselect and all trigger timings.
- Full pages apply CSP-compatible HTMX defaults for history, eval/scripts, same-origin requests,
  indicator styles, and native form-validity reporting.

## [0.4.0] — 2026-08-03

Developer platform for the FastAPI flagship.

### Added

- CLI `new`, `check` (text/JSON/SARIF), `graph`, and `audit-components`.
- Plugin loader with entry points, compatibility gates, lifespan hooks, and rollback.
- Public `hedron.testing` helpers and optional `hedron[browser]` hooks.
- Inference explanations/overrides in CLI `preview`.

### Fixed

- Plugin loads roll back the full registry builder (not only Explorer panels) on failure.
- Plugin `start()` failures roll back registry contributions and Explorer panels.
- `plugins = []` loads no plugins; unset plugins discover all at lifespan and build; missing enabled names error.
- Version compatibility uses `packaging` specifier sets (fail closed on invalid ranges).
- Lifespan always surfaces plugin load/`start` failures and shuts down started hooks.
- CSRF applies when any declared method is unsafe for page/component/action routes, including `include_component`.
- CSRF cookies set `Secure` when the request is HTTPS (all profiles).
- Local redirects and HTMX local-path headers reject backslash open-redirect forms; `redirect_external` fails closed without a policy.
- Production forces Explorer `development` mode off; scaffolds default `explorer = "off"`.
- Lifespan applies `[tool.hedron] component_roots` to `app.state.hedron_component_roots`.
- CLI `check`/`graph`/`audit-components` apply discovery; evergreen INFORMATION findings do not fail the exit gate; `new` guards existing `app.py`/`pyproject.toml`.
- Builds match lifespan plugin discovery and restore the registry afterward so in-process app startup can reload plugins; `override_dependencies` restores FastAPI overrides.
- Asset `href` values are HTML-escaped before page injection.

## [0.3.0] — 2026-08-03

Authoring, styles, assets, and themes for the FastAPI flagship.

### Added

- `[tool.hedron]` configuration loader and `Hedron(theme=..., build_dir=..., production=...)`.
- CLI commands: `build`, `dev`, `inspect`, and `eject` (plus existing routes/components/preview).
- Build orchestration that compiles HDN/CSS, fingerprints assets, and atomically
  promotes versioned manifests; production lifespan rejects missing manifests.
- Manifest-driven `/hedron-assets` StaticFiles mounting and page asset injection.
- Strict CSP without `style-src 'unsafe-inline'` for external stylesheets.
- First-party `hedron-disclose` Web Component with HTMX swap-safe lifecycle.

### Fixed / hardened

- Same-device atomic build promote (avoids cross-device rename failures) and CSS
  `url(...)` rewrite to fingerprinted `/hedron-assets/...` paths.
- Production loads compiled HDN from the build manifest; runtime compile is gated
  on the compile APIs with build force-allow.
- `RenderResult.assets` filled from the active build manifest; injection deduped.
- First-load CSRF form/`hx-headers` tokens match the CSRF cookie
  (`csrf_token_for_request`).
- Unique HDN/css-symbol artifact paths from logical ids; style component ids honor
  `STYLE_COMPONENT_ID` when present.
- `hedron-disclose` uses `textContent` for labels, preserves light-DOM children, and
  rebuilds incomplete chrome cleanly.
- CLI hints when the registry is empty without `--app`; `eject` exits non-zero when
  nothing is written.
- `run_program` exported from the public `hedron` API; static mounts live in
  `hedron.static_mount` to avoid lifespan↔app circular imports.
- Explorer mounting follows `SecurityPolicy.explorer_enabled` unless `explorer=` is set.

[0.4.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.4.0
[0.3.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.3.0

## [0.2.0] — 2026-08-03

Initial FastAPI flagship distribution for the secure HTML/HTMX application MVP.

### Added

- Thin `Hedron(FastAPI)` facade with composable lifespan, security profiles,
  `session_secret` warnings/strict gating, Explorer modes, and bundled HTMX
  2.0.10 via `/hedron-static/` (`mount_hedron_static` for plain FastAPI).
- `HedronRouter` / `HedronRoute` with `@page`, `@component`, `@action`, and
  `include_component` for reusable `@addressable` descriptors; plain `HTML(...)`
  conversion on `HedronRoute`.
- Response helpers: `HTML`, `ComponentResponse`, `PageResponse`, `FragmentResponse`,
  `FileComponentResponse`, and `hedron_response`.
- HTMX page/fragment selection, history-restore PAGE mode, approved headers,
  `oob_swap` / trigger helpers, and safe targets.
- CSRF integration that reuses the cookie across GETs and accepts header or
  `csrf_token` form field; safe redirects; private authenticated caching;
  security header profiles.
- `SessionState[T]` via `session_state(key, model)` FastAPI dependency factory.
- OpenAPI `text/html` responses, deterministic operation IDs, and `x-hedron-*`
  metadata.
- Interaction built-ins: `AutoForm`, `RefreshButton`, `Lazy`, `Poll`,
  `InfiniteScroll`, `Pagination`, `Loading`, and retryable `ErrorState`.
- Minimal CLI: `hedron [--app module:attr] routes|components|preview`.
- Optional `hedron[dev]` Explorer preview via `hedron-explorer`.

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0
