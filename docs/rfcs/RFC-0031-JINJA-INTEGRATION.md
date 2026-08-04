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
6. Every component invocation renders through one request-local `hedron_core.RenderSession` and merges the complete
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

HDJ adds bridges only where a plain Jinja string would lose a Hedron guarantee. Format v1 ships
typed component calls, render metadata, registered assets, typed URLs, and optional route/CSRF
callbacks. Native adapter request facts arrive in phase 0.11; scoped-style and validated-attribute
helpers require the broader provider/context contract in phase 0.14.

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

Format v1 accepts only static `.hdj` dependency names. Finite dynamic candidate manifests and the
foreign-Jinja boundary are assigned to phase 0.11; accepting a namespace name alone would not make
the graph finite, immutable, or capability-complete.

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
| `jinja.i18n` |  |  |  | Explicit configured Jinja i18n extension |
| `jinja.do` |  |  |  | Explicit configured expression-statement extension |
| `jinja.loop-controls` |  |  |  | Explicit configured loop `break` and `continue` extension |
| `jinja.async` |  |  |  | Explicit async environment and `render_async()` |
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
metadata accumulator, and the IDs explicitly listed in `features`. Provider-bound IDs are always
explicit and are never implied by `full`: `jinja.i18n`, `jinja.do`, `jinja.loop-controls`,
`jinja.async`, `jinja.extension:<id>`, `hedron.data`, `hedron.charts`, and
`htmx.extension:<id>`. Provider registration supplies version and availability metadata.

Profiles are allowed authoring surfaces, not claims that every included feature is used. An
explicit provider feature that is unavailable is an error; an undeclared observed use is an error
in checked/build mode; only an explicitly added non-provider feature can produce an unused warning.
The feature graph for a root template is the union of its static dependencies, while every source
retains its own declaration for editor feedback.

`requires` is an assertion, not permission. Format v1 defines `browser.inline-style`,
`browser.inline-script`, `browser.head-mutation`, `htmx.eval`, `htmx.response-scripts`, and
purpose-specific `network.<script|style|image|connect|frame|font|media>-origin:https://<authority>`
capability IDs. The checker compares declarations to capabilities inferred from source and static
dependencies:
under-declaration is an error and harmless over-declaration is a warning. SecurityPolicy, CSP,
CSRF, route authorization, asset-origin policy, and HTMX runtime configuration remain authoritative.

