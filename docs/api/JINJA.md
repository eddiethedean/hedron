---
status: implementing
---

# HDJ authoring API

!!! note "Name and stability"

    HDJ means **Hedron Jinja**. The distribution is `hedron-jinja`, the import is
    `hedron_jinja`, and `.hdj` is the explicit, versioned template format. After a small static
    TOML prologue, the body is ordinary Jinja and HTML. The phase 0.9 core is implemented; the
    complete RFC-0031 capability surface is still being closed.

HDJ is the optional HTML-first authoring surface for advanced Hedron applications. It combines
normal Jinja and HTMX with typed Hedron components and preserves `RenderResult` metadata.

## What HDJ does—and does not do

HDJ does:

- let you write native HTML, CSS, JavaScript, custom elements, and HTMX directly;
- preserve Jinja inheritance, includes, macros, filters, tests, loops, i18n, and async support;
- render explicitly bound Hedron components with typed props and slots;
- merge component assets, approved headers, identity, diagnostics, and traces; and
- check dynamic values, dependencies, HTMX semantics, assets, and deployment capabilities.

HDJ does not replace HTML with component wrappers, make templates safe for hostile authors, expose
every Python component, or silently relax CSP/CSRF/authorization policy.

## Install

```bash
pip install "hedron[jinja]"
# or
pip install hedron-jinja
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
  <!-- ordinary Jinja and HTML from here down -->
</html>
```

Only `version`, `kind`, and `profile` are required. Profiles keep common templates concise:

| Profile | Available surface |
|---|---|
| `minimal` | `web.html` and `jinja.core` |
| `standard` | Minimal plus `web.css`, Jinja composition, stable Hedron bridges, HTMX core/history/OOB, and registered browser modules |
| `full` | Standard plus native JavaScript/custom elements, Jinja i18n/do/loop-controls/async/dynamic dependencies, and advanced HTMX events/selectors/transitions |
| `custom` | Only invariant parsing, escaping, secret, loader, and metadata boundaries plus the IDs in `features` |

Use `features` for additions or the complete custom set. Feature IDs are namespaced (`web.*`,
`jinja.*`, `hedron.*`, `htmx.*`, and `browser.*`). Provider-bound features—custom Jinja
extensions, foreign templates, data, charts, and individual HTMX extensions—always need their own
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

Unknown keys/features, unavailable features, used-but-undeclared features, and under-declared
capabilities fail checked builds. Unused features and harmlessly over-declared capabilities produce
diagnostics. The prologue is static—no Jinja expressions or executable values are permitted.

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

    <form action="{{ view.urls.search|hedron_url }}"
          method="get"
          hx-get="{{ view.urls.search|hedron_url }}"
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

Strict production builds inventory static `.hdj` dependencies. Dynamic inheritance/includes must
name bounded loader namespaces in the prologue because they cannot otherwise produce a complete
deterministic build graph. Third-party plain Jinja sources require the explicit `jinja.foreign`
feature and a namespaced foreign loader; they cannot use Hedron tags.

## HTML, CSS, and JavaScript

Literal template source is trusted application code, so native markup remains available:

```jinja
<style>
  .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr)); }
</style>

<app-command-palette data-endpoint="{{ view.urls.commands|hedron_url }}"></app-command-palette>

<script type="module" src="{{ view.assets.dashboard|hedron_url }}"></script>
```

Registered CSS/modules are preferred when you need fingerprinting, deduplication, dependency
inspection, fragment delivery, or strict CSP. The complete phase 0.9 contract supports unconditional
prologue `assets` and branch-dependent `{% hedron_asset "logical-id" %}` declarations.

Inline source is not silently blocked by the HDJ grammar, but it must match the application's
`SecurityPolicy`. HDJ reports requirements such as inline script/style, HTMX eval, response script
processing, remote origins, extensions, and fragment head mutation. It never inserts
`unsafe-inline`, `unsafe-eval`, remote CSP origins, or permissive HTMX settings for you.

For dynamic data:

- ordinary expressions are HTML-escaped;
- raw markup requires `TrustedHtml|hedron_trusted`;
- dynamic URLs require a purpose-compatible `SafeUrl|hedron_url`;
- bounded JavaScript/JSON data uses Jinja's `tojson` in a valid JSON/JS context; and
- arbitrary dynamic CSS, script source, event bodies, tag names, and attribute names require an
  explicit advanced trust adapter or unchecked application policy.

`strict=False` restores conventional trusted-Jinja freedom for those dynamic contexts. It does not
disable secret redaction, component authorization, response-header validation, or loader isolation.

## HTMX

All pinned HTMX 2 attributes are written directly. HDJ understands and checks:

- request verbs, triggers, polling, debounce/throttle/queues, and `hx-sync`;
- targets, swaps/modifiers, selection, OOB swaps, and preserved elements;
- boost, push/replace URL, history snapshots, and history restoration;
- includes, parameters, JSON values/headers, multipart encoding, prompts, and confirmation;
- indicators, disabled controls, validation, inheritance/disinheritance; and
- registered `hx-ext` assets plus HTMX lifecycle events.

Dynamic URLs use `SafeUrl`. Unsafe actions still require framework authorization and CSRF.
Executable `hx-on:*`, `js:` values, and trigger filters require the application's HTMX eval/CSP
capability. History-changing URLs must also serve a complete ordinary page. OOB targets must match
declared fragment regions.

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

Both return `hedron_core.RenderResult`. Hedron components and conditional assets require the active
HDJ render session; direct `Template.render()` fails when it encounters those bridges because a bare
string would lose metadata.

PAGE templates own one complete document. FRAGMENT templates cannot emit document elements in
checked mode and may require only assets already present unless a registered head-management path
is active.

## Checking and capability inspection

```python
declaration = templates.describe(DASHBOARD)
assert "htmx.history" in declaration.effective_features

diagnostics = templates.check(DASHBOARD)
capabilities = templates.capabilities(DASHBOARD)  # phase 0.9 target
```

`describe()` returns the parsed format version, kind, profile, declared and effective features,
requirements, assets, regions, and dynamic dependency bounds without rendering. Checking covers
template dependencies, component/slot/view contracts, contextual dynamic values,
assets, HTMX semantics, accessibility, render shape, and resource limits. Capability inspection
separately describes what the trusted source needs from CSP, HTMX runtime configuration, remote
origins, and extensions.

See [RFC-0031](../rfcs/RFC-0031-JINJA-INTEGRATION.md) for the normative feature matrix, trust model,
HTMX contract, lifecycle, inventory, and acceptance requirements.
