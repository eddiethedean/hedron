---
status: shipped
---

# HDJ authoring API

!!! note "Name and stability"

    HDJ means **Hedron Jinja**. The distribution is `hedron-jinja`, the import is
    `hedron_jinja`, and `.hdj` is the explicit, versioned template format. After a small static
    TOML prologue, the body is ordinary Jinja and HTML.

    **Package maturity:** Beta on the living **0.27** train (HDJ introduced earlier).
    The phase 0.9 core authoring surface is **shipped**. Remaining RFC-0031 capability
    edges continue to close without blocking basic `.hdj` use—see [STABILITY](STABILITY.md)
    and [What’s ready](../guides/whats-ready.md).

HDJ is the optional HTML-first authoring surface for advanced Hedron applications. It combines
normal Jinja and HTMX with typed Hedron components and preserves `RenderResult` metadata.

## What HDJ does—and does not do

HDJ does:

- let you write native HTML, CSS, JavaScript, custom elements, and HTMX directly;
- preserve static Jinja inheritance/includes, macros, filters, tests, loops, explicitly configured
  i18n, and core async rendering;
- render explicitly bound Hedron components with typed props and slots;
- merge component assets, approved headers, identity, diagnostics, and traces; and
- check the format-v1 dynamic sink matrix, static dependencies, assets, and locally inferable
  deployment capabilities.

HDJ does not replace HTML with component wrappers, make templates safe for hostile authors, expose
every Python component, or silently relax CSP/CSRF/authorization policy.

## Install

```bash
pip install "hedron[jinja]>=0.27.0,<0.28"
# or
pip install "hedron-jinja>=0.27.0,<0.28"
```

Neither `hedron-core` nor a default `hedron` installation depends on Jinja.

## Setup

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

from hedron_jinja import HedronJinja

environment = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(("hdj",)),
)
templates = HedronJinja(
    environment,
    components={"Card": Card, "StatusBadge": StatusBadge},
    strict=True,
)
```

Bindings are application-local and freeze on the first check or render. Configure Jinja loaders,
bytecode cache, i18n, extensions, application filters, tests, and globals before binding.

## Template contract

```python
from hedron import Model
from hedron_jinja import TemplateSpec


class DashboardView(Model):
    heading: str
    rows: tuple[RowView, ...]
    urls: DashboardUrls


DASHBOARD = TemplateSpec(
    "dashboard/index.hdj",
    view_type=DashboardView,
)

result = templates.render(DASHBOARD, view, context=context)
```

`view` is a Hedron `Model`, a plain materialized `dict`, or an immutable mapping proxy. Custom root
mapping implementations are rejected; applications must also materialize bounded nested
collections instead of passing lazy/query-backed values.

The supplied value is available as `view`; fields are not flattened into the template namespace.
The complete target contract also exposes an immutable `hdj` facade for mode, locale/theme, portable
HTMX request facts, reverse URLs, assets, scoped styles, validated attributes, and CSRF markup.

The source prologue owns template kind and feature availability. A `TemplateSpec.mode` value may
assert the expected kind for application wiring, but cannot override a mismatch.

## `.hdj` format

Every HDJ file begins with a TOML prologue:

```hdj
---hdj
version = 1
kind = "page"
profile = "standard"
assets = ["app:dashboard.css", "app:dashboard.mjs"]
regions = ["main", "notices"]
---
<!doctype html>
<html lang="{{ hdj.locale }}">
  <head><meta charset="utf-8"><title>Dashboard</title></head>
  <body><!-- ordinary Jinja and HTML from here down --></body>
