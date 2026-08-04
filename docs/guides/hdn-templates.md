# HDN templates (`.hdx`)

Hedron Discovery Notation (HDN) lets component folders ship markup templates next to
Python. On the 0.8 train the **preferred filename is `template.hdx`** (JSX-familiar).
Legacy `template.hdn` remains a discoverable compatibility fallback.

## Discovery

When both `template.hdx` and `template.hdn` exist in a component folder, discovery uses
`.hdx` and may log a warning. Prefer renaming to `.hdx` when convenient.

## Authoring

1. Create a component folder under a configured `component_roots` path.
2. Add `template.hdx` with HDN markup and a Python module that registers the component.
3. Run `hedron check` / tests to validate discovery.

Eject / scaffold tooling writes `.hdx` for new overrides (`hedron eject`).

## Interpolation and attributes

Lowercase tags render native HTML. Put an expression in braces to render a value or to
set a dynamic attribute. HDN uses HTML attribute names such as `class` and `for` rather
than React's `className` and `htmlFor` aliases.

```html title="template.hdx"
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

```html title="template.hdx"
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

An uppercase tag resolves a registered Hedron component. Fragments group siblings
without adding a wrapper element, and `slot` declares a named or default insertion point.

```html title="template.hdx"
<>
  <Card>
    <Text content={title} />
    <slot name="actions">
      <Text content="No actions available" />
    </slot>
  </Card>
  <StatusBadge label={status} />
</>
```

The component names must be present in the render registry. Static classes such as
`class="root"` are also where colocated `styles.css` symbols are rewritten to their
scoped build names.

## Trusted HTML

Normal interpolation is the default for user-controlled content:

```html title="template.hdx"
<div class="message">{message}</div>
```

Only use `{@html}` when the scope value is already a `TrustedHtml` instance created at a
reviewed trust boundary:

```html title="template.hdx"
<article class="prose">
  {@html sanitized_body}
</article>
```

Passing a plain string to `{@html}` is rejected at runtime. See the
[`TrustedHtml` API](../api/SECURITY_TYPES.md#trustedhtml) for the supported trust-boundary
methods.

## Complete examples

The repository includes two small, runnable templates:

- [`StatusBanner/template.hdx`](https://github.com/eddiethedean/hedron/blob/main/examples/reference-app/components/StatusBanner/template.hdx)
  is compiled and rendered by the FastAPI reference application.
- [`Callout/template.hdx`](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sample-kit/src/hedron_sample_kit/components/Callout/template.hdx)
  shows the colocated component layout used by a distributable plugin.

## Relation to Python components

HDN is optional. Many apps use pure Python `html.*` / built-ins without templates.
Templates are for authoring convenience and Explorer-friendly structure—not a second
runtime.

## See also

- [Component API](../api/COMPONENT.md)
- [Upgrade notes](upgrade.md) (0.7 → 0.8 `.hdx` preference)
- [Glossary](../GLOSSARY.md)
