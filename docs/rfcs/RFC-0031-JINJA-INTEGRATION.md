# RFC-0031: HDJ — Hedron Jinja authoring

**Status:** Implementing · **Target:** phase 0.9 (`v0.9.0`)

## Summary

HDJ is Hedron's optional, standards-first `.hdj` template format built on Jinja. It does not hide
HTML or replace Jinja expressions. An HDJ file has a small static TOML prologue declaring the
format version, template kind, available feature profile, additional features, and required
deployment capabilities. Its body is ordinary HTML, CSS, JavaScript, Web Components, Jinja, and
HTMX with a small Hedron extension for typed components, assets, routing, security values, render
metadata, and diagnostics.

The distribution is `hedron-jinja`, the import is `hedron_jinja`, and the convenience extra is
`hedron[jinja]`. `.hdj` makes the integrated contract explicit to authors, editors, loaders,
checkers, and build tooling. HDJ remains a profile over Jinja rather than a fork of it.

Typed Python components remain canonical for reusable behavior, authorization, data preparation,
and component contracts. HDJ is the advanced HTML-first surface. It must give a trusted application
author the same practical freedom they have in a normal Jinja application while preserving the
Hedron features that disappear when a template engine returns only an opaque string.

## Decision

1. `.hdj` is a versioned source format: a mandatory static prologue followed by an ordinary Jinja
   template body. HDJ uses Jinja rather than reimplementing inheritance, includes, macros,
   expressions, filters,
   tests, i18n, async rendering, or editor tooling.
2. Standard HTML is first-class. HDJ does not require component wrappers around native markup.
3. Trusted template source may contain author-written HTML, CSS, JavaScript, custom elements, and
   HTMX attributes. Strict mode protects dynamic values and contracts; it is not a reduced HTML
   grammar.
4. Deployment policy remains authoritative. A template may require inline script, inline style,
   HTMX eval, response script processing, remote origins, or an extension; HDJ reports those
   capabilities and the application security policy decides whether the response may ship.
5. Hedron components available to a template come from an explicit immutable binding namespace.
6. Every component invocation renders through `hedron_core.render()` and merges the complete
   `RenderResult`: HTML, assets, approved headers, identity, diagnostics, and trace data.
7. HTMX is usable directly through its HTML attributes. HDJ adds validation and Hedron integration,
   not a second interaction DSL.
8. Templates are trusted application or installed-package code. HDJ does not support hostile or
   tenant-authored templates, even with `SandboxedEnvironment`.
9. Feature declarations state which HDJ integrations are available and which deployment
   capabilities the source requires. They never authorize application behavior or relax policy.
10. D-041 removes HDN in 0.9 without a compatibility runtime or converter. HDN does not constrain
   this design.

## Design principles

### Standards first

If HTML, Jinja, CSS, JavaScript, or HTMX already has an understandable construct, HDJ uses it. A
developer can paste normal markup into an HDJ template and progressively add Hedron features.

### Small explicit bridges

HDJ adds bridges only where a plain Jinja string would lose a Hedron guarantee: typed component
calls, render metadata, registered assets, route reversal, CSRF, typed URLs, scoped-style symbols,
HTMX request facts, and diagnostics.

### Freedom at the source boundary

Someone allowed to edit an HDJ template is trusted like someone allowed to edit application Python
or JavaScript. Literal template source may use the full browser platform. Dynamic values do not
inherit that trust: they remain autoescaped and context-checked unless the author crosses an
explicit typed trust boundary.

### Policy is not syntax

HDJ never silently weakens CSP or Hedron's security headers to make a template work. The checker
computes the template's required browser capabilities. A mismatch is an actionable diagnostic:
either change the source, register an asset, or deliberately change application policy.

### Progressive enhancement before cleverness

HDJ examples prefer links with `href`, forms with `action` and `method`, semantic HTML, stable IDs,
and server-rendered error states. HTMX enhances those controls. JavaScript-disabled navigation and
form submission remain useful unless the application explicitly documents a JavaScript-only tool.

## Authoring layers

| Layer | Best for | Owns |
|---|---|---|
| Typed Python | authorization, I/O, derived data, reusable behavior, typed props/slots | application and component logic |
| HDJ template | documents, fragments, inheritance, macros, presentation branching, native markup | trusted presentation composition |
| HTMX | requests, swaps, history, OOB updates, progressive interaction | hypermedia interaction |
| Browser module / Web Component | persistent client-local behavior and third-party JS integration | browser lifecycle and DOM-local state |
| CSS / Hedron styles | layout, visual design, themes, transitions | presentation styling |