</html>
```

Only `version`, `kind`, and `profile` are required. Profiles keep common templates concise:

| Profile | Available surface |
|---|---|
| `minimal` | `web.html` and `jinja.core` |
| `standard` | Minimal plus `web.css`, Jinja composition, stable Hedron bridges, HTMX core/history/OOB, and registered browser modules |
| `full` | Standard plus native JavaScript/custom elements and advanced HTMX events/selectors/transitions |
| `custom` | Only invariant parsing, escaping, secret, loader, and metadata boundaries plus the IDs in `features` |

Use `features` for additions or the complete custom set. Feature IDs are namespaced (`web.*`,
`jinja.*`, `hedron.*`, `htmx.*`, and `browser.*`). Provider-bound features—custom Jinja
extensions, i18n/do/loop-controls/async, data, charts, and individual HTMX extensions—need their own
ID, even under `full`. The normative profile-to-ID expansion is in RFC-0031.

Use `requires` for deployment capabilities such as `browser.inline-style`,
`browser.inline-script`, `htmx.eval`, `htmx.response-scripts`, or an approved remote origin. It is
an assertion for the checker, not permission: application SecurityPolicy and CSP still decide
whether rendering may ship. `assets` and `regions` make the production inventory explicit.

An advanced template can be equally explicit without enumerating the built-in full profile:

```toml
profile = "full"
features = ["hedron.charts", "htmx.extension:idiomorph"]
requires = ["browser.inline-style", "htmx.eval"]
```

Unknown keys/features, unavailable explicit provider features, used-but-undeclared features, and
under-declared capabilities fail checked builds. Profiles are allowed surfaces, so their unused
members do not warn; unused explicit additions and harmless over-declarations do. The prologue is
static—no Jinja expressions or executable values are permitted.

## Standards-first template

```jinja
---hdj
version = 1
kind = "page"
profile = "standard"
assets = ["app:dashboard.css"]
regions = ["main", "results"]
---
{% extends "layouts/app.hdj" %}

{% block content %}
  <main id="main" hx-history-elt>
    <h1>{{ view.heading }}</h1>

    <form action="{{ view.urls.search_action|hedron_form_url }}"
          method="get"
          hx-get="{{ view.urls.search|hedron_nav_url }}"
          hx-target="#results"
          hx-trigger="input changed delay:300ms from:find input"
          hx-sync="this:replace"
          hx-indicator="#search-progress">
      <label for="query">Search</label>
      <input id="query" name="q" value="{{ view.query }}">
      <span id="search-progress" class="htmx-indicator" role="status">Searching…</span>
      <button type="submit">Search</button>
    </form>

    <section id="results" aria-live="polite">
      {% for row in view.rows %}
        {% hedron "StatusBadge" text=row.label tone=row.tone key=row.id %}
      {% else %}
        <p>No matches.</p>
      {% endfor %}
    </section>
  </main>
{% endblock %}
```

The link/form fallback, Jinja loop, HTMX interaction, native accessibility semantics, and Hedron
component all remain visible. HDJ adds no alternative interaction language.

## Components and slots

Inline:

```jinja
{% hedron "StatusBadge" text=view.status compact=true %}
```

Body and named slot:

```jinja
{% hedron "Card" title=view.heading with body %}
  <p>{{ view.summary }}</p>
  {% slot "footer" %}
    {% hedron "AccountMenu" account_id=view.account_id %}
  {% endslot %}
{% endhedron %}
```

Aliases and slots are static strings, props are named, and `key=` is reserved for Hedron identity.
`with body` is required for a block call. Evaluated props still pass the component's runtime props
validation even when static checking succeeds.

## Jinja features

Use standard Jinja directly:

- inheritance, blocks, `super()`, includes, imports, macros, and `call`;
- conditions, loops, recursive loops, `set`, namespaces, filters, and tests;
- whitespace control, comments, i18n, `do`, and loop controls when enabled; and
- explicit application filters/globals plus transparent async behavior in `render_async()`.

Format-v1 production builds accept only static `.hdj` dependencies. Dynamic candidate manifests,
foreign Jinja, and package namespace interoperation are scheduled for phase 0.11; ordinary Jinja can
run alongside HDJ in a separate environment today.

## HTML, CSS, and JavaScript

Literal template source is trusted application code, so native markup remains available:

```jinja
<style>
  .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr)); }
</style>

<app-command-palette data-endpoint="{{ view.urls.commands|hedron_nav_url }}"></app-command-palette>

