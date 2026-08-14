# Web Component platform acceptance

**Planning status:** RFC-0060 **Accepted** (D-064); phases 0.36–0.42. Phase **0.36** is
**Published** (`v0.36.0`; all owned gates Verified) — see [`RELEASE_0_36.md`](RELEASE_0_36.md) and
[`release-gate-0.36.toml`](release-gate-0.36.toml). Phase **0.37** is **Published**
(`v0.38.0`; all owned gates Verified) — see [`RELEASE_0_37.md`](RELEASE_0_37.md) and
[`release-gate-0.37.toml`](release-gate-0.37.toml). Phase **0.38** high-fidelity charts has a
refined Planned packet under RFC-0069 / D-066. Later phases (0.39–0.42) remain draft until their
own Stage 0 packets land.
Renumbered from 0.34–0.39 to 0.35–0.40 by D-058, then to 0.36–0.41 by D-061. D-066 inserts charts
at 0.38 and moves the former 0.38–0.41 capabilities to 0.39–0.42 without scope loss.
The exact five interaction protocols are defined in the
[interaction-contract specification](../implementation/WEB_COMPONENT_INTERACTION_CONTRACTS.md).

Unchecked requirements are future release gates, not claims about the current 0.38 train. Each
phase requires a `release-gate-0.N.toml` index, retained evidence under the release evidence policy,
and zero Deferred rows among that phase's owned gates at cut.

## Evidence matrix used by every phase

Every gate below must name exact commands, owners, supported browser/host/package matrices, retained
artifacts, time/size limits, and failure disposition before it may become Verified.

| Dimension | Minimum evidence |
|---|---|
| Functional | Pre-upgrade, successful upgrade, reconnect, outer/inner/OOB swap, history, and failed-module behavior |
| Security | CSP, Trusted Types, escaping/payload bounds, event spoofing, URL/HTML sinks, origin/assets, version skew, dependency audit |
| Accessibility | Native semantics, name/role/state/value, keyboard/focus, forms/errors, zoom/reflow, forced colors, reduced motion, localization, fallback |
| Browser | Supported Chromium, Firefox, and WebKit versions with JavaScript on/off, slow/failing modules, and HTMX lifecycle |
| Performance | Route asset inventory, compressed sizes, upgrade/swap timings, long tasks/layout shift, and repeated-cycle leak evidence |
| Compatibility | ABI/schema fixtures, mixed package/module versions, upgrades, rollback, and unknown/incompatible feature behavior |
| Portability | FastAPI, Flask, Django, Python rendering, HDJ where owned, and portable conformance fixtures |
| Supply chain | Local/fingerprinted assets, source/build mapping, SBOM, provenance, licenses, vulnerabilities, and rollback |
| Documentation | Public contract, fallback, limitations, stability, examples, migration, diagnostics, and Supported/Experimental claims agree |

## 0.36 — Element ABI and lifecycle foundation

Evidence index: [`release-gate-0.36.toml`](release-gate-0.36.toml). Acceptance packet:
[`RELEASE_0_36.md`](RELEASE_0_36.md). Reference element: **`hedron-example`**.
`BROWSER-036` “100 elements” means **100 upgrade/swap cycle instances** of that reference
element, not 100 distinct tag types.

### `ABI-036`

Command (at Verified): `python scripts/check_abi_036.py`

- [ ] The element registry schema covers tag/module/ABI identity, attributes, structured inputs,
  properties/methods, typed events, DOM ownership, forms (**metadata stub**), accessibility, styles, resources,
  lifecycle, and fallback.
- [ ] Duplicate same-definition registration is idempotent; tag or ABI conflicts fail visibly
  before use and preserve server-rendered content.
- [ ] Compatible and incompatible server/module combinations have immutable fixtures and
  `HED-ELEMENT-*` diagnostics with no payload leakage.
- [ ] The `hedron-` first-party namespace and third-party naming rules are machine-checked.
- [ ] Frozen markup attributes (`data-hedron-abi`, `data-hedron-element`,
  `data-hedron-server-region`, structured-input encoding) match
  [WEB_COMPONENT_PLATFORM.md](../implementation/WEB_COMPONENT_PLATFORM.md).