The layers can be mixed in one template without making one layer emulate another.

## Packaging

| Distribution | Import | Required dependencies |
|---|---|---|
| `hedron-jinja` | `hedron_jinja` | matching `hedron-core`, `Jinja2>=3.1,<4`, MarkupSafe |
| `hedron[jinja]` | convenience extra | matching `hedron-jinja` |

`hedron-core` and a default `hedron` install do not depend on Jinja. Framework response helpers stay
in `hedron`, `hedron-flask`, and `hedron-django`, keeping dependency direction acyclic.

## `.hdj` source format

An HDJ source is UTF-8 text named with the `.hdj` suffix. It begins at byte zero with a delimited
TOML prologue; the body after the closing delimiter is passed to Jinja with source line numbers
preserved:

```hdj
---hdj
version = 1
kind = "page"
profile = "standard"
assets = ["app:dashboard.css", "app:dashboard.mjs"]
regions = ["main", "notices"]
---
{% extends "layouts/app.hdj" %}

{% block content %}
  <main id="main" hx-history-elt>{{ view.heading }}</main>
{% endblock %}
```

The prologue grammar is deliberately data-only. It has no interpolation, imports, tags, aliases,
or executable values and is parsed before Jinja with Python's TOML parser. Unknown keys and feature
IDs are errors in version 1, so misspellings cannot silently change the template contract.

Required keys:

| Key | Contract |
|---|---|
| `version` | Integer HDJ source-format version. Version 1 is the phase 0.9 format. |
| `kind` | `page`, `fragment`, or `library`; controls document shape and whether direct route rendering is valid. |
| `profile` | Versioned named baseline: `minimal`, `standard`, `full`, or `custom`. |

Optional keys:

| Key | Contract |
|---|---|
| `features` | Additional feature IDs; for `custom`, the complete non-invariant set. |
| `requires` | Deployment capabilities the author expects, such as inline style, inline script, HTMX eval, response scripts, or a remote origin. |
| `assets` | Unconditional registered logical asset IDs, merged into `RenderResult.assets`. |
| `regions` | Fragment-region IDs used or emitted by the template; selectors remain defined by the application route contract. |
| `dynamic_dependencies` | Bounded loader namespaces allowed for dynamic include/import/extends expressions. |

Feature IDs use the `web.*`, `jinja.*`, `hedron.*`, `htmx.*`, and `browser.*` namespaces. Format v1
defines these exact built-in profile expansions (`●` means included):

| Feature ID | Minimal | Standard | Full | Enables |
|---|:---:|:---:|:---:|---|
| `web.html` | ● | ● | ● | Native HTML, SVG, ARIA/data attributes, and custom data vocabulary |
| `web.css` |  | ● | ● | Literal/linked CSS subject to declared capabilities and policy |
| `web.javascript` |  |  | ● | Literal/linked JavaScript subject to declared capabilities and policy |
| `web.custom-elements` |  |  | ● | Custom-element markup and registered implementations |
| `jinja.core` | ● | ● | ● | Expressions, escaping, conditions, loops, filters, tests, assignment |
| `jinja.composition` |  | ● | ● | Extends, blocks, include/import, macros, `call`, and namespaces |
| `jinja.i18n` |  |  | ● | Configured Jinja i18n extension |
| `jinja.do` |  |  | ● | Configured expression-statement extension |
| `jinja.loop-controls` |  |  | ● | Configured loop `break` and `continue` extension |
| `jinja.async` |  |  | ● | Async filters/globals/includes/iterables through `render_async()` |
| `jinja.dynamic-dependencies` |  |  | ● | Dynamic dependency expressions bounded by `dynamic_dependencies` |
| `hedron.components` |  | ● | ● | Bound typed components, body, slots, identity, complete metadata |
| `hedron.assets` |  | ● | ● | Prologue assets, `{% hedron_asset %}`, fingerprinting and graph merge |
| `hedron.routes` |  | ● | ● | Reverse URLs and addressable route references without authorization changes |
| `hedron.forms` |  | ● | ● | CSRF controls and typed form/error presentation bridges |
| `hedron.styles` |  | ● | ● | Scoped-style symbols and registered CSS |
| `hedron.themes` |  | ● | ● | Active theme facts and theme tokens |
| `hedron.interaction` |  | ● | ● | Portable HTMX facts, regions, and typed response integration |
| `htmx.core` |  | ● | ● | Verbs, triggers/sync, targets/swaps, request data, forms and inheritance |
| `htmx.history` |  | ● | ● | Boost, push/replace URL, history controls and restoration contracts |
| `htmx.oob` |  | ● | ● | Select/OOB swaps, preservation, and region authorization |
| `htmx.events` |  |  | ● | HTMX event API and inline `hx-on:*` capability classification |
| `htmx.advanced-selectors` |  |  | ● | Selectors beyond Hedron's portable statically validated subset |
| `htmx.view-transitions` |  |  | ● | Swap transition modifiers and browser View Transition integration |
| `browser.modules` |  | ● | ● | Registered lifecycle-aware ES modules |

