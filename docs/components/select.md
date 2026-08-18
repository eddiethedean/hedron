---
title: Select
description: Choose one value from server-defined label/value options.
---

# `Select`

Choose one value from server-defined label/value options.

| | |
|---|---|
| Import | `from hedron import Select` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Select"><div class="hdc-stage"><div class="hdc-form"><label for="demo-region">Region</label><select id="demo-region"><option>US East</option><option>Europe</option><option>Asia Pacific</option></select></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Select

component = Select('region', [('iad', 'US East'), ('fra', 'Europe')], value='iad')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Options are explicit value/label pairs and the selected value is matched server-side during rendering. The result is a native single-select.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Select(name, options, *, id=None, required=False, value=None, depends_on=None, source=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Submitted field name. |
| `options` | `Sequence[tuple[str, str]]` | Value/label pairs. |
| `id` | `str | None` | Control ID. |
| `required` | `bool` | Native required constraint. |
| `value` | `str | None` | Selected option value. |
| `depends_on` | `str | None` | Parent field name; compiles `hx-trigger="change from:#field-{dom_id_part(name)}"`. |
| `source` | `str | None` | Child `hx-get` fragment that synthesizes options. |

## Composition and backend behavior

Keep `Select` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Select` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

Use meaningful option labels and include a non-value prompt option when no default is appropriate.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Validate the submitted value against the authoritative server-side option set.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