### `ELEMENTS-036`

Command (at Verified): `python scripts/check_elements_036.py`

- [ ] `hedron-elements` builds and installs as a framework-neutral wheel with no Node.js required by
  a consuming FastAPI, Flask, or Django application.
- [ ] One representative light-DOM element (`hedron-example`) exercises Python rendering, registry discovery, local
  module/CSS assets, typed events, Explorer metadata, and all three hosts.
- [ ] Pure `hedron-core` rendering remains deterministic when browser assets are not mounted.

### `LIFECYCLE-036`

Command (at Verified): `python scripts/check_lifecycle_036.py`

- [ ] Connect/reconnect is idempotent; disconnect and HTMX early cleanup release all declared
  listeners, observers, timers, workers, object URLs, requests, focus traps, and adapter handles.
- [ ] At least 100 outer swaps, inner authorized swaps, OOB swaps, and history save/restore cycles
  produce no duplicate handlers and no retained-instance/resource growth beyond the recorded bound.
- [ ] Module timeout/failure, initialization exception, removed-before-load, and reconnect races
  restore or preserve useful fallback content.

### `SSR-036`

Command (at Verified): `python scripts/check_ssr_036.py`

- [ ] The representative element is understandable and completes its documented fallback workflow
  before upgrade, with JavaScript disabled, and after module/ABI failure.
- [ ] Structured configuration uses a declared inert/property path with contextual escaping and
  byte/item/depth limits; malicious closing tags, HTML, URLs, and oversized inputs fail safely.
- [ ] Server-owned and element-owned DOM regions are disjoint and machine-audited.

### `STATE-036` — `ElementStateOwnership`

Command (at Verified): `python scripts/check_state_036.py`

- [ ] Every mutable field declares `controlled`, `local`, `draft`, or `preference` ownership plus
  reflection, incoming-update, persistence, limit, and event policy; capabilities/server authority
  cannot use an element-owned mode.
- [ ] Controlled programmatic updates do not emit user-intent loops; local state is disposable;
  draft state tracks schema/base revision/dirty fields and explicit submit/discard/conflict behavior.
- [ ] Dirty-draft incoming updates exercise replace, preserve, proven typed rebase, and conflict;
  unsafe/unspecified merge defaults to visible conflict rather than last-write-wins or silent loss.
- [ ] Ownership violations and illegal persistence emit redacted `HED-ELEMENT-STATE-*` diagnostics
  while useful server fallback remains available.
- [ ] Cross-instance draft **transfer** is out of scope until phase 0.41.

### `SECURITY-036`

Command (at Verified): `python scripts/check_security_036.py`

- [ ] Strict CSP and Trusted Types enforcement pass without inline handlers, eval, remote runtime
  fetches, undeclared executable assets, or unsafe HTML construction.
- [ ] Event details are schema-validated, contain no capability/secret/DOM/executable values, and
  remain untrusted under CSRF/authn/authz/tenant/server validation.

### `A11Y-036`

Command (at Verified): `python scripts/check_a11y_036.py`

- [ ] Pre-upgrade, upgraded, failed-upgrade, swap, and history states pass semantic, keyboard, focus,
  axe/ACT, zoom, forced-colors, reduced-motion, and localization checks.

### `BROWSER-036`

Command (at Verified): `python scripts/check_browser_036.py`

- [ ] Chromium, Firefox, and WebKit run the same lifecycle/fallback corpus on the declared browser
  floor; unsupported versions receive a usable fallback and explicit support message.
- [ ] The shared bridge is at most 12 KiB gzip; unused rich adapters do not load; **100 upgrade/swap
  cycle instances** of `hedron-example` meet the recorded upgrade/swap/long-task/layout-shift budget.

### `PKG-036`

Command (at Verified): `python scripts/verify_pkg_36.py`

- [ ] Clean wheels, source maps, manifests, SBOM/provenance/licenses, docs, and release verifier pass.

## 0.37 — Form-associated controls and semantic primitives