`custom` includes only the invariant source parser, autoescape/secret boundaries, loader isolation,
metadata accumulator, and the IDs explicitly listed in `features`. These provider-bound IDs are
always explicit and are never implied by `full`: `jinja.extension:<id>`, `jinja.foreign`,
`hedron.data`, `hedron.charts`, and `htmx.extension:<id>`. Provider registration supplies the exact
version, digest, dependencies, and capability metadata.

A declared but unavailable feature is an error; an undeclared feature use is an error in
checked/build mode; a declared but unused feature is a diagnostic. The feature graph for a root
template is the union of its static dependencies, while every source retains its own declaration
for editor feedback.

`requires` is an assertion, not permission. Format v1 defines `browser.inline-style`,
`browser.inline-script`, `browser.head-mutation`, `htmx.eval`, `htmx.response-scripts`, and
`network.origin:<scheme>://<authority>` capability IDs; registered providers may add namespaced
IDs. The checker compares declarations to capabilities inferred from the source and dependencies:
under-declaration is an error and harmless over-declaration is a warning. SecurityPolicy, CSP,
CSRF, route authorization, asset-origin policy, and HTMX runtime configuration remain authoritative.

HDJ loaders accept `.hdj` only. An application can still run an ordinary Jinja environment beside
HDJ. Importing a third-party `.html`/`.jinja` template into an HDJ graph requires the explicit
`jinja.foreign` feature and a namespaced foreign loader; foreign source cannot use Hedron tags and
is capability-inventoried conservatively.

## Public API

The phase 0.9 target surface is:

```python
from hedron_jinja import (
    HdjContext,
    HedronJinja,
    HedronJinjaExtension,
    TemplateCapabilities,
    TemplateDeclaration,
    TemplateSource,
    TemplateSpec,
)
```

The currently implemented core (`HedronJinja`, `HedronJinjaExtension`, `TemplateSpec`, and
`TemplateSource`) grows toward this surface without changing Jinja itself.

### `TemplateSpec[ViewT]`

`TemplateSpec` is the immutable contract for one document or fragment:

```python
DASHBOARD = TemplateSpec[DashboardView](
    "dashboard/index.hdj",
    view_type=DashboardView,
    source=TemplateSource.APPLICATION,
)
```

Target fields are:

- `name`: canonical loader-relative name;
- `view_type`: optional runtime view-model contract;
- `mode`: optional assertion matching the source `kind`; a mismatch fails rather than overriding
  the `.hdj` prologue;
- `source`: application or package namespace;
- `logical_id`: stable diagnostic identity;
- `assets`: optional application-supplied additions to the source declarations;
- `fragment_regions`: application-owned selector definitions for region IDs declared by source;
- `strict`: application policy that may tighten dynamic-value and static-contract checking, default
  `True`; it cannot add an undeclared source feature.

Canonical names use `/`, contain no empty, `.` or `..` segment, NUL, backslash, or absolute path,
and cannot escape the owning loader namespace.

### `HedronJinja`

```python
templates = HedronJinja(
    environment,
    components={"Card": Card, "StatusBadge": StatusBadge},
    strict=True,
)
```

Public operations are:

```python
templates.register_component(alias, factory)
templates.register_asset(logical_id, asset)
templates.freeze()
templates.describe(spec_or_name) -> TemplateDeclaration
templates.check(spec_or_name, *, view_type=None) -> tuple[Diagnostic, ...]
templates.capabilities(spec_or_name) -> TemplateCapabilities
templates.render(spec_or_name, view, *, context=None, mode=None) -> RenderResult
await templates.render_async(spec_or_name, view, *, context=None, mode=None)
```

Registration is startup-only and freezes on first check or render. Component aliases are static,
case-sensitive, application-local, duplicate-safe, and never discovered from a global registry.

