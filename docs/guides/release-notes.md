# Releases

This is the canonical adopter-facing release history. Package-level implementation
details remain in the [package changelogs](changelog.md).

## 0.60.1 — 2026-08-23

Release candidate for the 0.60 maintenance train. The coordinated packages are
versioned `0.60.1` in the repository and have passed the release gate and package
verification; PyPI remains at `0.60.0` until the upload is authorized and verified.

### Fixed

- Hardened path, URL, secret, serializer, upload, and MCP boundaries against traversal,
  scheme-smuggling, state pollution, and authorization regressions.
- Fixed `UploadFlow` route identity and authorization handling, including reliable
  multi-file result aggregation.
- Repaired data-source, transform, tree, pivot, import, spreadsheet, and collaboration
  integrity edge cases.
- Hardened chart transforms, limits, and redaction behavior.
- Isolated cache values and preserved native prepare-tree lifecycle semantics.

For maintainers, the release gate is `python scripts/check_release_gate.py 0.60.1`
and the package packet check is `python scripts/verify_pkg_60.py`.

## 0.60.0 — 2026-08-22

Verified and published release for the 0.60 train. The latest public install is
`hedron>=0.60.0,<0.61`.

### Custom theme platform

- Added typed absolute Color input, canonical immutable ThemeSpec/ThemePatch authoring, bounded
  recipe families, registry-derived validation, deterministic data-only packages, accessibility
  modes, server-first ThemePicker, and the read-only Explorer Theme Lab.
- Completed zero-application-CSS Brand, ToastHost, ConnectorFlow, and ScrollRegion contracts with
  narrow, print, reduced-motion, forced-color, and fallback behavior.
- Added the 27-gate release evidence packet and third-party conformance/reporting surfaces.

### Added

- CSS compiler format 2 compatibility, explicit container queries, theme variants, typed controls,
  bounded overlay placement, and preference-aware default CSS.
- Three-engine capability probes, contract fixtures, performance/package measurements, and a
  reviewable Data Mover migration evidence packet.

## 0.58.0 — 2026-08-21

Published cut for progressive feature and styling authoring (RFC-0085 /
D-101 / D-102 / D-105). The 0.58 train is available on PyPI; reproduce this
historical train with `hedron>=0.58.0,<0.60`. For current applications, use
`hedron>=0.60.0,<0.61`. [What’s new in 0.58](whats-new-0.58.md).
[Installation](../getting-started/installation.md).

### Added
- Beginner facades: `Hedron.screen`, `Hedron.form_command`, `DataWorkspace.with_screen`,
  `TaskFlow`, `DashboardWorkspace`, `SessionAuthFlow`, `UploadFlow`.
- `DesignSystem` brand/theme bridge, semantic `StyleRecipe` families, `StyleScope`,
  and unified `hedron explain` / `hedron style` tooling.
- FastAPI scaffolds `--template minimal|crud|dashboard|task`.

## 0.57.0 — 2026-08-21

In-tree Published cut for unified presentation / zero-application-CSS (RFC-0084 /
D-099 / D-100). The 0.57 PyPI upload remained **deferred**; the subsequent 0.58
train carried the public release. For current applications, use
`hedron>=0.60.0,<0.61`. [What’s new in 0.57](whats-new-0.57.md).
[Installation](../getting-started/installation.md).

