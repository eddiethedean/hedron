# HDN templates (`.hdn`)

!!! warning "Experimental and scheduled for removal"

    D-040 and RFC-0031 select a separate optional Jinja integration and schedule HDN deprecation in
    0.11, default-discovery removal in 0.12, and first-party runtime removal in 0.13. This guide
    documents the shipped prototype only for existing users and migration work. Prefer typed Python
    components today; the Jinja adapter is planned, not shipped on the current train.

The current Hedron Discovery Notation (HDN) prototype lets component folders ship markup templates
next to Python. The canonical and only discovered legacy filename is `template.hdn`.

## Discovery

Component discovery looks for `template.hdn`. Other extensions are not treated as HDN source.

## Authoring

1. Create a component folder under a configured `component_roots` path.
2. Add `template.hdn` with HDN markup and a Python module that registers the component.
3. Run `hedron check` / tests to validate discovery.

Eject / scaffold tooling writes `template.hdn` for new overrides (`hedron eject`).

## Interpolation and attributes

Lowercase tags render native HTML. Put an expression in braces to render a value or to
set a dynamic attribute. HDN uses HTML attribute names such as `class` and `for` rather
than React's `className` and `htmlFor` aliases.

```html title="template.hdn"
<section class="status-banner" data-tone={tone}>
  <strong>{label}</strong>
  <p>{detail ?? "No additional detail."}</p>
</section>
```

Here `label`, `detail`, and `tone` come from the template's render scope. Expression
output is escaped, including values rendered in attributes. The `??` operator supplies a
fallback only when its left-hand value is null.

## Conditions and lists

Use `{#if}` with an optional `{:else}` branch, and `{#for}` to repeat markup. A loop
variable can expose public object attributes or mapping keys with dot notation.

```html title="template.hdn"
<ul aria-label="Team members">
  {#for member in members}
    <li>
      <span>{member.name}</span>
      {#if member.active}
        <strong>Active</strong>
      {:else}
        <span>Inactive</span>
      {/if}
    </li>
  {/for}
</ul>
```

HDN expressions support literals, property and index access, boolean and comparison
operators, arithmetic, conditional expressions, and the registered pure helpers `len`,
`str`, `int`, `bool`, and `enum_name`. They cannot import modules, inspect private
attributes, or call arbitrary functions.

## Components, fragments, and slots

An uppercase tag resolves a Hedron component. Make that dependency explicit with a
top-level `{@import ...}` declaration whose string is the component's stable logical ID.
The local name can be an alias, so the tag does not have to match the Python class name.

```html title="template.hdn"
{@import Card from "hedron-core:hedron_core.builtins.surfaces.Card"}
{@import Copy from "hedron-core:hedron_core.builtins.content.Text"}

<>
  <Card>
    <Copy content={title} />
    <slot name="actions">
      <Copy content="No actions available" />
    </slot>
  </Card>
</>
```

Imports must appear before markup and are declarative: HDN never imports a Python module
or reads a source path. Once a template declares any imports, every uppercase tag must
have a matching declaration. Templates without imports continue to use tag-name lookup,
so explicit imports can be adopted per template.

The host provides imported implementations by logical ID when it executes a render
program:

```python
from hedron import Card, Text
from hedron_core import compile_hdn, run_program

program = compile_hdn(source).program
nodes = run_program(
    program,
    {"title": "Account"},
    components={
        "hedron-core:hedron_core.builtins.surfaces.Card": Card,
        "hedron-core:hedron_core.builtins.content.Text": Text,
    },
)
```

The compiler records imported logical IDs in `RenderProgram.dependencies` and
`RenderProgram.component_imports`; missing declarations and missing host mappings fail
with `HED-HDN-0004`. Fragments group siblings without adding a wrapper element, while
`slot` declares a named or default insertion point. Static classes such as `class="root"`
are where colocated `styles.css` symbols are rewritten to their scoped build names.

## Trusted HTML

Normal interpolation is the default for user-controlled content:

```html title="template.hdn"
<div class="message">{message}</div>
```

Only use `{@html}` when the scope value is already a `TrustedHtml` instance created at a
reviewed trust boundary:

```html title="template.hdn"
<article class="prose">
  {@html sanitized_body}
</article>
```

Passing a plain string to `{@html}` is rejected at runtime. See the
[`TrustedHtml` API](../api/SECURITY_TYPES.md#trustedhtml) for the supported trust-boundary
methods.

## Complete examples

The repository includes two small, runnable templates:

- [`StatusBanner/template.hdn`](https://github.com/eddiethedean/hedron/blob/main/examples/reference-app/components/StatusBanner/template.hdn)
  is compiled and rendered by the FastAPI reference application.
- [`Callout/template.hdn`](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sample-kit/src/hedron_sample_kit/components/Callout/template.hdn)
  shows the colocated component layout used by a distributable plugin.

## Relation to Python components

HDN is optional. Many apps use pure Python `html.*` / built-ins without templates.
Templates are for authoring convenience and Explorer-friendly structure—not a second
runtime.

## See also

- [Component API](../api/COMPONENT.md)
- [Upgrade notes](upgrade.md)
- [Glossary](../GLOSSARY.md)