`TemplateDeclaration` is immutable and exposes `format_version`, `kind`, `profile`,
`declared_features`, `effective_features`, `requires`, `assets`, `regions`, and bounded dynamic
dependency namespaces. `describe()` parses and resolves availability without rendering. It is the
canonical editor/CLI/Explorer answer to “what is available to this source?”; `capabilities()`
separately reports what the source and its dependency graph actually require from deployment.

### `HdjContext`

Every render exposes one immutable `hdj` facade. It offers presentation capabilities without
leaking a raw framework request, session, container, environment, or registry:

```text
hdj.mode                 PAGE or FRAGMENT
hdj.is_fragment          convenience boolean
hdj.locale / hdj.theme   render-context values
hdj.htmx                 read-only portable HTMX request facts
hdj.url(ref, **params)   framework-owned reverse URL as SafeUrl
hdj.asset_url(id)        registered fingerprinted asset as SafeUrl
hdj.styles(id)           typed scoped-style symbols
hdj.attrs(value)         serialize only a validated attribute collection
hdj.csrf_input()         framework-owned CSRF hidden control
```

The template also receives `view`. View fields are not flattened into globals. Applications may
install ordinary Jinja globals, filters, and tests before binding; the checker inventories them and
their trust/I/O declarations.

## Template syntax

### Prologue and native markup

Normal HTML and HTMX need no Hedron wrapper:

```jinja
---hdj
version = 1
kind = "fragment"
profile = "standard"
regions = ["main"]
---
<main id="main" hx-history-elt>
  <a href="{{ view.urls.settings|hedron_url }}"
     hx-get="{{ view.urls.settings|hedron_url }}"
     hx-target="#main"
     hx-push-url="true">
    Settings
  </a>
</main>
```

Literal standard tags, custom elements, `data-*`, `aria-*`, `hx-*`, CSS, and JavaScript are
application source and remain available. Checked mode validates what it can prove; it does not
replace the browser platform with an allowlisted mini-HTML language.

### Hedron component

```jinja
{% hedron "StatusBadge" status=view.plan compact=true %}
```

Props are named Jinja expressions. `key=` is reserved for Hedron identity. Aliases are static
string literals in 0.9 so tooling can inventory calls. Positional props and spread mappings are not
part of the checked grammar.

### Body and slots

```jinja
{% hedron "Card" title=view.heading with body %}
  <p>{{ view.summary }}</p>
  {% slot "footer" %}
    {% hedron "AccountMenu" account_id=view.account_id %}
  {% endslot %}
{% endhedron %}
```

`with body` is deliberately explicit so the parser can distinguish inline and block calls without
guessing. A body uses the component's `body` slot when declared and children otherwise. Named slots
must be direct structural children of the component block; control flow belongs inside a slot.
Slot names and cardinality are checked against the component contract.

Body and slot markup is provenance-carrying internal output, not a public `TrustedHtml` shortcut.
Nested components retain their metadata.

### Conditional asset requirement

Unconditional assets normally belong in the `.hdj` prologue. A branch-dependent registered asset
uses:

```jinja
{% hedron_asset "app:charts.mjs" %}
```

The tag emits no markup. It adds the resolved, fingerprinted asset to `RenderResult.assets` in
first-use order. Unknown IDs, kind conflicts, remote-policy violations, or use after the relevant
document head has been sealed fail with a diagnostic. Authors may still write literal `<link>` and
`<script>` tags; doing so is ordinary HTML but opts that tag out of Hedron fingerprinting,
deduplication, dependency graphs, and fragment-asset checks.

## Jinja feature contract

HDJ preserves Jinja semantics instead of offering lookalikes.

| Jinja capability | HDJ contract |
|---|---|
| `extends`, blocks, `super()`, `self` | Supported; static dependencies inventoried in strict production builds. |
| `include`, `import`, `from ... import` | Supported with normal context/cache semantics; static names preferred and inventoried. |
| macros and `call`/`caller` | Supported; Hedron tags inside macros use the active render session and merge metadata. |
| `if`, loops, recursive loops, loop variables | Supported over bounded materialized values; work counts toward render limits. |
| filters, tests, globals | Standard Jinja and explicit application additions are supported; trust and I/O behavior is declared. |
| `set`, block assignment, `namespace` | Supported; captured markup retains Jinja safety semantics but is not automatically `TrustedHtml`. |
| whitespace control and comments | Supported exactly as Jinja defines them. |
| i18n extension | Supported when installed/configured by the application; locale comes from `RenderContext`. |
| `do` and loop controls | Supported when enabled before binding; checker and budgets understand them. |
| async filters, globals, includes, iterables | Supported only through `render_async()` and explicitly declared application functions; awaited work is traced and deadline-aware. |
| custom Jinja extensions | Supported when installed before HDJ binding and declared in build evidence; they cannot bypass render-session or trust boundaries. |
| bytecode cache / precompile | Supported as a local optimization; Python bytecode is not a portable Hedron artifact. |
| dynamic include/inheritance | Available through the explicit dynamic-dependency escape hatch; production needs a bounded loader namespace or rejects it. |
| `TemplateStream` / incremental output | Not exposed in 0.9 because headers/assets/identity must be known before a response begins; a future two-phase API may add it. |
| `NativeEnvironment` | Not a supported root environment because HDJ's result is HTML plus `RenderResult` metadata. |