Evidence index: [`release-gate-0.37.toml`](release-gate-0.37.toml). Acceptance packet:
[`RELEASE_0_37.md`](RELEASE_0_37.md). Reference elements: **`hedron-field-text`**,
**`hedron-field-choice`**, **`hedron-field-file`**, **`hedron-disclosure`**, **`hedron-dialog`**,
**`hedron-action-async`**. **`hedron-example`** remains non-form.

### `FORM-037`

Command (at Verified): `python scripts/check_form_037.py`

### `VALIDITY-037`

Command (at Verified): `python scripts/check_validity_037.py`

### `PRIMITIVE-037`

Command (at Verified): `python scripts/check_primitive_037.py`

### `ACTIONSTATE-037` — `InteractionState`

Command (at Verified): `python scripts/check_actionstate_037.py`

### `INTERACT-037` — `GestureOverlayCatalog`

Command (at Verified): `python scripts/check_interact_037.py`

### `HTMX-037`

Command (at Verified): `python scripts/check_htmx_037.py`

### `AT-037`

Command (at Verified): `python scripts/check_at_037.py`

### `REGRESS-037` / `PKG-037`

Command (at Verified): `python scripts/check_regress_037.py` / `python scripts/verify_pkg_37.py`

### `FORM-037` / `VALIDITY-037` (requirements)

- [ ] Named single- and multi-value controls submit identical values through ordinary navigation,
  HTMX, and supported hosts, including disabled, reset, restore, repeated-name, and empty states.
- [ ] `ElementInternals` behavior and native fallback cover label/description, required/readonly,
  validity reporting, server-returned field errors, autofill expectations, and form reset/restore.
- [ ] CSRF, request size, authorization, and business validation remain server-owned; client
  validation cannot suppress a server error or authorize a mutation.
- [ ] File/directory controls retain browser objects only within bounded user-initiated flows and
  pass upload type/size/path/cancel/cleanup adversarial cases.

### `PRIMITIVE-037` (requirements)

- [ ] A locked catalog selects only primitives with material browser-local behavior; ordinary links,
  buttons, fields, layout, and landmarks remain native when custom elements add no value.
- [ ] Disclosure/dialog/tabs/menu-popover/selection primitives in scope retain semantic fallback,
  keyboard conventions, focus entry/exit/restore, and HTMX fragment behavior.
- [ ] Native platform features are used when they meet the contract; polyfills/adapters are local,
  conditional, inventoried, and removable.

### `ACTIONSTATE-037` — `InteractionState` (requirements)

- [ ] All element-owned async operations use `idle`, `pending`, `success`, `error`, and `canceled`
  with bounded progress, opaque operation correlation, timestamps/durations, and safe status/error
  codes; components do not invent incompatible loading flags.
- [ ] `drop`, `replace`, bounded `queue`, and bounded `parallel` concurrency policies pass request,
  late-response, retry, timeout, disconnect, and duplicate-intent scenarios with no unbounded queue.
- [ ] HTTP `202`, polling/job completion, browser abort, and acknowledged server cancellation remain
  distinct; no UI reports canonical success/cancellation before the server contract does.
- [ ] Pending/progress/error/retry/cancel states preserve native form fallback, focus, `aria-busy`,
  restrained announcements, reduced motion, and JS/module-failure completion paths.

### `INTERACT-037` — `GestureOverlayCatalog` (requirements)

- [ ] Reorder/drag-drop, resize/splitter, pointer capture, keyboard equivalence, touch/scroll/RTL,
  reduced-motion, Escape/cancel, target allowlists, and disconnect cleanup share catalog fixtures.
- [ ] Pointer and keyboard paths emit the same typed intent using stable item/position identities;
  payloads reject DOM nodes, selectors, arbitrary MIME/path/HTML/URL values, and direct server edits.
- [ ] Dialog, popover/menu, combobox/listbox popup, tooltip/help, command palette, and toast/status
  entries declare native/fallback implementation, focus/dismissal/nesting/inert/anchor/viewport/swap
  behavior, DOM ownership, keyboard map, and essential-information fallback.
- [ ] Command surfaces invoke registered routes/actions under ordinary authz/CSRF validation;
  tooltips/toasts never become the sole essential instruction, error, or completion record.

