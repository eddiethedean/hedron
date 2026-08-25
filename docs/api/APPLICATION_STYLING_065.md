# Integrated styling and application CSS (proposed 0.65 API)

Status: **Proposed; not implemented or Supported.** The exact names below are contract candidates
for Stage 0 refinement under D-110. See [RFC-0092](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md).

## Authoring model

```python
app.styles(
    "application",
    "styles/app.css",
    layer="application",
    scope="app",
)
```

The registration API must accept only local, package-owned assets and produce a stylesheet manifest
with source path, fingerprint, layer, scope, CSP disposition, and provenance. A stylesheet is not
implicitly loaded because a file happens to exist.

The supported authoring ladder is semantic props → theme/recipes → registered application CSS →
explicit scoped/global CSS → ejected CSS. Ordinary CSS remains ordinary CSS; Hedron adds ownership,
ordering, diagnostics, and stable hooks around it.

## Public hooks

Rendered markup may expose manifest-backed attributes such as:

```html
<div data-hedron-component="data-view"
     data-hedron-part="header"
     data-hedron-state="loading">
</div>
```

Component names, parts, slots, and state values are public only when present in the versioned hook
manifest. Generated class names and DOM shapes not listed in that manifest are private and may
change in a patch release. Typed selector helpers are Progressive until their generated metadata
and compatibility rules are frozen.

## Tokens and cascade

Application tokens use a namespace owned by the registering package or application. They compose
with the existing ThemeSpec/ThemePatch graph, carry provenance, and cannot overwrite a core token
without an explicit compatibility error. The proposed layer order is:

```css
@layer reset, tokens, base, components, application, utilities, overrides;
```

The `application` layer is explicit and inspectable. Global CSS requires an explicit opt-in and
cannot bypass CSP, source maps, unsafe-at-rule checks, or the public-hook policy.

## Diagnostics and ejection

Candidate static commands:

```text
hedron style explain <surface> [--property <name>]
hedron style inspect <manifest-or-source>
hedron style check --custom-css
hedron style eject <surface> [--output <path>]
hedron style diff <ejected-path>
hedron style update --check
```

Diagnostics identify the winning declaration, layer, selector/hook, token, source asset, and
fallback. Output is deterministic and redacted. Ejected blocks retain source-map and manifest
provenance; generated blocks are never silently overwritten by `update`.

## Required behavior contracts

- focus-visible, invalid, disabled, busy, and reduced-motion behavior remains accessible;
- native controls retain usable browser fallback when appearance customization is unsupported;
- data views expose semantic header/body/empty/loading/error chrome rather than visual-only states;
- print, forced-colors, contrast, reduced-transparency, RTL, and no-JS paths are explicit;
- CSS cannot change route, effect, authorization, interaction state ownership, or semantic markup;
- package and adapter support is declared per surface, with no universal compatibility claim.