HDJ loaders accept `.hdj` only. An application can run an ordinary Jinja environment beside HDJ,
but format v1 rejects foreign and dynamic dependencies. Phase 0.11 owns a finite, fingerprinted
foreign-template/candidate-manifest boundary; no 0.9 namespace escape hatch is accepted.

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
- `source`: application namespace in 0.9; the package value is reserved for phase 0.11;
- `logical_id`: stable application/inventory identity included in render traces;
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
templates.check(spec_or_name) -> tuple[Diagnostic, ...]
templates.capabilities(spec_or_name) -> TemplateCapabilities
templates.render(spec_or_name, view, *, context=None, mode=None) -> RenderResult
await templates.render_async(spec_or_name, view, *, context=None, mode=None)
```

Registration is startup-only and freezes on first check or render. Component aliases are static,
case-sensitive, application-local, duplicate-safe, and never discovered from a global registry.
The optional `mode` operation argument is also an assertion; source kind remains authoritative.
`library` sources can be checked and imported but cannot be render entry points.

`TemplateDeclaration` is immutable and exposes `format_version`, `kind`, `profile`,
`declared_features`, `effective_features`, `requires`, `assets`, `regions`, `source_digest`, and
`body_start_line`. Format v1 rejects dynamic dependencies rather than exposing dependency-bound
namespaces; finite fingerprinted manifests are phase 0.11. `describe()` parses and resolves
availability without rendering. It is the canonical editor/CLI/Explorer answer to “what is
available to this source?”; `capabilities()` separately reports what the source and its dependency
graph actually require from deployment.

### `HdjContext`

Every render exposes one immutable `hdj` facade. It offers presentation capabilities without
leaking a raw framework request, session, container, environment, or registry:

```text
hdj.mode                 PAGE or FRAGMENT
hdj.is_fragment          convenience boolean
hdj.locale / hdj.theme   render-context values
hdj.htmx                 reserved immutable mapping (empty until native adapter work in 0.11)
hdj.url(ref, **params)   framework-owned reverse URL as SafeUrl
hdj.asset_url(id)        registered fingerprinted asset as SafeUrl
hdj.csrf_input()         framework-owned TrustedHtml hidden control; cross with |hedron_trusted
```

The template also receives `view`. View fields are not flattened into globals. Applications may
install ordinary Jinja globals, filters, and tests before binding; format v1 fingerprints and seals
that environment. I/O declarations are phase 0.13 and contracted provider evidence is phase 0.14.

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
  <a href="{{ view.urls.settings|hedron_nav_url }}"
     hx-get="{{ view.urls.settings|hedron_nav_url }}"
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

Dynamic URL sinks use purpose-specific filters: `hedron_nav_url` for navigation and safe GET/URL
history sinks, `hedron_form_url` for form actions and unsafe HTMX verbs, and `hedron_asset_url` for
asset sources. `hedron_trusted` is valid only in HTML body content.

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
are collected while the component body executes, including through ordinary Jinja control flow.
Slot names and cardinality are checked against the component contract.

Body and slot markup is provenance-carrying internal output, not a public `TrustedHtml` shortcut.
Nested components retain their metadata.

### Conditional asset requirement

Unconditional page assets belong in the `.hdj` prologue. A branch-dependent registered asset is a
fragment-only format-v1 operation:

```jinja
{% hedron_asset "app:charts.mjs" %}
```

The tag emits no markup. It adds the resolved, fingerprinted asset to `RenderResult.assets` in
first-use order. A PAGE graph containing the tag fails before execution because vanilla Jinja has
no reliable semantic “head sealed” event. Registered fragment head management is assigned to phase
0.10. Unknown IDs, kind conflicts, or remote-policy violations fail. Authors may write literal `<link>` and
`<script>` tags; doing so is ordinary HTML but opts that tag out of Hedron fingerprinting,
deduplication, dependency graphs, and fragment-asset checks.

## Jinja feature contract

HDJ preserves Jinja semantics instead of offering lookalikes.

| Jinja capability | HDJ contract |
|---|---|
| `extends`, blocks, `super()`, `self` | Supported; static dependencies inventoried in strict production builds. |
| `include`, `import`, `from ... import` | Supported with normal context/cache semantics; static names preferred and inventoried. |
| macros and `call`/`caller` | Supported; Hedron tags inside macros use the active render session and merge metadata. |
| `if`, loops, recursive loops, loop variables | Supported over bounded materialized values; resulting output, component calls, and Hedron nodes are bounded in 0.9. Exact loop work accounting is phase 0.14. |
| filters, tests, globals | Standard Jinja and explicit application additions are supported and sealed before use. I/O behavior contracts are phase 0.13. |
| `set`, block assignment, `namespace` | Supported; captured markup retains Jinja safety semantics but is not automatically `TrustedHtml`. |
| whitespace control and comments | Supported exactly as Jinja defines them. |
| i18n extension | Supported when installed/configured by the application; locale comes from `RenderContext`. |
| `do` and loop controls | Supported when enabled before binding and declared explicitly; exact loop budgets are phase 0.14. |
| async filters, globals, includes, iterables | Core Jinja async execution is available only through `render_async()` and explicit `jinja.async`; I/O contracts, deadlines, cancellation, and operation traces are phase 0.13. |
| custom Jinja extensions | Trusted application code installed before binding; 0.9 seals the environment but does not claim arbitrary extensions cannot produce `Markup` or bypass contextual lint. Contracted provider evidence is phase 0.14. |
| bytecode cache / precompile | Supported as a local optimization; Python bytecode is not a portable Hedron artifact. |
| dynamic include/inheritance | Rejected in format v1. Phase 0.11 requires an exact finite, fingerprinted candidate manifest rather than a namespace assertion. |
| `TemplateStream` / incremental output | Not exposed in 0.9 because headers/assets/identity must be known before a response begins; a future two-phase API may add it. |
| `NativeEnvironment` | Not a supported root environment because HDJ's result is HTML plus `RenderResult` metadata. |

Jinja's meta API is used for referenced-template analysis. Environment mutation after HDJ binding
is rejected. Binding state is environment-keyed and runtime state is render-context-local rather
than stored on a reusable extension instance, so overlays do not inherit an application's binding.
Attribute-level static equivalence to Python typing is not a 0.9 guarantee.

## Hedron feature contract

| Hedron capability | HDJ surface and guarantee |
|---|---|
| Typed models | `TemplateSpec.view_type` runtime validation; attribute-level static typing is deferred. |
| Components | Explicit aliases, props validation, slots, identity, render limits, and metadata parity. |
| Native HTML | Written directly; dynamic values follow contextual trust rules. |
| Routing/addressable actions | An optional application callback supplies purpose-aware `SafeUrl`; native framework reversal remains phase 0.11. |
| Pages/fragments | Source kind controls render mode and document-shape checks. HTMX request/history selection is phase 0.11. |
| Interaction results | Component headers and assets retain `RenderResult` metadata; adapter response/OOB/region integration is phase 0.11. |
| Forms/validation/CSRF | Semantic HTML is direct; an optional CSRF callback exists, while native framework parity is phase 0.11. |
| Assets | Registered template/component declarations merge into one ordered asset result with explicit capability policy. |
| Scoped styles/themes | Active theme comes through `RenderContext`; a template scoped-symbol helper is phase 0.14. |
| Browser modules/Web Components | Registered modules merge as assets and custom elements are ordinary HTML; browser lifecycle evidence is phase 0.10. |
| Icons, data, charts, built-ins | Invoked as normal allowlisted Hedron components with identical output/metadata to Python composition. |
| Security types | `Secret` never renders; `TrustedHtml` is HTML-body-only; `SafeUrl` requires a purpose-specific sink filter. |
| State/cache/jobs | Prepared in Python; templates receive bounded presentation values and portable status facts, never live backends. |
| Diagnostics/trace/Explorer | Format/source spans, component diagnostics, capabilities, dependencies, and redacted component traces use Hedron records. CLI/Explorer inventory is phase 0.11. |
| Accessibility | Component contracts remain intact; surrounding native-markup/browser evidence is phase 0.10 and broader static analysis phase 0.14. |

## HTML, CSS, and JavaScript freedom

### Trusted source versus dynamic data

HDJ treats these cases differently:

```jinja
<style>/* trusted application source */</style>
<script type="module">/* trusted application source */</script>
<p>{{ view.user_supplied_text }}</p>
```

The literal source is application code. The expression is data. Strict mode enforces a deliberately
finite sink matrix:

- enables HTML autoescape and `StrictUndefined`;
- rejects rendering `Secret`;
- requires `TrustedHtml|hedron_trusted` only for dynamic HTML body markup;
- requires `SafeUrl|hedron_nav_url`, `|hedron_form_url`, or `|hedron_asset_url` at the
  corresponding dynamic URL sink;
- permits `tojson` for placing bounded data into a JavaScript expression or JSON script block;
- rejects unknown contexts, dynamic tag names, attribute names, event-handler bodies, CSS source, `srcdoc`, and
  executable script source unless a named advanced trust adapter is installed; and
- rejects a generic `safe` escape as too context-blind in checked mode.

Jinja autoescaping alone is not described as contextual safety. The strict checker recognizes the
documented finite contexts and fails when it cannot establish one; arbitrary Markup-producing
filters and extensions are trusted application code outside that proof. An advanced application can
disable strict mode for trusted source. It
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

In format v1, `templates.capabilities(spec)` reports the locally inferable set:

- inline script and inline style;
- inline DOM/HTMX event code and `js:` values requiring eval;
- response script-tag processing;
- literal and registered remote asset origins, separated by purpose; and
- page-head mutation requirements for fragment renders.

The binding compares this report with its explicit application capability allowlist. Framework
`SecurityPolicy`, CSP, integrity, and HTMX-runtime reconciliation is adapter/build work in phase
0.11. HDJ
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

Future static attributes in the pinned compatible HTMX line do not require an HDJ grammar release:
they remain ordinary trusted HTML. Version-aware attribute diagnostics and semantic/browser
fixtures are phase 0.10.

### Checked HTMX semantics

Format v1 enforces only what is locally provable without route or browser state:

- dynamic request/history URL attributes use purpose-compatible `SafeUrl` filters;
- `js:` values and `hx-on:*` are classified as eval capabilities;
- literal remote request origins are classified separately from source/script/style origins; and
- static feature use must be allowed by the selected profile.

Version-aware attribute semantics, selectors, inheritance, race/double-submit diagnostics,
navigation/history/OOB/focus/accessibility behavior, and browser fixtures are phase 0.10. Route
authorization, CSRF, response contracts, and region reconciliation are phase 0.11.

Format v1 keeps dynamic navigation/form `SafeUrl` values local because a filter alone cannot prove
a runtime origin was declared. External registered asset URLs must come through `hdj.asset_url()`
and the static graph. Native dynamic-origin reconciliation is phase 0.11.

### Response-side HTMX

Request attributes belong in HTML. Response mechanics remain typed Python/Hedron values. The
following adapter integration is explicitly phase 0.11:

- `HtmxRequestFacts` exposes `HX-Request`, target, trigger, current URL, boost, prompt, and history
  restore without exposing a raw request;
- `InteractionResult` owns status, primary region, swap, retarget/reselect, push/replace/redirect,
  refresh, cache variation, concurrency, triggers, and OOB updates;
- approved `HX-*` response headers are validated and merged into the same `RenderResult` session;
- status policies cover validation, accepted/no-content, authorization, conflict, throttling, and
  server errors while non-HTMX clients keep framework-native behavior; and
- OOB markup written directly in a checked template is validated against the same declared region
  graph as `OobUpdate`.

That phase makes an adapter accept an HDJ `RenderResult` wherever it accepts component render output. A typed
interaction envelope may wrap that result without re-rendering or converting it to an opaque
string.

### Scripts in swapped content

Hedron's managed HTMX configuration independently keeps `allowEval=false`, `allowScriptTags=false`,
`historyRestoreAsHxRequest=false`, `includeIndicatorStyles=false`, native form validity enabled,
and same-origin requests by default. This supports strong CSP and deterministic fragment behavior.

Advanced applications may enable HTMX eval features or response script processing explicitly.
The format-v1 capability report records that requirement; full managed-runtime/CSP reconciliation
is phase 0.11.
Registered modules plus HTMX lifecycle events are preferred because a script tag returned in a
fragment is not a reliable component lifecycle.

### HTMX extensions

Core extensions such as head support, idiomorph, preload, response targets, SSE, and WebSocket can
be ordinary registered assets. Exact provider metadata and evidence are phase 0.14; merely writing
`hx-ext` does not install or authorize an extension in format v1.

SSE/WebSocket transport remains owned by phase 0.10. HDJ does not need new syntax when those
extensions become Supported.

## Render lifecycle and metadata

Each render creates an isolated session:

1. Resolve the canonical `.hdj` source, parse its prologue, expand its profile, and reject
   unavailable or policy-denied declarations.
2. Resolve the static `.hdj` dependency graph and aggregate declared features, requirements,
   assets, and regions.
3. Validate the view and create `HdjContext` from the normal `RenderContext` and portable request
   facts.
4. Seed unconditional template assets and an empty metadata/capability accumulator.
5. Execute Jinja with `view`, `hdj`, and explicit application additions through a guarded,
   chunk-consumed HDJ entry point.
6. Render every Hedron tag through the bound component contract and one shared core render session.
7. Merge HTML, assets, approved headers, identity, diagnostics, trace data, and conditional assets.
8. Validate document/fragment shape, locally observable feature use, declared/inferred
   capabilities, the application allowlist, and
   output/resource budgets.
9. Return one immutable `RenderResult`.

Direct `Template.render()` always fails for `.hdj`, including pure HTML/Jinja templates, because it
would bypass prologue assets, kind checks, capabilities, policy, manifests, and metadata. Ordinary
Jinja remains available through a separate environment.

Assets deduplicate by canonical identity in first-use order. Conflicting asset or header
definitions and identity collisions fail. Diagnostics retain template source, include/macro stack,
component path, and safe capability context. No secret or raw request value enters traces.

PAGE mode emits one complete document and permits only prologue/application assets in 0.9.
FRAGMENT mode rejects document-level elements and may use conditional registered assets when the
declared `browser.head-mutation` capability and application policy allow them. A conformance-tested
head-management path is assigned to phase 0.10.

## Loaders and production inventory

Phase 0.9 accepts canonical application-loader names and rejects traversal, non-`.hdj` input, and
post-bind loader mutation. Installed-package namespaces, declared overrides, and shadow prevention
are phase 0.11 so they can share the finite foreign/candidate-manifest contract.

Format-v1 static dependencies use Jinja's referenced-template meta API. Dynamic or non-`.hdj`
references fail. The 0.9 library exposes the facts needed for inventory. Phase 0.11
build/Explorer wiring records:

- source format version, kind, profile, declared/expanded/observed features, logical ID, canonical
  name, and digest;
- static extends/include/import dependencies;
- referenced components, assets, extensions, and their contract digests;
- view contract, render mode, and fragment regions;
- declared and inferred browser/security capabilities plus policy decision;
- Jinja, MarkupSafe, HTMX, Hedron, and policy versions; and
- optional bytecode-cache identity, never portable Python bytecode.

The manifest contains no source text, absolute root, live object, nonce, secret, or request data.
Development invalidates affected dependency subgraphs atomically. Production fails closed on stale,
missing, undeclared, shadowed, or incompatible inputs.

## Resource and async policy

HDJ shares one Hedron identity/node/depth render session across component calls and adds bounds for
static dependency depth, component calls, chunk-consumed output characters, and metadata. Exact
Jinja loop/macro accounting requires compiler instrumentation and is assigned to phase 0.14; async
operation deadlines/cancellation are phase 0.13.

Models expose bounded materialized collections. Arbitrary generators, lazy database/query objects,
live backends, and hidden unbounded iterators are not valid presentation-model inputs. Components
retain Hedron's no-hidden-I/O render contract.

Limits fail atomically before a response begins. Output is consumed in bounded chunks into the
atomic result rather than allocated without limit and measured only afterward.

## Diagnostics

The format-v1 `HED-JINJA-*` family covers names/loaders, bindings, props/slots, view contracts,
raw/contextual trust, dependencies, capability declarations/policy, limits, metadata conflicts,
environment/async mismatch, and page/fragment shape. Adapter HTMX semantics and stale production
manifests join in phases 0.10 and 0.11.

Every format-v1 diagnostic includes a stable code, explanation, remediation, and a source span when
the checker has one. Rich include/macro stacks, attribute paths, and portable checker fixtures are
phase 0.14; CLI and Explorer presentation is phase 0.11.

## Tooling and developer experience

- `HedronJinja.check()` reports locally provable format/dependency/component/context/capability
  errors in 0.9.
- Phase 0.11 wires those facts into `hedron check`, `hedron dev`, `hedron build`, and Explorer,
  alongside the finite production manifest and adapter context.
- HDJ publishes the prologue TOML schema, format-v1 feature registry, and small Jinja extension
  grammar for existing editor tooling. It does not ship a competing expression language.
- Diagnostics use terms an HTML/Jinja author recognizes and always suggest the smallest fix.

Generated examples progress from plain HTML, to Jinja composition, to Hedron components, to HTMX,
to browser modules. Advanced features are opt-in but never hidden.

## Deferred capability ownership

The 0.9 reductions are scheduled work, not an unowned backlog:

| Capability | Phase | Required boundary |
|---|---:|---|
| Registered fragment head management, two-phase template streaming, version-aware HTMX semantics, and browser-backed navigation/history/OOB/lifecycle validation | 0.10 | Must preserve atomic metadata and ordinary HTTP fallbacks. Normative contracts: [RFC-0032](RFC-0032-LIVE-TRANSPORT.md). |
| Finite fingerprinted dynamic dependency manifests, foreign Jinja/package namespaces, adapter-specific route/CSRF/context/response depth, SecurityPolicy/CSP reconciliation, and CLI/build/Explorer production inventory | 0.11 | A namespace alone is never a dependency bound; foreign source cannot use Hedron tags. |
| `hedron.data`/`hedron.charts` provider parity and high-volume template presentation evidence | 0.12 | Bounded data and accessible fallbacks remain authoritative. |
| Async filter/global I/O declarations, deadlines, cancellation, operation budgets, and trace correlation | 0.13 | Async work remains explicit and render handoff deterministic. |
| Optional Jinja compiler instrumentation for exact loop/macro budgets, contracted custom-extension evidence, scoped-style/validated-attribute helpers, broader contextual analysis, and portable checker fixtures | 0.14 | Public Jinja semantics and the pure-Python fallback remain authoritative. |

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

- standard static Jinja composition and the small Hedron grammar pass parser, inheritance, macros,
  explicit provider availability, metadata, environment sealing, and overlay-isolation fixtures;
- `.hdj` format-v1 prologues, exact profile expansion, declared/observed feature checks, capability
  assertions, line preservation, `.hdj`-only loading, and static dependency/kind fixtures;
- direct rendering always fails, while guarded rendering preserves shared component identity,
  node/depth budgets, metadata, chunked output limits, and atomic results;
- trusted literal HTML/CSS/JS remains available while the documented finite dynamic sink matrix,
  purpose-specific URL filters, and explicit HTML-body trust crossing pass adversarial tests;
- page assets are static, conditional assets are fragment-only, and capability/policy mismatch
  behavior is explicit;
- locally provable HTMX syntax/capability checks do not claim route, accessibility, lifecycle, or
  browser-behavior proof;
- capability reporting and explicit application-policy mismatch diagnostics prove that freedom
  never causes silent policy weakening; full SecurityPolicy/CSP reconciliation is phase 0.11;
- clean package, supported Python/Jinja/MarkupSafe, static composition, and resource-limit evidence
  passes; and
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