### `HTMX-037` / `AT-037` / `REGRESS-037` / `PKG-037` (requirements)

- [ ] Controls survive inner/outer/OOB swaps, 422 validation fragments, duplicate submission,
  retarget/reselect, history restore, and slow/canceled requests without lost errors or stale state.
- [ ] Representative keyboard-only and screen-reader sessions cover fallback and upgraded form
  completion; findings are remediated or explicitly dispositioned without application WCAG claims.
- [ ] Cross-host forms, browser matrix, performance/leak, compatibility, docs, clean install, and
  package evidence pass with zero Deferred 0.37 rows.
- [ ] Open high-severity issues #230–#237 are closed (`REGRESS-037`; see
  [RELEASE_0_37](RELEASE_0_37.md) remediations table).

## 0.38 — High-fidelity declarative charts

Normative acceptance: [`RELEASE_0_38.md`](RELEASE_0_38.md). Evidence index:
[`release-gate-0.38.toml`](release-gate-0.38.toml). Design:
[RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md).

- [ ] `hedron-chart` is an ABI-conforming, lifecycle-safe Web Component that upgrades a useful
  semantic figure/summary/table/export fallback and owns no application authorization.
- [ ] Typed `ChartSpec` / deterministic `ChartPlan`, modular pinned D3, SVG/Canvas rendering,
  publication-quality design, typed interaction, accessibility, performance, export, visual
  review, security, compatibility, documentation, and packaging satisfy all thirteen 0.38 gates.
- [ ] The chart-scoped Python/spec/element contract may become Supported for `hedron-charts` 0.2
  without promoting unrelated element tags or the general author ABI before 0.42.

## 0.39 — Rich data and visualization convergence

### `DATA-039`

- [ ] DataTable/DataEditor adapters use the common element ABI for configuration, typed edits,
  selections, validation, paging/virtualization, saved views, fallback tables/forms, and teardown.
- [ ] Local pending edits have explicit submit/discard/conflict/swap/history behavior and never
  widen source authorization or tenant filters.

### `OPTIMISTIC-039` — `OptimisticMutation`

- [ ] Each optimistic mutation declares registered action, base revision, typed forward patch,
  deterministic inverse or canonical refetch, idempotency/replay, affected region, limits, and
  timeout/retry/cancel/rejection/conflict behavior; server-confirmed rendering remains the default.
- [ ] Proposed/submitted/confirmed/rejected/rolled-back/conflicted scenarios pass success, 4xx/5xx,
  validation, lost/late/duplicate response, disconnect/history, concurrent writer, and refetch tests.
- [ ] Auth/permission, irreversible destructive, payment, secret, publication, cross-tenant, and
  non-recoverable mutations reject optimism unless a later accepted risk-specific contract exists.
- [ ] Patches obey typed property/collection allowlists and reject HTML, selectors, executable
  values, arbitrary URLs/object paths/DOM targets; server canonical output may differ and wins.
- [ ] Pending, rollback, and conflict are announced without color/motion-only cues or focus theft;
  reconnect resolves by operation/revision or canonical refetch rather than assuming rollback.

### `CHARTLINK-039`

- [ ] DataTable/DataEditor cross-filtering and rich-surface composition consume the 0.38
  `hedron-chart` event, selection, fallback, export, and lifecycle contracts without creating a
  parallel renderer or vendor-default path.
- [ ] Accessible chart summaries remain available during optimistic data/editor states and
  cross-surface failure; Canvas/SVG does not erase title, description, data summary, keyboard
  alternative, or export fallback.

### `RICH-039` / `WORKER-039`

- [ ] Map, media/capture, code/editor, and eligible specialty surfaces adopt the shared ABI or retain
  an explicit Experimental exception with owner and destination.
- [ ] Workers, WASM, object URLs, observers, media streams, third-party runtimes, and large buffers
  are declared, bounded, cancelable, and fully disposed on swap/disconnect/failure.
- [ ] Third-party adapters cannot target undeclared origins, inject untrusted HTML, or bypass the
  element/server event and action contracts.

