---
status: shipped
---

# Jinja integration API

!!! note "Stability"

    This surface replaces HDN in phase 0.9. It is optional in packaging but is the only first-party
    template integration; typed Python components remain canonical.

Hedron's optional Jinja integration composes trusted application templates with allowlisted typed
Hedron components while preserving `RenderResult` metadata.

## Install

```bash
pip install "hedron[jinja]"
# or: pip install hedron-jinja
```

The package imports as `hedron_jinja`. Neither `hedron-core` nor a default `hedron` installation
depends on Jinja.

## Setup

```python
from jinja2 import Environment, FileSystemLoader

from hedron_jinja import HedronJinja

environment = Environment(loader=FileSystemLoader("templates"), autoescape=True)
templates = HedronJinja(
    environment,
    components={"Card": Card, "StatusBadge": StatusBadge},
    strict=True,
)
```

Bindings are application-local and freeze on the first check or render. Template code cannot import
or enumerate Python components.

## Template contracts

```python
from hedron import Model, RenderMode
from hedron_jinja import TemplateSpec


class DashboardView(Model):
    heading: str
    rows: tuple[RowView, ...]


DASHBOARD = TemplateSpec(
    "dashboard.html",
    view_type=DashboardView,
    mode=RenderMode.PAGE,
)

result = templates.render(DASHBOARD, DashboardView(heading="Status", rows=rows))
```

The supplied value is available only as `view`. Mapping-based rendering is supported for migration,
but typed `Model` view contracts are recommended.

## Component tags

Inline:

```jinja
{% hedron "StatusBadge" status=view.status compact=true %}
```

With body and named slot:

```jinja
{% hedron "Card" title=view.heading with body %}
  <p>{{ view.summary }}</p>
  {% slot "footer" %}
    {% hedron "AccountMenu" account_id=view.account_id %}
  {% endslot %}
{% endhedron %}
```

Aliases and slot names are string literals. Props are named. `key=` is reserved for Hedron identity.
Dynamic aliases, spread props, template-level Python imports, and `slot` outside a component block
are rejected. A block component must end its opening tag with the literal `with body`; without that
marker the component is inline and must not have an `{% endhedron %}` tag.

## Rendering

```python
result = templates.render(spec, view, context=context)
result = await templates.render_async(spec, view, context=context)
```

Both operations return `hedron_core.RenderResult`. Async rendering permits Jinja async operations
in an async-enabled environment; Hedron component rendering remains synchronous and free of hidden
I/O.

Hedron tags work only inside these operations. Calling Jinja's `Template.render()` directly fails
when it reaches a Hedron tag because a bare HTML string cannot preserve component assets, approved
headers, identities, diagnostics, and traces.

## Checking

```python
diagnostics = templates.check(DASHBOARD)
```

The checker validates static template dependencies, component aliases, prop names and required
props, literal types, slots, typed `view.field` paths, page/fragment shape, and strict security
rules. Runtime props validation remains mandatory because general Jinja expressions cannot always
be typed statically.

## Strict mode

Strict mode is the default and requires `StrictUndefined` plus HTML autoescape. It rejects Jinja's
`safe` filter, dynamic component/include names, unsafe dynamic URL attributes, dynamic style/script/
event/srcdoc contexts, lazy iterators, and secret rendering.

Trusted markup uses `TrustedHtml` with `|hedron_trusted`. Dynamic URL attributes use a
purpose-compatible `SafeUrl` with `|hedron_url`. Templates are still trusted application code;
strict mode and `SandboxedEnvironment` do not support hostile template authors.

## Registration

```python
templates.register_component("Card", Card)
templates.freeze()
```

Registration after freeze, duplicate aliases, invalid names, and factories without an inspectable
props contract fail. Framework adapters bind an existing Flask environment or a named Django Jinja2
backend and convert the returned `RenderResult` through their normal response policy.

See [RFC-0031](../rfcs/RFC-0031-JINJA-INTEGRATION.md) for the complete grammar, lifecycle, metadata,
security, packaging, diagnostics, migration, and acceptance contract.