Jinja's meta API is used for undeclared-variable and referenced-template analysis. Environment
mutation after template loading is rejected because Jinja itself does not define that behavior
reliably. Extension state lives on the bound environment or render context, not on a reusable
extension instance, so Jinja overlays cannot leak one application's bindings into another.

## Hedron feature contract

| Hedron capability | HDJ surface and guarantee |
|---|---|
| Typed models | `TemplateSpec.view_type`; runtime validation plus sound static `view.field` checks. |
| Components | Explicit aliases, props validation, slots, identity, render limits, and metadata parity. |
| Native HTML | Written directly; dynamic values follow contextual trust rules. |
| Routing/addressable actions | `hdj.url` returns purpose-aware `SafeUrl`; exposing a route/action remains framework-owned. |
| Pages/fragments | `TemplateSpec.mode`, HTMX request facts, history-restore PAGE selection, and document-shape checks. |
| Interaction results | Typed response headers, status policy, OOB authorization, cache variation, and fragment regions stay authoritative. |
| Forms/validation/CSRF | Semantic HTML forms, typed view errors, `hdj.csrf_input`, same-origin unsafe actions, and HTMX/non-HTMX error parity. |
| Assets | Template/component declarations merge into one fingerprinted, ordered, CSP-aware asset graph. |
| Scoped styles/themes | `hdj.styles` exposes compiled symbols; theme variables and active theme come through normal render context. |
| Browser modules/Web Components | Registered modules merge as assets; custom elements are ordinary HTML and initialize on the documented lifecycle. |
| Icons, data, charts, built-ins | Invoked as normal allowlisted Hedron components with identical output/metadata to Python composition. |
| Security types | `Secret` never renders; `TrustedHtml` and `SafeUrl` require explicit context-appropriate filters. |
| State/cache/jobs | Prepared in Python; templates receive bounded presentation values and portable status facts, never live backends. |
| Diagnostics/trace/Explorer | Template spans, include/macro stack, component path, capabilities, dependencies, and redacted timings share Hedron diagnostics. |
| Accessibility | Component contracts remain intact; static template checks and browser evidence cover surrounding native markup. |

## HTML, CSS, and JavaScript freedom

### Trusted source versus dynamic data

HDJ treats these cases differently:

```jinja
<style>/* trusted application source */</style>
<script type="module">/* trusted application source */</script>
<p>{{ view.user_supplied_text }}</p>
```

The literal source is application code. The expression is data and is escaped. Strict mode:

- enables HTML autoescape and `StrictUndefined`;
- rejects rendering `Secret`;
- requires `TrustedHtml|hedron_trusted` for dynamic raw markup;
- requires purpose-compatible `SafeUrl|hedron_url` for dynamic URL attributes;
- permits `tojson` for placing bounded data into a JavaScript expression or JSON script block;
- rejects dynamic tag names, attribute names, event-handler bodies, CSS source, `srcdoc`, and
  executable script source unless a named advanced trust adapter is installed; and
- rejects a generic `safe` escape as too context-blind in checked mode.

An advanced application can disable individual static checks or strict mode for trusted source. It
then owns those dynamic contexts exactly as it would in a conventional Jinja application. Secret
redaction, response-header validation, component authorization, and loader isolation are not
disabled by `strict=False`.

### CSS

Authors may use literal `<style>`, ordinary `<link>`, registered CSS assets, component-scoped CSS,
theme custom properties, third-party styles, and plain classes. Registered assets are preferred
when fingerprinting, deduplication, CSP, fragment delivery, or dependency inspection matters.

Dynamic visual values should normally cross through class names, theme tokens, `data-*`, or CSS
custom properties prepared by a typed helper. Interpolating arbitrary user data into CSS source is
not made safe by HTML escaping.