### `PERF-039` / `A11Y-039` / `REGRESS-039` / `PKG-039`

- [ ] Representative large data/chart/map scenarios meet surface-specific response, interaction,
  memory, worker, long-task, layout-shift, and route-asset budgets on documented hardware/data.
- [ ] Rich surfaces pass keyboard, screen-reader automation, zoom/reflow, forced colors, reduced
  motion, fallback, and swap-state matrices; limitations remain explicit.
- [ ] Existing component imports and server markup have upgrade fixtures; no rich adapter becomes a
  transitive/default asset merely because it implements the common ABI.

## 0.40 — Authoring, interoperability, and ecosystem

### `AUTHOR-040` / `PLUGIN-040`

- [ ] A third-party author kit defines typed metadata/events, DOM ownership, lifecycle/fallback,
  asset/resource disclosure, tests, diagnostics, compatibility, and packaging without private APIs.
- [ ] `hedron new element` (or accepted equivalent) scaffolds Python wrapper, module, CSS, examples,
  contract tests, browser tests, accessibility metadata, and build configuration.
- [ ] An externally built consumer plugin proves discovery, disable/uninstall, conflict errors,
  manifests, Explorer, clean install, and no host-framework dependency leakage.

### `HDJ-040` / `THEME-040`

- [ ] HDJ can use registered custom elements as standards-based markup while its static prologue
  declares modules, feature/ABI requirements, events/actions, and fragment regions.
- [ ] Light-DOM scoped styles and Shadow-DOM tokens/parts/slots have documented stable customization
  boundaries; applications do not depend on private shadow structure.
- [ ] Theme changes, color modes, forced colors, reduced motion, and print/export paths work without
  redefining elements or an application JavaScript build.

### `EXPLORER-040` / `CONF-040` / `SUPPLY-040` / `PKG-040`

- [ ] Explorer displays and simulates fallback/upgrade/failure, ABI, attributes/properties/events,
  forms, DOM ownership, slots/parts/tokens, assets, lifecycle, performance, and accessibility.
- [ ] Portable positive/negative fixtures allow third-party and Node/Java evaluators to validate
  element metadata, markup, events, manifests, and compatibility without implementing a browser.
- [ ] If `@hedron/elements` is published, npm and wheel modules have matching content identity,
  version/provenance/license/SBOM policy and reproducible consumer tests.
- [ ] Documentation clearly separates the supported Python-host workflow from any standalone npm
  scope; clean author and consumer packages pass with zero Deferred 0.40 rows.

### `MIGRATE-040` — `ReactMigrationMatrix`

- [ ] The React matrix maps components/props/callbacks/state/effects/context/reducers, controlled
  forms, data/mutations, routing, portals, loading/error boundaries, memoization/list identity,
  transitions, gestures, virtualization, rich widgets, tests, styles, auth, and deployment.
- [ ] Every inventoried React dependency receives `native`, `hedron`, `element`, `react-island`, or
  `not-a-fit` disposition with rationale, owner, target/removal, and migration/fallback evidence.
- [ ] Worked CRUD form, coordinated dashboard, optimistic DataEditor edit, overlay/command flow, and
  temporary React-island migrations compare navigation/HTMX/upgrade/JS failure/a11y/performance/cleanup.
- [ ] The optional React-island bridge is Experimental, non-transitive, single-root, pinned,
  CSP/supply-inventoried, typed at props/events, SSR-fallback-capable, deterministically unmounted,
  forbidden from owning HTMX server regions, and paired with a removal ledger.
- [ ] The fit guide explicitly rejects universal parity and covers offline/client-authoritative,
  games/canvas, arbitrary npm, and high-frequency collaboration non-equivalents.

## 0.41 — Composition, state, and navigation

### `COMPOSE-041`

- [ ] Typed element events compose through registered actions and `InteractionGraph` bindings with
  cycle, payload, target, authorization, cancellation, and full-fragment fallback controls.
- [ ] Element-to-element communication uses DOM events or registered graph contracts, not hidden
  global stores, direct private method calls, or arbitrary selector mutation.

### `STATE-041`

- [ ] Disposable, draft, preference, server, and capability state classes are machine-visible and
  enforce their persistence/authority rules.
