# RFC-0078: Curated extras depth and lifecycle closure

**Status:** Accepted<br>
**Target phase:** 0.51 (`v0.51.0`)<br>
**Decision:** D-087<br>
**Stage 0 contract refine:** D-088<br>
**Planning baseline:** Published in-tree `v0.50.3` (D-088)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.50.3`<br>
**Tracking:** [#507](https://github.com/eddiethedean/hedron/issues/507)<br>
**Related:** [#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)
— companion 0.51 authoring; not extras gates<br>
**Extends:** RFC-0014, RFC-0021, RFC-0023, RFC-0025, RFC-0037, RFC-0038,
RFC-0051, RFC-0058, RFC-0060, RFC-0070, RFC-0072, RFC-0073

**Post-cut:** Stage 1 shipped in-tree `v0.51.0` (Git tag and PyPI upload
deferred; PyPI remains `v0.50.1`). Do not rewrite Stage 0 D-088.

**Revision:** 2026-08-19 — D-088 contract refine against Published in-tree
`v0.50.3`: planning baseline locked; inventory, descriptor, experimental
disposition, workbench, lifecycle, and companion-authoring locks recorded;
real `hedron_extras.plugin` / `hedron_extras.experimental` seams named.

Stage 1 added `hedron_extras_sandbox` / `HEDRON_EXTRAS_SANDBOX` opt-in
registration, `ExtrasFeature`, shared extras HTMX lifecycle, workbench depth,
and flagship #504–#506. Tracking
[#507](https://github.com/eddiethedean/hedron/issues/507) remains open for
tag/PyPI.

## Summary

Phase 0.51 turns `hedron-extras` into a genuinely curated package: each
Supported component is complete across server fallback, browser lifecycle,
accessibility, security, theming, testing, and upgrade, while Experimental
surfaces stay quarantined and are not pulled into `hedron[extras]`
transitively.

Companion HTMX authoring ([#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506))
ships on the flagship (RFC-0009 / RFC-0070 / RFC-0075). It does not graduate
Experimental UI and does not own extras gate IDs.

## Goals

- Inventory every extras component, event, asset, optional dependency,
  fallback, and enhancement as Supported, Experimental, Deprecated, or
  removed.
- Add a versioned `ExtrasFeature` descriptor as the package's single
  inventory authority, consuming today's `feature_specs` rather than
  forking `FeatureBundle` or `InteractionCatalog`.
- Standardize custom-element/HTMX connect, disconnect, reconnect,
  duplicate-registration, form, draft-state, focus-restoration, and cleanup
  on the shared element ABI.
- Bound JSON/Data/Chart workbenches: schemas, large-input behavior, action
  authority, cancellation, export, and server-rendered fallbacks. These are
  UI mechanics, not persistence or authorization policy.
- Decide Experimental UI individually: `CodeEditor`, `TerminalView`,
  joystick/device bridges, and `BrowserPythonSandbox` remain Experimental
  (see locked answers). Do not graduate host stubs.
- Keep optional features non-transitive and demand-loaded.
- Close or explicitly defer companion authoring #504–#506 on the flagship.

## Non-goals and exclusions

- Graduating `CodeEditor` with a pinned CodeMirror 6 bundle (RFC-0037 remains
  historical; the host stub stays Experimental).
- Graduating `TerminalView`, `Joystick`, or `DeviceBridge`.
- Pulling Experimental surfaces into Supported `hedron[extras]` workflows.
- Replacing `FeatureBundle`, `InteractionCatalog`, or `AccessibilityContract`.
- Owning 0.52 conformance / Node / Java evaluators.
- Owning 0.53 notebook / sim / sample-kit / `hedron package doctor`.
- Reopening `polling_only`, `MORPH-048`, Explorer 0.50, `SR-021`, or
  scheduling Hedron `1.0`.
- Inventing numeric limits, asset digests, or perf budgets in Stage 0.
- A WSGI-only extras runtime or Flask/Django `explorer_router` mount.

## Proposed design

### Consume shipped, do not fork

Stage 1 consumes these 0.50.3 symbols:

- `hedron_extras.plugin.register` / `PLUGIN_META` (`name="hedron_extras"`)
- `hedron_extras.experimental.register` / `PLUGIN_META`
  (`name="hedron_extras_experimental"`, `depends_on=("hedron_extras",)`)
- Entry points `hedron.plugins`: `hedron_extras`, `hedron_extras_experimental`
- Enablement: `hedron[experimental-ui]` plus `HEDRON_EXPERIMENTAL_UI=1` or
  explicit plugin enable; landmines omitted from default `__init__` exports
- `PluginMeta` / `PluginCapabilities` / `PluginContext.register_feature`
- In-plugin `feature_specs` names: `composition`, `workbench`,
  `image_tools`, `calendar`, `signature`, `typeahead`, `display`,
  `recipes`, `sandbox`
- Browser hosts: `hedron-extras-sandbox`, `hedron-extras-image-tools`,
  `hedron-extras-calendar`, `hedron-extras-signature`,
  `hedron-extras-typeahead`, `hedron-extras-composition`, plus experimental
  `hedron-extras-code-editor` / `hedron-extras-terminal`
- Optional extras: `json_editor`, `data_explorer`, `chart_workbench`,
  `image_tools`, `calendar`, `signature`, `typeahead`, `sandbox`,
  `code_editor`, `terminal`, `joystick`, `experimental-ui`, `all`
  (`hedron-data` + `hedron-charts` only)
- EXTRAS-025 quarantine
  ([extras-quarantine-025.toml](../acceptance/extras-quarantine-025.toml))
- Explorer panel `hedron-extras-features` (`path="/hedron-explorer/packages"`)
- Projection `hedron.extras` / diagnostic family `HED-EXTRAS-`
- 0.27 Supported extras slice
  ([production-grade-inventory-027.toml](../acceptance/production-grade-inventory-027.toml))
- Element ABI, `FeatureBundle`, `AccessibilityContract`, and
  `InteractionCatalog` as **projections**, not a second descriptor authority
- Flask/Django stay `projection_adapter` stacked on
  [adapter-disposition-044.toml](../acceptance/adapter-disposition-044.toml)
  and
  [host-portable-facts-045.toml](../acceptance/host-portable-facts-045.toml)

### `ExtrasFeature` descriptor

`ExtrasFeature` is additive and package-owned in `hedron-extras`. Portable
fields may sit next to plugin metadata. It covers component tag, Python
facade, schemas, events, assets, optional dependencies, fallback, limits,
maturity, accessibility contract, and Explorer/Jinja/conformance
projections. One descriptor per admitted feature is the inventory
authority. It does not live as a parallel catalog in `hedron-core` and
does not replace `FeatureBundle`.

Reserve `HED-EXTRAS-*` (already owned) and `HED-EXTRAS-FEATURE-*` in docs
only at Stage 0. Do not add runtime symbols.

### Workbench and input contracts

Editor/workbench primitives (undoable draft history, validation issue
navigation, import preview, apply/cancel, diff/export, cancellation,
restoration from a server-owned revision) are UI mechanics. The
application retains persistence, tenancy, and authorization.

Image transformation intents (crop/region/annotation) carry source
dimensions, normalized coordinates, revision preconditions, preview
limits, and server-confirmed output. Never evaluate code embedded in
JSON documents.

Virtualized/batched TreeView and Typeahead providers use stable
identities, abortable requests, race handling, empty/error/retry, and
ordinary paged/select fallbacks.

### Companion authoring (flagship)

| Issue | Deliverable |
|---|---|
| [#504](https://github.com/eddiethedean/hedron/issues/504) | Built-in password visibility toggle |
| [#505](https://github.com/eddiethedean/hedron/issues/505) | Declarative page reveal / swap transition helper |
| [#506](https://github.com/eddiethedean/hedron/issues/506) | Framework-level busy fallback for generic HTMX requests |

These stack on RFC-0009 / RFC-0070 / RFC-0075 and 0.50 authoring
primitives. They are **not** `INVENTORY-051`…`REGRESS-051`.

## Alternatives considered

1. **Graduate Experimental UI in 0.51.** Rejected: CodeEditor is a host
   stub without CodeMirror 6; specialty surfaces lack fail-closed evidence.
2. **Leave sandbox on the default plugin as `stability: beta`.** Rejected:
   [What’s ready](../guides/whats-ready.md) already labels it Experimental
   and `http_fallback` is false. Supported `hedron[extras]` must not pull
   it transitively.
3. **Put `ExtrasFeature` in `hedron-core` as a second catalog.** Rejected:
   extras remain a plugin package; consume `register_feature` /
   `FeatureBundle` projections.
4. **Defer companion #504–#506 to a later phase.** Rejected: ROADMAP already
   binds them to 0.51; they may close or explicitly defer, but they are
   in-phase.

## Security implications

Per-feature threat models for document editors, images, signatures,
clipboard/download, URLs, sandbox messages, terminal output, devices, and
high-frequency events. Strict-CSP / offline assets; no ambient remote
assets; no `eval` / dynamic module fetch; integrity-pinned vendored
assets. Sandbox stays origin-isolated with network deny. Experimental UI
stays behind `hedron[experimental-ui]`. Do not invent numeric byte/pixel
limits in Stage 0.

## Accessibility implications

Keyboard/touch parity, accessible names/instructions/status, non-spatial
alternatives, zoom/reflow, reduced motion, contrast, and error recovery
for composition, editor, signature, image, and typeahead surfaces.
`A11Y-051` is extras-owned evidence, not `SR-021` / human AT.

## Performance implications

Budgets for initial load, repeated HTMX swaps, large trees/options/
documents/images, and long-lived pages are Stage 1. Stage 0 reserves
names only.

## Testing strategy

Package-owned contract fixtures, no-JS fallback, three-engine browser,
adversarial cases, lifecycle leak checks, install isolation
(minimal / per-feature / all), and 0.50 upgrade/rollback. Gate scripts
`scripts/check_*_051.py` are Stage 1.

## Compatibility and migration

Public 0.50.3 extras imports and experimental quarantine stay. Moving
sandbox off default plugin registration is a Stage 1 compatibility
event documented in upgrade fixtures. Flask/Django stay projection
adapters. Pin strings `>=0.50.1,<0.51` stay until a 0.51 cut.

## Resolved questions (D-087)

1. **Which gates?** Closed inventory `INVENTORY-051`, `DESCRIPTOR-051`,
   `WORKBENCH-051`, `DATA-051`, `IMAGE-051`, `INPUT-051`,
   `LIFECYCLE-051`, `BROWSER-051`, `SECURITY-051`, `SUPPLY-051`,
   `A11Y-051`, `VISUAL-051`, `ECOSYSTEM-051`, `DOCS-051`, `PKG-051`,
   and `REGRESS-051`.
2. **Does 0.51 graduate CodeEditor?** No. Host stub; no CodeMirror 6.
3. **Does 0.51 graduate TerminalView / Joystick / DeviceBridge?** No.
   Remain `hedron[experimental-ui]`.
4. **Is sandbox Supported under `hedron[extras]`?** No. Experimental;
   Stage 1 makes default registration opt-in.
5. **What is the release baseline?** Verified in-tree `v0.50.3` before
   Stage 1 or the 0.51 cut. **D-088** locks the living/planning baseline
   to Published in-tree `v0.50.3`.

## Resolved questions (D-088)

1. **Does 0.51 still include all 16 extras gates?** Yes. Companion
   #504–#506 stay outside that matrix.
2. **Does this refine change a later phase or the living tip?** No.
   Cut target stays `v0.51.0`. Living tip remains `v0.50.3`. Do not
   reopen 0.50, `polling_only`, `MORPH-048`, `SR-021`, 0.52, 0.53, or
   schedule `1.0`.
3. **Which shipped seams does 0.51 consume?** Listed under Consume
   shipped. Do not fork `feature_specs` names or browser tags.
4. **Where does `ExtrasFeature` live?** `hedron-extras` (package-owned);
   not a `hedron-core` catalog replacement.
5. **Does EXTRAS-025 quarantine weaken?** No. XOR remains quarantine.
6. **What happens to sandbox `stability: beta` in `feature_specs`?**
   Honesty lock: Experimental. Stage 1 aligns registration and
   descriptors; Stage 0 does not change runtime.
7. **Do recipes become Supported components?** They stay `recipe`
   maturity unless the inventory promotes a named subset. They remain
   Supported *targets* for lifecycle/fallback evidence as recipes.
8. **Upgrade source for PKG-051?** **0.50** (`v0.50.3`), not 0.49.
9. **Reserve which diagnostics?** Keep `HED-EXTRAS-`; reserve
   `HED-EXTRAS-FEATURE-*` in docs only. Tracking
   [#507](https://github.com/eddiethedean/hedron/issues/507).
   In-tree Verified 0.50.3 is enough predecessor evidence; do not wait
   on PyPI/Git #501 assets.

Locks:
[extras-capability-inventory-051.toml](../acceptance/extras-capability-inventory-051.toml) ·
[extras-descriptor-051.toml](../acceptance/extras-descriptor-051.toml) ·
[extras-experimental-disposition-051.toml](../acceptance/extras-experimental-disposition-051.toml) ·
[extras-workbench-051.toml](../acceptance/extras-workbench-051.toml) ·
[extras-lifecycle-051.toml](../acceptance/extras-lifecycle-051.toml) ·
[extras-companion-authoring-051.toml](../acceptance/extras-companion-authoring-051.toml).

## Acceptance criteria

- RFC-0078 and D-087/D-088 are Accepted; tracking
  [#507](https://github.com/eddiethedean/hedron/issues/507) is bound.
- Stage 0 changes contracts only; no 0.51 runtime or version claim.
- Every 0.51-owned extras gate is Planned with an evidence command name;
  Stage 1 may not start until Verified in-tree 0.50.3 and this tracking
  issue exist.
- Experimental dispositions and sandbox honesty are named.
- Deferred items (`polling_only`, `MORPH-048`, `SR-021`, 0.52, 0.53)
  stay explicit.