### JavaScript

Authors may use literal scripts, local/remote script tags allowed by application policy, ES
modules, registered browser assets, and Web Components. Registered modules are the recommended
path because they load once, work with strict CSP, participate in the asset manifest, and can
handle content added by HTMX.

Browser modules initialize from `htmx:load`/`htmx:afterSwap`, release resources on
`htmx:beforeCleanupElement`, and sanitize third-party DOM mutations before `htmx:beforeHistorySave`
when history snapshots are enabled. A module must be idempotent because the same fragment may be
processed more than once.

### Capability report and CSP

`templates.capabilities(spec)` reports at least:

- inline script and inline style;
- inline DOM/HTMX event code and HTMX trigger filters requiring eval;
- response script-tag processing;
- remote asset origins and integrity metadata;
- registered browser/HTMX extensions;
- dynamic template dependencies;
- raw/trusted dynamic markup contexts; and
- page-head mutation requirements for fragment renders.

The selected `SecurityPolicy` compares this report with CSP and HTMX runtime configuration. HDJ
does not inject `unsafe-inline`, `unsafe-eval`, remote origins, nonces, or `allowScriptTags=true`
silently. Nonces are request values and never stored in templates or build manifests.

## HTMX contract

### Complete attribute surface

HDJ allows the pinned HTMX 2 attribute surface directly:

| Area | Attributes/features |
|---|---|
| Requests | `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete` |
| Triggering/concurrency | `hx-trigger`, polling, debounce/throttle/queue modifiers, `hx-sync` |
| Targeting/swaps | `hx-target`, `hx-swap` and modifiers, `hx-select`, `hx-select-oob`, `hx-swap-oob`, `hx-preserve` |
| Navigation/history | `hx-boost`, `hx-push-url`, `hx-replace-url`, `hx-history`, `hx-history-elt` |
| Request data | `hx-include`, `hx-params`, `hx-vals`, `hx-headers`, `hx-encoding`, `hx-request` |
| UX/forms | `hx-indicator`, `hx-disabled-elt`, `hx-confirm`, `hx-prompt`, validation behavior |
| Inheritance | normal inheritance plus `hx-inherit` and `hx-disinherit` |
| Extensions | `hx-ext` for registered, versioned extension assets |
| Events | `hx-on:*` and the JavaScript event API when the application's eval/CSP policy permits them |

Future static attributes in the pinned compatible HTMX line do not require an HDJ grammar release.
The checker recognizes the installed HTMX version, validates known semantics, and reports an
unknown `hx-*` attribute instead of stripping it.

### Checked HTMX semantics

The checker/runtime enforce the Hedron integration boundary:

- dynamic request/history URLs use purpose-compatible `SafeUrl`; static literals must be local
  unless policy explicitly allows an origin;
- unsafe verbs require the application CSRF contract and cannot become authorized merely because
  a template writes `hx-post` or `hx-delete`;
- targets, selectors, includes, indicators, and disabled-element selectors are checked against the
  supported selector policy, with an explicit advanced escape hatch for full selectors;
- `hx-vals` and `hx-headers` use JSON by default; `js:` values, event filters, and `hx-on:*` are
  classified as executable/eval capabilities;
- `hx-sync`, trigger queues, indicators, disabled controls, and `aria-busy` are checked together so
  common request-race and double-submit mistakes produce useful diagnostics;
- `hx-boost` and history-changing controls need a navigable `href`/`action`, and every pushed URL
  must return a complete page on ordinary navigation/history cache miss;
- `hx-history="false"` is required around sensitive material that must not enter browser snapshots;
- fragment targets and OOB updates must match route/template-declared `FragmentRegion` contracts;
- swaps preserve focus where possible, announce semantic status/error changes, and use stable IDs;
  View Transitions and scroll/focus modifiers remain available;
- file uploads use normal forms plus `multipart/form-data`/`hx-encoding`; upload progress belongs in
  a browser module or documented HTMX event handler; and
- attribute inheritance is surfaced in diagnostics so an inherited destructive verb, target,
  header, or parameter policy is never invisible in Explorer.

### Response-side HTMX

Request attributes belong in HTML. Response mechanics remain typed Python/Hedron values:

- `HtmxRequestFacts` exposes `HX-Request`, target, trigger, current URL, boost, prompt, and history
  restore without exposing a raw request;
- `InteractionResult` owns status, primary region, swap, retarget/reselect, push/replace/redirect,
  refresh, cache variation, concurrency, triggers, and OOB updates;