<script type="module" src="{{ view.assets.dashboard|hedron_asset_url }}"></script>
```

Registered CSS/modules are preferred when you need fingerprinting, deduplication, dependency
inspection, fragment delivery, or strict CSP. Phase 0.9 supports unconditional page/prologue assets
and branch-dependent fragment `{% hedron_asset "logical-id" %}` declarations. Conditional page-head
assets and registered head management are phase 0.10.

Inline source is not silently blocked by the HDJ grammar, but it must match application policy.
Format v1 reports inline script/style, obvious HTMX eval, response script processing,
purpose-specific remote origins, and fragment head mutation. Provider/extension evidence and full
`SecurityPolicy`/CSP reconciliation are phases 0.14 and 0.11 respectively. HDJ never inserts
`unsafe-inline`, `unsafe-eval`, remote CSP origins, or permissive HTMX settings for you.

For dynamic data:

- ordinary expressions are HTML-escaped;
- raw markup requires `TrustedHtml|hedron_trusted` in HTML body content;
- dynamic URLs require `SafeUrl|hedron_nav_url`, `|hedron_form_url`, or
  `|hedron_asset_url` for the destination sink;
- bounded JavaScript/JSON data uses Jinja's `tojson` in a valid JSON/JS context; and
- arbitrary dynamic CSS, script source, event bodies, tag names, and attribute names require an
  explicit advanced trust adapter or unchecked application policy.

`strict=False` restores conventional trusted-Jinja freedom for those dynamic contexts. It does not
disable secret redaction, component authorization, response-header validation, or loader isolation.

## HTMX

All pinned HTMX 2 attributes are written directly as ordinary HTML. Format v1 observes feature and
capability categories for:

- request/history URL attributes that need purpose-specific `SafeUrl` filters;
- obvious eval contexts such as `hx-on:*` and `js:` values;
- history/OOB/event profile usage; and
- literal remote request origins.

Dynamic URLs use `SafeUrl`. Unsafe actions still require framework authorization and CSRF, but
native adapter enforcement is phase 0.11. Version-aware attribute/selector validation and
navigation/history/OOB/focus/browser evidence are phase 0.10.

Format v1 dynamic navigation and form URLs are local. External registered asset URLs are allowed
only through `hdj.asset_url()` after static declaration and purpose-specific origin policy. Native
dynamic-origin reconciliation is phase 0.11.

Hedron's managed runtime keeps HTMX eval and response script processing disabled by default.
Advanced applications may enable either explicitly. Registered ES modules listening to
`htmx:load`, `htmx:afterSwap`, `htmx:beforeCleanupElement`, and `htmx:beforeHistorySave` are the
recommended lifecycle path for durable client behavior.

Response-side interaction remains typed through `HtmxRequestFacts`, `InteractionResult`, status
policies, approved `HX-*` response headers, fragment regions, OOB updates, and cache variation.
Templates cannot authorize a response target or action merely by spelling it.

## Rendering and metadata

```python
result = templates.render(spec, view, context=context)
result = await templates.render_async(spec, view, context=context)
```

Both return `hedron_core.RenderResult`. Every `.hdj` source requires the active guarded render
session; direct `Template.render()` always fails because a bare string would bypass prologue,
kind, capability, policy, and metadata contracts.

PAGE templates own one complete document and use static source/application assets in 0.9. FRAGMENT
templates cannot emit document elements and may declare conditional registered assets when
`browser.head-mutation` is declared and allowed.

## Checking and capability inspection

```python
declaration = templates.describe(DASHBOARD)
assert "htmx.history" in declaration.effective_features

diagnostics = templates.check(DASHBOARD)
capabilities = templates.capabilities(DASHBOARD)
```

`describe()` returns the parsed format version, kind, profile, declared and effective features,
requirements, assets, regions, source digest, and body start line without rendering. Format v1
rejects dynamic dependencies rather than exposing dependency-bound namespaces; finite fingerprinted
manifests arrive in phase 0.11. Checking covers static template dependencies, component/slot/view
contracts, the finite contextual sink matrix, assets, locally inferable HTMX capabilities, render
shape, and enforceable resource limits. Route and response integration is phase 0.11; version-aware
HTMX and browser evidence is phase 0.10; broader contextual/provider analysis is phase 0.14.
Capability inspection separately describes the format-v1 facts that an application policy must
reconcile.

See [RFC-0031](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0031-JINJA-INTEGRATION.md) for the normative feature matrix, trust model,
HTMX contract, lifecycle, inventory, and acceptance requirements.