### Added
- Shared appearance vocabulary, CSP-safe gap tokens, Grid/GridItem tracks and spans,
  Surface and AppShell chrome, ResourceList/Identity, FileUpload composition, and
  authenticated zero-application-CSS evidence (#558–#570).

### Fixed
- Map `tiles=` preserves restrictive `MapPolicy` fields; relative OSM tile URLs no longer
  forge the public CDN origin.
- Empty DataWorkspace `search_fields` stay deny-by-default; workspace identity reads
  `user_id` / `_user_id` without touching Starlette `request.user` unless present.
- CSS compiler excludes `@import` URLs from class rewrite and rejects `expression()` /
  `-moz-binding`; active-markup and chart scanners NFKC-normalize scheme/tag smuggling.
- Idempotency aborts on cancel and refuses empty streaming replay bodies; connection
  registry shares factory errors and locks reset/close.
- OIDC logout scheme matching, HTMX history-restore gating, Flask AuthSignal scope clear,
  trusted-proxy auth rate-limit IP, session CSRF require Request, Redis tag cleanup,
  Pagination `page_size >= 1`, MCP tool/resource authz fail-closed, and
  `HED-DATA-0010` for missing in-memory keys.

## 0.56.1 — 2026-08-21

Historical in-tree quality patch on the prior tip. Install from PyPI with
`hedron>=0.60.0,<0.61`. [What’s new in 0.56](whats-new-0.56.md).
[Installation](../getting-started/installation.md).

- Workspace Python quality upgrade: typing debt burn-down, safer best-effort exception
  logging, ASYNC/PTH/DTZ/RET ruff rules, and maintainability refactors without public API
  breaks.
- `fastapi-workbench` ships a `py.typed` marker.

## 0.56.0 — 2026-08-20

Security control plane tip (RFC-0083 / D-097 / D-098). **On PyPI** as `0.56.0`. Pin
`hedron>=0.60.0,<0.61`.
[What’s new in 0.56](whats-new-0.56.md).

## 0.55.0 — 2026-08-20

In-tree Published cut for secure upgradeable application workflows
(RFC-0082 / D-095 / D-096). Pin `hedron>=0.60.0,<0.61` from PyPI until the 0.55
wheel lands. [What’s new in 0.55](whats-new-0.55.md).
[Installation](../getting-started/installation.md).

- Master-detail layout, capabilities, replay-safe actions, multipart uploads,
  CSP reporting helpers, and offline upgrade reports (#544–#549).

## 0.53.0 — 2026-08-20

In-tree Published cut for application DX contracts
(RFC-0080 / D-091 / D-092). Pin `hedron>=0.60.0,<0.61` from PyPI until the 0.53
wheel lands. [What’s new in 0.53](whats-new-0.53.md).
[Installation](../getting-started/installation.md).

- Ordered application assets, version-aware diagnostics, structured route export,
  operation workflows, catalog testgen, semantic theming, API discovery, and
  installed-fleet doctor.

## 0.52.0 — 2026-08-20

Published cut for conformance authority and Posit lifecycle
(RFC-0079 / D-089 / D-090). **Git tag / PyPI LANDED** — `v0.52.0` is on PyPI.
Pin `hedron>=0.60.0,<0.61` from the public index (0.53 remains deferred).
[What’s new in 0.52](whats-new-0.52.md).
[Installation](../getting-started/installation.md).

- Cross-language portable-subset conformance authority (`hedron-conformance`) with
  profiles, fixture compiler, differential/platform evidence, and Node/Java evaluators.
- HedronPosit lifecycle companions: `CookieRegistry`, `PositContext`, `hands_off`,
  deployment-matrix check, diagnostics, and named-route query/fragment parity
  ([#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)).
- Tracking [#522](https://github.com/eddiethedean/hedron/issues/522).


## 0.51.2 — 2026-08-20

Quality and typing patch on the 0.51 train. Pin `hedron>=0.60.0,<0.61` from PyPI until the
0.51.2 wheel lands. [What’s new in 0.51](whats-new-0.51.md).
[Installation](../getting-started/installation.md).

- Replace runtime `assert` validation with explicit typed errors on chart adapters, Gradio
  client, hosts, and jobs.
- Typing ratchet on charts/maps/MCP/Jinja/Redis and host-integration modules (`handles`,
  pages, Explorer router).
- Fail-soft exception paths log at debug/warning; HDJ document-shape helpers extracted.

## 0.51.1 — 2026-08-20

Bugfix patch on the 0.51 train. Pin `hedron>=0.60.0,<0.61` from PyPI until a later
0.51.x wheel lands. [Installation](../getting-started/installation.md).

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
- Login CSRF, auth rate limiting, Flask CSRF for non-POST unsafe methods, Workbench cookie Path checks (#138, #139, #187, #160).
- Packaged asset paths cannot escape the static directory; simulator captions are HTML-escaped (#220, #204).

## 0.51.0 — 2026-08-19

Published curated extras cut. Install from PyPI with `hedron>=0.60.0,<0.61`.
[What’s new in 0.51](whats-new-0.51.md). [Installation](../getting-started/installation.md).

- `ExtrasFeature`, shared extras HTMX lifecycle, workbench/image/input depth.
- Sandbox default registration is opt-in (`hedron_extras_sandbox` / `HEDRON_EXTRAS_SANDBOX`).
- Flagship password toggle, swap reveal, and generic HTMX busy (#504–#506).

## 0.50.3 — 2026-08-19

Bugfix patch on the 0.50 train. Pin `hedron>=0.50.3,<0.51` for this in-tree tip.
[Installation](../getting-started/installation.md).

- `@command` no longer opts out of HTMX target authorization; compiled refresh/patch
  policies declare owned hosts and stay fail-closed.
- Secrets stay redacted in tabular normalize and secret columns; draft-transfer names
  tokenize forbidden fields; `redact_secret_like` no longer substring-matches.
- In-memory sort/filter/search deny-by-default; SQLAlchemy search uses `search_fields`;
  Great Tables HTML is sanitized; Three.js payloads require a verified size.
- Patch increment rejects bools; missing remove/delete fail closed; CSS brace checks
  ignore strings/comments; `process_image` keeps a 1px minimum height; collab merge
  conflicts insert vs delete.

## 0.50.2 — 2026-08-19

In-tree correctness and security patch on the 0.50 train. Git tag and PyPI upload
are **deferred**; pin `hedron>=0.50.2,<0.51` for this tip.
[Installation](../getting-started/installation.md).

- Login CSRF and OIDC state/nonce compare never 500 on length mismatch.
- OIDC `extra_params` cannot override protocol keys; logout redirect is allowlisted.
- Flask leftover session is not authenticated when flask-login says anonymous; CSRF
  stays on when the policy requires it; missing strategy fails closed.
- `include_component` rolls back Starlette routes; handle ownership and ActionHandle
  merge fail closed; FragmentHandle re-raises security/HTTP errors.
- HTMX 422 handlers retarget status chrome; missing `HX-Target` on `h-view-*` is 403;
  Explorer simulate rejects empty region lists.
- Django render honors `HEDRON_SECURITY_POLICY`; `include_component_path` forwards
  `request`; Flask cache-on-auth-error is private; `process_image` path jail; Redis
  SET requires MULTI; plugin specifier parse is `HED-PLUGIN-FAILED`.

## 0.50.1 — 2026-08-18

Bugfix patch on the 0.50 train. Pin `hedron>=0.50.1,<0.51`.
This version is on PyPI: [Installation](../getting-started/installation.md).

- Formula CSV/spreadsheet prefixes reject Unicode combining marks; `evaluate_formula` no longer coerces bool/junk to `0.0`.
- HTMX `hx-target="this"` is a closed relative keyword; control `id=` is accepted on Button/LinkButton/IconButton.
- Enabled TerminalView POST includes CSRF; Field*/Disclosure/Dialog frozen markup emit live attrs; ActionAsync accepts `hx-target`.
- Charts: tabular fallback, negative-Y SVG domain, GreatTables `supports()`, missing-extra pin `hedron[charts]>=0.50.1,<0.51`.
- Explorer: dashboard graph from `app.state`, packages render Hedron nodes, maps `plan_facts`, security AUDIT list; `hedron-explorer[fastapi]` matches FastAPI 0.141+.

## 0.50.0 — 2026-08-18

Explorer architecture and HTMX authoring cut. Pin `hedron>=0.50.0,<0.51`.
[Installation](../getting-started/installation.md).

- Command `effect` / `after`, history restore, Lazy error templates, dependent Select, and danger toast dismiss compile as documented.
- Explorer query/CLI envelopes replace silent caps; lab CSRF, diff baseline, and isolated `/packages` providers.
- Thin `explorer_router` plus services/views; frozen `/hedron-explorer/` mount.
- Additive `ExplorerProvider` v1 beside `ExplorerPanelMeta`.
- Cursor pagination and truncation diagnostics (`HED-EXPLORER-0001`).
- Headless CLI/HTML/JSON parity when `hedron-explorer` is installed; SARIF stays
  `diagnostics_to_sarif`.
- Bounded interaction lab and read-only package health.
- HTMX authoring primitives (#496–#500, #502, #503).

Pin this docs tree with `hedron>=0.50.0,<0.51`. Charts remain on
`hedron-charts>=0.2.0,<0.3`. Maps: `hedron[maps]` / `hedron-maps>=0.1.0,<0.2`.

## 0.49.1 — 2026-08-18

High-severity correctness and security patch for the 0.49 train. Prefer the 0.50.x pin
from PyPI `hedron>=0.60.0,<0.61` — [Installation](../getting-started/installation.md).

- Django `@hedron_view` validates CSRF before the handler (#392).
- Directory-upload paths reject raw CR/LF/TAB (#393).
- `hedron.Field()` and Pydantic tagged unions can register TypeSchema v2 (#394, #395).
- `Field(default_factory=...)` compiles as optional FastAPI params (#396).
- `DependsOn(streaming=True)` fail-closes without RESPONSE lifetime (#397).
- `data-hx-*` URLs receive the mount-path prefix (#398).
- Form-associated `hedron-field-*` elements no longer double-submit (#399).
- Flask session cookies set Secure when `FLASK_ENV=production` (#400).
- Flask and Django hosts run production security and durability gates (#401).
- Follow-up in-tree correctness/security fixes on this same `0.49.1` tip: CSRF UTF-8 compare, OutcomeMap/`generate_form`/button attrs, job cancel and SSE Last-Event-ID, MCP authz, Redis cache keyspaces, spreadsheet formula prefixes, chart asset schemes, map compile/proxy, and remaining open `bug` issues on the train (#254–#495).

Historical 0.49.1 in-tree pin was `hedron>=0.49.1,<0.50` (superseded; see 0.50.2 / 0.50.1 above).
Charts remain on `hedron-charts>=0.2.0,<0.3`.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
```

## 0.49.0 — 2026-08-17

In-tree FastAPI/Pydantic binding work. Prefer the 0.50.x pin
from PyPI `hedron>=0.60.0,<0.61` — [Installation](../getting-started/installation.md).

- FastAPI `Depends` compiles from Hedron `DependsOn` for handler and response scopes.
- Query, header, cookie, and non-file form models can bind as native Pydantic parameter models.
- TypeSchema v2 dual projections; v1 readers still work.
- Router provenance and typed OpenAPI projection; `RequiresScopes` remains non-granting.
- Workbench/Posit settings keep custom loaders.
- Bugfixes: query-only GET no longer 422s as JSON (#381); late registration fails closed (#382); required FormBody JSON is HTTP 415 (#383); TypeSchema sanitizer fail-closes unknown keys (#384).

Historical 0.49.0 in-tree pin was `hedron>=0.49.0,<0.50` (superseded; see the 0.50 install block above). Charts remain on
`hedron-charts>=0.2.0,<0.3`. Maps: `hedron[maps]` / `hedron-maps>=0.1.0,<0.2`.

<details markdown>
<summary>Maintainer identifiers</summary>

D-081 / D-084 / RFC-0076. New symbols begin Beta. `SR-021` stays open. Live-transport
maturity is unchanged (`polling_only`). `MORPH-048` stays Deferred. FailFast / Pydantic
`MISSING` / partial validation stay experimental (not Supported).
([#380](https://github.com/eddiethedean/hedron/issues/380)).

</details>

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[maps]>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.48.0 — 2026-08-17

Coordinated Beta cut for first-class HTMX extension integration (D-080 / D-083 / RFC-0075).

- Closed `HtmxExtension` / `ExtensionSet` / `Page.htmx_extensions` with demand-driven pinned local `sse`, `head-support`, and `preload` assets after HTMX core.
- Unset pages keep the 0.47 `sse` + `head-support` pair; `htmx_extensions=()` loads zero extension bytes. `preload` never rides the default.
- Typed `SseRegion` / `SseTrigger`. Polling remains the Supported fallback. SSE and preload helpers stay experimental.
- Registered `AssetRef` head merge; GET-only preload on `HtmxLink`. Idiomorph / morph swap is **Deferred**.
- New symbols begin Beta. `SR-021` stays open. Live-transport maturity is unchanged (`polling_only`).
- Pin the living tip with the 0.50.0 install block above. Charts remain on `hedron-charts>=0.2.0,<0.3`. Maps: `hedron[maps]` / `hedron-maps>=0.1.0,<0.2`.
- Head-support admits only local `AssetRef` hrefs, HTML-escapes them, and rejects quote/breakout/`..` values. Fragment inject rejects invented `<script>` tags (#374).
- Git tag `v0.48.0`, GitHub Release, and PyPI (`hedron` 0.48.0). Tracking [#373](https://github.com/eddiethedean/hedron/issues/373).
  Historical 0.48 pin (do not copy this constraint): `hedron>=0.48.0,<0.49`. Prefer the 0.50.1 block above.

## 0.47.0 — 2026-08-17

Coordinated Beta cut for first-class maps (D-078 / D-082 / RFC-0074).

- Independent Beta `hedron-maps` `0.1.0`: `MapSpec` / `MapPlan` / `compile_map`, `hedron_maps.Map`, OSM preset, custom/offline sources, `hedron-map` + MapLibre 5.6.1 strict-CSP, and `MapInteraction`.
- Core `hedron.Map` and charts MapLibre/Folium/PyDeck stay explicit and optional.
- New symbols begin Beta. Unused maps extra is request-path identical to 0.46. `SR-021` stays open.
- Historical cut; Git tag `v0.47.0`, GitHub Release, and PyPI (`hedron` 0.47.0). Tracking [#350](https://github.com/eddiethedean/hedron/issues/350).
  Install with the pin under **0.50.0** above.
  Charts remain on `hedron-charts>=0.2.0,<0.3`. Maps: `hedron[maps]` / `hedron-maps>=0.1.0,<0.2`.
- High-severity map origin, DataWorkspace paging/authz, MCP authorize, and MapInteraction POST fixes land in this 0.47 registry cut (#351–#357). `hedron-mcp` publishes **0.2.1** because **0.2.0** is already on PyPI.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[maps]>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.46.0 — 2026-08-16

Coordinated Beta train cut for package-native typed workflows (D-075 / D-079 / RFC-0073).

- Immutable `FeatureBundle` / `Hedron.include_feature` atomically register ordinary handles, components, scenarios, and stacked projections. Bundles are not executors.
- `DataWorkspace` / `DataWorkspacePolicy` compile list/detail/create/edit onto explicit authorized `DataEditorSource` surfaces. Never `.objects.all()`.
- `ChartInteraction` maps Supported `select` / `inspect` / `focus` / `reset` onto `ActionHandle` effects. Experimental chart kinds stay Experimental.
- Schema-aware elements are opt-in (`ActionHandle.form(enhance="elements")`). Native `ActionHandle.form()` remains canonical.
- `McpExposure` and `RemoteWorkflow` wrap live MCP/Gradio registration. Catalog presence never grants exposure.
- New symbols begin Beta. Unused `include_feature` is request-path identical to 0.45. `SR-021` stays open.
- Historical cut; Git tag `v0.46.0`, GitHub Release, and PyPI (`hedron` 0.46.0). Tracking [#334](https://github.com/eddiethedean/hedron/issues/334).
  Install with the pin under **0.50.0** above.
  Charts remain on `hedron-charts>=0.2.0,<0.3`.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.45.0 — 2026-08-16

Coordinated Beta train cut for the typed interaction ecosystem (D-074 / D-077 / RFC-0072).

- One sealed `InteractionCatalog` indexes 0.43 descriptors and optional 0.44 `TypeSchema` extensions.
- `hedron build` emits redacted sibling `interactions.json`; production validates it fail-closed when the catalog has entries.
- Namespaced `PackageProjection` values describe current data/charts/elements/extras surfaces. Direct APIs remain.
- FastAPI is the complete flagship; Flask/Django project portable facts and are not TypeSchema producers.
- MCP/Gradio consume catalog facts without auto-exposure. Catalog ids/fingerprints are not capabilities.
- New symbols begin Beta. Unused catalog is request-path neutral. `SR-021` stays open.
- Historical cut; install with the pin under **0.50.0** above.
  Charts remain on `hedron-charts>=0.2.0,<0.3`.
- In-tree cut only; Git tag / GitHub Release / PyPI remain deferred ([#328](https://github.com/eddiethedean/hedron/issues/328)).

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.44.0 — 2026-08-16

Coordinated Beta train cut for type-driven authoring, schema-derived forms, declared
effects, typed outcomes, and optional class handlers (D-072 / D-076 / RFC-0071).

- `ViewParams` / `FormBody` opt existing 0.43 handles into one Pydantic validator.
- `ActionHandle.form()` generates native forms for the closed field inventory.
- `Refreshes` / `Updates` declare effects; `OutcomeMap(case(...), ...)` maps results.
- Optional `RefreshableView` / `CommandHandler` classes compile to the same handles.
- New symbols begin Beta. Unmodeled 0.43 handlers remain unchanged.
- Historical cut; install with the pin under **0.50.0** above.
  Charts remain on `hedron-charts>=0.2.0,<0.3`.
- Generated-form CSRF tokens, `Field.alias` HTTP names, and FormBody JSON
  rejection land in this cut (#319, #320, #321).

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.43.0 — 2026-08-16

Coordinated Beta train cut for refreshable views, command handles, and typed updates
(D-071 / RFC-0070).

- `@app.refreshable` / `@app.command` return handles that own routes, hosts, and controls.
- `refresh()` and `Patch` / `PatchSet` compile into the existing `InteractionResult` / OOB stack.
- Low-level `region` / `swap` APIs remain supported. New symbols begin Beta.
- Pin `hedron>=0.60.0,<0.61`. Charts remain on `hedron-charts>=0.2.0,<0.3`.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.42.0 — 2026-08-14

Coordinated Beta train cut for browser composition, state, and navigation
(D-069 / RFC-0060).

- Ships allowlisted typed composition, subject-bound draft transfer, progressive
  navigation/restoration, content-free traces, and element/region failure isolation.
- Server and ordinary links/forms remain authoritative; optional preload/View Transitions
  never affect correctness.
- Historical cut; install with the pin under **0.50.0** above.
  Charts remain on `hedron-charts>=0.2.0,<0.3`.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.40.0 — 2026-08-14

Coordinated Beta train cut for Web Component authoring and interoperability
(D-068 / RFC-0060).

- Ships the public author kit (`hedron new element`), plugin element registration
  APIs, and HDJ / Explorer / theme / conformance metadata parity for element ABI.
- Publishes a React migration matrix with an Experimental island bridge as
  docs/reference only; optional in-repo `@hedron/elements` modules/TS types.
- Closes remediations #162, #203, #204, #219, #220, and #222.
- Historical cut pin `hedron>=0.40.0,<0.42`. Install with the pin under
  **0.50.0** above. Charts remain on `hedron-charts>=0.2.0,<0.3`.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.39.0 — 2026-08-14

Coordinated Beta train cut for rich data surfaces and OptimisticMutation
(D-067 / RFC-0060).

- Ships ABI-conforming `<hedron-data-editor>` with retained SSR fallback after
  upgrade, typed `OptimisticMutation` on bounded collection edits, and
  `compose_chartlink_039` so DataTable/DataEditor consume Published 0.38
  `hedron-chart` events without a parallel renderer.
- Records owned Experimental exceptions for map / media / code-editor /
  specialty surfaces; worker/object-URL abort and media Range streaming bounds.
- Closes tracking [#94](https://github.com/eddiethedean/hedron/issues/94) and the
  locked 27-issue rich-data remediation packet.
- Historical cut pin `hedron>=0.39.0,<0.40`. Install with the pin under
  **0.50.0** above. Charts remain on `hedron-charts>=0.2.0,<0.3`.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[data]>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.38.0 — 2026-08-14

Coordinated Beta train cut for first-party high-fidelity charts
(D-066 / RFC-0069).

- Ships Beta `hedron-charts` `0.2.0` with typed `ChartSpec` / `ChartPlan`, ABI
  `hedron-chart` (SVG default, Canvas for dense marks), and beginner
  `LineChart` / `AreaChart` / `BarChart` / `ScatterChart` compiled to the grammar.
- `MatplotlibChart` remains Supported; Plotly/Altair stay Experimental.
- Closes remediations #71, #72, #75, #81, #82, #83, #201, and #239.
- Historical cut pin `hedron>=0.38.0,<0.39`. Install with the pin under
  **0.50.0** above.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[charts]>=0.60.0,<0.61"
python -m pip install "hedron-charts>=0.2.0,<0.3"
```

## 0.37.0 — 2026-08-14

Coordinated Beta train cut for form-associated elements and interactive primitives
(D-065 / RFC-0060).

- Ships Alpha `hedron-elements` `0.37.0` with `hedron-field-text`,
  `hedron-field-choice`, `hedron-field-file`, `hedron-disclosure`, `hedron-dialog`,
  and `hedron-action-async` (`InteractionState`).
- Shared gesture/overlay catalog and HTMX form/validation matrices.
- Closes high-severity remediations #230–#237 and follow-on #244 (element-markup
  `style=` / dangerous URL schemes).
- Historical cut pin `hedron>=0.37.0,<0.39`. Install with the pin under
  **0.50.0** above.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
```

## 0.36.0 — 2026-08-13

Coordinated Beta train cut for Web Component ABI / lifecycle foundation
(D-064 / RFC-0060).

- Ships Alpha `hedron-elements` `0.36.0` with shared bridge and reference
  `hedron-example` (SSR/HTMX lifecycle; not form-associated).
- Versioned element registry, `ElementStateOwnership`, and `HED-ELEMENT-*` /
  `HED-ELEMENT-STATE-*` diagnostics.
- Fleet inventory-036 registers `hedron-elements` as incubator until the rephased 0.42 graduation.
- Historical cut pin `hedron>=0.36.0,<0.37`. Install with the pin under
  **0.50.0** above.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
python -m pip install "hedron[elements]>=0.60.0,<0.61"
```

## 0.35.0 — 2026-08-13

Coordinated Beta train cut for whole-fleet production-grade closure
(D-063 / RFC-0068).

- Publishes fleet inventory `production-grade-inventory-035.toml` with dispositions
  for every publishable package/runtime.
- Tooling packages (notebook, sample-kit, sim, runtimes) reconciled to Beta tooling-grade.
- PRESENT-034 default presentation gallery remains deferred/experimental.
- Historical cut pin `hedron>=0.35.0,<0.36`. Install with the pin under
  **0.50.0** above.

## 0.34.0 — 2026-08-13

Coordinated Beta train cut for production-grade Gradio / Hugging Face client
interop (D-062 / RFC-0067).

- Ships `hedron-gradio` `0.2.0` Beta: allowlisted remote predict/stream, bounded
  files, scoped jobs, HF Space vendor helpers.
- Coordinated `hedron` / core packages `0.34.0`; `fastapi-workbench` stays `1.x`;
  MCP stays satellite `>=0.2.0,<0.3`.
- Default presentation gallery (`PRESENT-034`) deferred to whole-fleet `0.35` audit.
- Historical cut pin `hedron>=0.34.0,<0.35`. Install with the pin under
  **0.50.0** above.

## 0.33.0 — 2026-08-13

Coordinated Beta train cut for unified Posit Workbench / Connect adapter
(D-061 / RFC-0066).

- Ships `hedron-posit` `0.33.0` Beta: `HedronPosit` + `PositConfig` / native Connect.
- `hedron-workbench` `0.33.0` remains a Supported compatibility package (≥0.35).
- Supported cookie bridge dropped after Stage 0 (`BRIDGE_DECISION=drop_supported`).
- Coordinated `hedron` / core packages `0.33.0`; `fastapi-workbench` stays `1.x`;
  MCP stays satellite `>=0.2.0,<0.3`.
- Historical cut pin `hedron>=0.33.0,<0.34`. Install with the pin under
  **0.50.0** above.

## 0.32.0 — 2026-08-12

Coordinated Beta train cut for production-grade deny-by-default MCP projection
(D-060 / RFC-0065).

- Ships `hedron-mcp` `0.2.0` Beta: authenticated Streamable HTTP projection;
  Supported inventory only; mutations remain Experimental.
- Coordinated `hedron` / core packages `0.32.0`; MCP stays satellite `>=0.2.0,<0.3`.
- Security hardening: session-bound MCP principals, formula-injection evasion strip,
  optional-session scope gates, MCP cancel/session lifecycle bounds.
- Historical cut pin `hedron>=0.32.0,<0.33`. Install with the pin under
  **0.50.0** above.

## 0.31.0 — 2026-08-12

Coordinated Beta train cut for tooling-grade developer/portable conformance and the
Streamlit AST migrator (D-059 / RFC-0064 / RFC-0061).

- Tooling-grade `hedron-conformance`, `hedron-sample-kit`, `hedron-sim`, `hedron-notebook`.
- Published Node/Java evaluators (`hedron-runtime-node` / `hedron-runtime-java` `0.31.0`).
- `hedron migrate streamlit` non-executing AST assistant.
- Historical cut pin `hedron>=0.31.0,<0.32`. Install with the pin under
  **0.50.0** above.

```bash
python -m pip install -U "hedron>=0.60.0,<0.61"
hedron migrate streamlit streamlit_app.py --analyze-only --format text
```

## 0.30.0 — 2026-08-12

Coordinated Beta train cut for standalone Workbench package extraction (D-058 /
RFC-0063).

- Ships monorepo-owned `fastapi-workbench` `1.0.0` for plain FastAPI Posit Workbench /
  RStudio Server deployment without installing Hedron.
- `hedron-workbench` `0.30.0` depends on `fastapi-workbench>=1.0.0,<2.0` and delegates
  generic resolver / middleware / runner behavior.
- Historical cut pin `hedron>=0.30.0,<0.31`. Install with the pin under
  **0.50.0** above.

Historical cut used `hedron` / `hedron-workbench` on the 0.30 train and
`fastapi-workbench>=1.0.0,<2.0`. Prefer the pin under **0.50.0** above.

## 0.29.0 — 2026-08-11

Coordinated Beta train cut for production-grade `hedron-workbench`.

- Ships optional `hedron[workbench]` / `hedron-workbench`: Posit Workbench /
  RStudio Server launcher that exports `HEDRON_ROOT_PATH` before import.
- Hedron-neutral polish: `Hedron(root_path=...)`, re-exported
  `resolve_mount_path_from_environ`, color-mode cookie Path.
- No auto-activation on install/import/`RS_SERVER_URL`. Flask/Django unchanged.
- Historical cut pin `hedron>=0.29.0,<0.30`. Install with the pin under
  **0.50.0** above.

## 0.28.2 — 2026-08-11

Coordinated Beta patch on the 0.28 train.

- Raises coordinated package versions / pins to `0.28.2` (historical cut pin
  `>=0.28.2,<0.29`).
- Aligns `hedron new` scaffolds and the published-quickstart release checker on
  `docs/release.toml` `pin_floor` (fixes the v0.28.1 release verify footgun).
- HTMX/OOB hardening: validated OOB swaps, select_oob conflict fail-closed,
  landmark-safe `HtmxLink` default `innerHTML`, FastAPI fragment-target auth parity,
  Flask/Django `allow_htmx_eval` + PAGE asset inject, portable Django CSRF header.
- Chart hosts listen for OOB/load lifecycle events; Plotly/Vega generation guards;
  MapLibre `coord_order`; tip `hedron-charts` `0.1.11` (floor `>=0.1.10`).
- GitHub Release create waits on quickstart verify and omits plain `linux_*` wheels.
- No Supported CRUD/admin API removal.

Install with the pin under **0.50.0** above (historical cut pin was
`>=0.28.2,<0.29`).

## 0.28.1 — 2026-08-10

Correctness and tip-honesty patch for the 0.28 train.

- Raises the `hedron[native]` floor and wires Supported native wheel publish evidence.
- Fixes Auto Experimental remediation, optional chart HTMX dispose, Flask/Django
  mount-aware static prefixes, and live `HEDRON_NATIVE_DISABLE`.
- Hardens tip-hub SSOT wrap scans and CI native/crates publish footguns.

Install with the pin under **0.50.0** above (historical cut pin was
`>=0.28.1,<0.29`).

## 0.28.0 — 2026-08-10

Hedron 0.28.0 graduates charts and optional native acceleration inventories.

- Publishes a machine-checked production-grade inventory for `hedron-charts` and
  `hedron-native` (D-056 / RFC-0059).
- Matplotlib/static beginner charts are Supported; Plotly/Altair remain Experimental
  and are excluded from production Auto defaults.
- Optional Rust escape acceleration ships with `HEDRON_NATIVE_DISABLE` fallback and a
  Supported wheel matrix.
- Charts `0.1.9` and native `0.1.2` leave Alpha for declared Supported scopes.

No Supported CRUD/admin API removal is listed. Polling remains the production path for
live status; SSE, WebSocket, streaming, and preload remain experimental.

## 0.27.0 — 2026-08-10

Hedron 0.27.0 graduates data, Flask/Django, HDJ, and curated extras inventories.

- Publishes a machine-checked production-grade inventory for `hedron-data`,
  `hedron-flask`, `hedron-django`, `hedron-jinja`, and `hedron-extras`.
- Validates upgrades from Published `v0.26.0` across satellite public contracts.
- Verifies host-only Flask/Django/data/HDJ/extras smokes and portable PAGE/FRAGMENT
  parity.
- Scopes `hedron check` Django / Plotly-Altair notices to detected adapters and chart
  extras (`#54`); injects HTMX before bundled extensions on PAGE responses (`#55`);
  warns on `select_oob` + `OobUpdate` same-target conflicts and defaults `OobUpdate`
  swaps to `innerHTML` (`#57`).
- Mounts `/hedron-static` and injects shared PAGE assets on Flask and Django like
  FastAPI.

No Supported CRUD/admin API removal is listed. Polling remains the production path for
live status; SSE, WebSocket, streaming, and preload remain experimental.

Install with the pin under **0.50.0** above.

Read [Upgrade to 0.38](upgrade.md) before changing a production lockfile. Maintainer
evidence identifiers and packets are linked from [What’s new in 0.27](whats-new-0.27.md).

## 0.26.1 — 2026-08-10

Correctness and adoption-readiness patch for the 0.26 train.

- Fixes Explorer navigation, component-detail, and static-asset links when Hedron is
  mounted under a subpath (for example reverse-proxy `/app`), and requires
  `hedron-explorer>=0.26.1` from the `dev` extra.
- Fixes `hedron new`, `hedron new --flask`, and `hedron new --django` to generate the
  then-current `>=0.26.0,<0.27` dependency range rather than the obsolete 0.25 range.
- Repairs optional-integration install commands and package-index links.
- Replaces the abbreviated OIDC outline and model-demo stub with tested, runnable
  application flows.
- Reorganizes documentation around tasks, adds an actual 5-minute quick start and
  0.25.2→0.26 upgrade guide, and makes release/maturity/support claims consistent.
- Adds CI enforcement for release-train metadata, API export coverage, documentation
  ownership, generated pages, PyPI-safe package links, and scheduled external links.
- Adds checksummed release manifests, versioned evidence metadata, documentation-version
  guidance, and an exact-PyPI quick-start gate before GitHub Release creation.

No Supported API removal is included. Existing 0.26.0 applications can upgrade within
their bounded 0.26 train pin.

## 0.26.0 — 2026-08-10

Hedron 0.26.0 strengthens the Supported CRUD/admin path.

- Publishes a machine-checked inventory of Supported, Experimental, and excluded
  surfaces for `hedron-core`, `hedron`, and `hedron-explorer`.
- Validates upgrades from 0.25.2 across facade identities, diagnostics, manifests, and
  HTMX interactions.
- Verifies secured Explorer behavior and refusal of development Explorer in production.
- Verifies the documented FastAPI multi-worker, Redis, and reverse-proxy deployment
  pattern.

No Supported CRUD/admin API removal is listed. Polling remains the production path for
live status; SSE, WebSocket, streaming, and preload remain experimental.

Historical pin for this train: `hedron>=0.26.0,<0.27`. See
[Upgrade](upgrade.md) / [What’s new in 0.50](whats-new-0.50.md).

## 0.25.2 — 2026-08-10

Security and correctness patch for fragment authorization, CSRF cookies, mount paths,
Redis job/status state, adapter lifecycle handling, and streaming cache headers.

## 0.25.1 — 2026-08-09

Restored a resolvable charts extra, repaired adopter recipes, and hardened the release
workflow so failed PyPI publication cannot create a GitHub Release.

## 0.25.0 — 2026-08-09

Added the production reference-app archetype, critical-path budgets, explicit
experimental-UI quarantine, and release evidence assets.

## Earlier releases

Use the [release archive](whats-new-archive.md) for 0.10–0.24. The project does not
rewrite historical release pages to describe current maturity; use
[What’s ready today](whats-ready.md) for present-day capability claims.