- approved `HX-*` response headers are validated and merged into the same `RenderResult` session;
- status policies cover validation, accepted/no-content, authorization, conflict, throttling, and
  server errors while non-HTMX clients keep framework-native behavior; and
- OOB markup written directly in a checked template is validated against the same declared region
  graph as `OobUpdate`.

An adapter accepts an HDJ `RenderResult` wherever it accepts component render output. A typed
interaction envelope may wrap that result without re-rendering or converting it to an opaque
string.

### Scripts in swapped content

Hedron's managed HTMX configuration keeps `allowEval=false`, `allowScriptTags=false`,
`historyRestoreAsHxRequest=false`, `includeIndicatorStyles=false`, native form validity enabled,
and same-origin requests by default. This supports strong CSP and deterministic fragment behavior.

Advanced applications may enable HTMX eval features or response script processing explicitly.
The capability report then records the requirement and the application must supply compatible CSP.
Registered modules plus HTMX lifecycle events are preferred because a script tag returned in a
fragment is not a reliable component lifecycle.

### HTMX extensions

Core extensions such as head support, idiomorph, preload, response targets, SSE, and WebSocket are
ordinary registered assets with exact versions, digests, CSP needs, load order, and conformance
evidence. Community extensions are application-owned and must declare the same metadata. Merely
writing `hx-ext` does not install or authorize an extension.

SSE/WebSocket transport remains owned by phase 0.10. HDJ does not need new syntax when those
extensions become Supported.

## Render lifecycle and metadata

Each render creates an isolated session:

1. Resolve the canonical `.hdj` source, parse its prologue, expand its profile, and reject
   unavailable or policy-denied declarations.
2. Resolve the static/bounded dependency graph and aggregate declared features, requirements,
   assets, and regions.
3. Validate the view and create `HdjContext` from the normal `RenderContext` and portable request
   facts.
4. Seed unconditional template assets and an empty metadata/capability accumulator.
5. Execute Jinja with `view`, `hdj`, and explicit application additions.
6. Render every Hedron tag through the bound component contract and `hedron_core.render()`.
7. Merge HTML, assets, approved headers, identity, diagnostics, trace data, and conditional assets.
8. Validate document/fragment shape, feature use, HTMX regions, declared/inferred capabilities,
   SecurityPolicy compatibility, and
   output/resource budgets.
9. Return one immutable `RenderResult`.

Direct `Template.render()` may render ordinary Jinja, but encountering a Hedron component/asset
bridge outside this session fails closed because a string cannot retain metadata.

Assets deduplicate by canonical identity in first-use order. Conflicting asset or header
definitions and identity collisions fail. Diagnostics retain template source, include/macro stack,
component path, and safe capability context. No secret or raw request value enters traces.

PAGE mode emits one complete document. FRAGMENT mode rejects document-level elements in checked
mode and applies fragment-asset/head policy. A fragment may require only assets already present on
the page unless a registered, conformance-tested head-management path is active.

## Loaders and production inventory

Application and installed-package templates use explicit namespaces. Application overrides are
declared; loader precedence never silently shadows a package template.

Strict static dependencies use Jinja's referenced-template meta API. The build records:

- source format version, kind, profile, declared/expanded/observed features, logical ID, canonical
  name, and digest;
- extends/include/import dependencies and dynamic-dependency bounds;
- referenced components, assets, extensions, and their contract digests;
- view contract, render mode, and fragment regions;
- declared and inferred browser/security capabilities plus policy decision;
- Jinja, MarkupSafe, HTMX, Hedron, and policy versions; and
- optional bytecode-cache identity, never portable Python bytecode.

The manifest contains no source text, absolute root, live object, nonce, secret, or request data.
Development invalidates affected dependency subgraphs atomically. Production fails closed on stale,
missing, undeclared, shadowed, or incompatible inputs.

## Resource and async policy

HDJ shares Hedron render depth/node budgets and adds bounds for template dependency depth, macro
recursion, per-loop and total loop work, component calls, async operations, output characters,
metadata, and optional wall-clock deadlines.

Models expose bounded materialized collections. Arbitrary generators, lazy database/query objects,
live backends, and hidden unbounded iterators are rejected. Explicit async filters/globals may do
I/O only when registered as such, invoked through `render_async()`, traced, cancellable where the
adapter supports it, and covered by deadlines. Components themselves retain Hedron's no-hidden-I/O
render contract.

Limits fail atomically before a response begins. A wall-clock deadline supplements structural
limits; it does not replace them.