- [ ] Opt-in draft transfer is schema/version/route/identity/expiry/size bounded, clears on identity
  or authorization change, and rejects secrets, capabilities, trusted HTML, files, and server state.
- [ ] Every stateful element has an explicit submit/discard/reconnect/swap/history policy and a
  no-transfer fallback.
- [ ] Controlled/local/draft/preference ownership and `InteractionState` operation identity remain
  stable through transfer, composition, history, and late-response scenarios; transfer cannot turn
  local/draft state into canonical server state.

### `NAV-041` / `TRACE-041` / `FALLBACK-041`

- [ ] Boosted navigation, push/replace URL, history cache, focus/title, preload, view transitions
  where supported, and full navigation fallback preserve server authority and existing privacy rules.
- [ ] Lifecycle, event, state-transfer, asset, action, and failure traces are correlated without
  recording payloads, secrets, field values, or user content by default.
- [ ] One failing/slow/incompatible element cannot prevent unrelated elements, native navigation,
  form submission, or authorized HTMX regions from operating.

### `BROWSER-041` / `REGRESS-041` / `PKG-041`

- [ ] Multi-element dashboard/form/navigation scenarios pass three-engine browser, host, a11y,
  performance, memory, failure-injection, history/privacy, and compatibility matrices.
- [ ] No phase 0.41 feature creates a hidden correctness dependency on live transports, preload,
  View Transitions, browser storage, or JavaScript.

## 0.42 — Production-grade Web Component platform

### `STABLE-042` / `COMPAT-042`

- [ ] A machine-readable Supported inventory names stable tags, ABI versions, attributes/properties,
  event schemas, form encodings, slots/parts/tokens, fallback, browser floor, and package versions.
- [ ] Minimum/current dependency and browser matrices, mixed versions, upgrades from 0.36–0.41,
  rollback, offline installs, CDN refusal, package removal, and unsupported-feature failure pass.
- [ ] Experimental elements/adapters are absent from production defaults and have an owner,
  destination/terminal disposition, and conspicuous capability label.
- [ ] The stable inventory names supported state-ownership modes, async-interaction transitions,
  optimistic mutation types, gesture/overlay entries, and React-migration bridge disposition; any
  excluded contract remains explicit and non-default.

### `REVIEW-042` / `AT-042`

- [ ] An independent browser/security review covers code execution, CSP/Trusted Types, XSS/HTML
  sinks, payloads/events, origins/assets/workers, Shadow DOM assumptions, state transfer, forms,
  version skew, dependencies, and failure isolation; no critical/high finding remains unresolved.
- [ ] Human AT sessions cover representative form, navigation, data-editor, chart, and failure/swap
  workflows across the declared desktop/mobile screen-reader and other-disability matrix; blockers
  are fixed or the affected surface remains outside Supported inventory.

### `PERF-042` / `SUPPLY-042`

- [ ] Shared and per-surface bundle, request, upgrade, interaction, memory/leak, long-task,
  layout-shift, and slow-module budgets pass in the production reference app.
- [ ] Wheel/npm artifacts, modules, workers/WASM, source maps, licenses, SBOMs, provenance,
  vulnerabilities, reproducible builds, retention, and rollback evidence are complete.

### `REGRESS-042` / `PKG-042`

- [ ] FastAPI, Flask, Django, HDJ, plugins, reference app, conformance, browser/a11y, security,
  performance, docs, and packaging suites pass with zero Deferred 0.42-owned rows.
- [ ] `hedron-elements` is production-grade only for the declared Supported inventory; the release
  does not imply that all Hedron UI is a custom element or that applications are SPAs.

## Program exit

The Web Component platform is production-grade only after all 0.42 gates are Verified. Earlier
phases may ship Alpha/Beta surfaces behind explicit pins and capability labels. SSR, native HTML,
ordinary forms/navigation, HTMX fragments, and server validation remain supported fallbacks
throughout the program. The five interaction contracts must either appear in the locked Supported
inventory with their evidence complete or retain an explicit Experimental/excluded disposition;
none may disappear between phase gates.