## Diagnostics

The `HED-JINJA-*` family covers names/loaders, bindings, props/slots, view contracts, raw/contextual
trust, dependencies, capabilities/CSP, HTMX semantics, limits, metadata conflicts, environment/
async mismatch, stale manifests, and page/fragment shape.

Every diagnostic includes the template logical ID, canonical source and span, include/macro stack,
component or HTMX attribute when applicable, explanation, remediation, and redacted structured
metadata. Text, JSON, SARIF, CLI, and Explorer use the same record.

## Tooling and developer experience

- `hedron check` checks Jinja dependencies, component/view contracts, HTML contexts, assets,
  required capabilities, HTMX semantics, accessibility, and policy compatibility.
- `hedron dev` watches templates/assets and invalidates affected graphs atomically.
- `hedron build` records the production inventory and capability report.
- Explorer shows source, inheritance/includes, macro/component calls, assets, HTMX request/swap
  graph, fragment regions, policy findings, and redacted render traces.
- HDJ publishes the prologue TOML schema, format-v1 feature registry, and small Jinja extension
  grammar for existing editor tooling. It does not ship a competing expression language.
- Diagnostics use terms an HTML/Jinja author recognizes and always suggest the smallest fix.

Generated examples progress from plain HTML, to Jinja composition, to Hedron components, to HTMX,
to browser modules. Advanced features are opt-in but never hidden.

## Non-goals

- Executing templates authored by untrusted users, tenants, CMS records, prompts, uploads, remote
  repositories, or database rows.
- Exposing raw requests, sessions, dependency containers, settings, environment variables, Python
  builtins, live registries, or backends by default.
- Making Jinja expressions statically equivalent to Python typing.
- Treating macros as Hedron components or making template names authorize routes/actions.
- Treating a feature or `requires` declaration as a security sandbox, permission grant, package
  installer, route exposure, or CSP relaxation.
- Reimplementing Jinja, HTMX, HTML, CSS, JavaScript, or Web Components behind a Hedron DSL.
- Silently weakening CSP, CSRF, URL, header, cache, authorization, or manifest policy.
- Preserving any HDN syntax or runtime.

## Acceptance criteria

Phase 0.9 is complete only when:

- standard Jinja composition and the small Hedron grammar pass parser, inheritance, macro, async,
  i18n, extension, metadata, and isolation fixtures;
- `.hdj` format-v1 prologues, exact profile expansion, declared/observed feature checks, capability
  assertions, line preservation, loader isolation, and the foreign-Jinja boundary pass fixtures;
- trusted literal HTML/CSS/JS remains available while dynamic-value escaping and explicit trust
  crossings pass contextual security tests;
- the complete pinned HTMX 2 attribute groups, response headers, lifecycle events, progressive
  enhancement, history, OOB, forms, concurrency, accessibility, and extension contracts have
  representative evidence;
- Hedron component, routing, forms, CSRF, interaction, assets/styles/themes, browser modules,
  security types, data/chart, diagnostic, trace, and adapter features have HDJ parity fixtures;
- capability reporting and SecurityPolicy/CSP mismatch diagnostics prove that freedom never causes
  silent policy weakening;
- FastAPI, Flask, and Django consume the same HDJ `RenderResult` semantics;
- check/dev/build/Explorer, manifests, package isolation, offline wheels, performance/resource
  budgets, and Python/Jinja/MarkupSafe matrices pass;
- three representative applications cover a semantic page, accessible form/error flow, repeated
  data/status view, HTMX history/OOB interaction, custom CSS, and a browser module; and
- no first-party HDN runtime, discovery, artifact, public API, example, or test remains.

## References

- [Jinja template designer documentation](https://jinja.palletsprojects.com/en/stable/templates/)
- [Jinja API and meta API](https://jinja.palletsprojects.com/en/stable/api/)
- [Jinja extension API](https://jinja.palletsprojects.com/en/stable/extensions/)
- [HTMX documentation](https://htmx.org/docs/)
- [HTMX attribute, header, event, and extension reference](https://htmx.org/reference/)
- [HTMX events](https://htmx.org/events/)
- [HTMX extensions](https://htmx.org/extensions/)

## HDN removal boundary

D-041 rejects a dual-runtime period. Version 0.9 contains no HDN parser, evaluator, formatter,
render program, source discovery, artifact, manifest field, public API, CLI/Explorer integration,
example, compatibility setting, converter, or legacy package. Applications requiring HDN remain on
0.8 until manually rewritten.
