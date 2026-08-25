# Integrated styling and application CSS (proposed 0.65 API)

Status: **Implemented for the bounded 0.65 issue slices.** The original application-CSS surface
remains staged under D-110; the four follow-up presentation contracts below are implemented and
covered by the 0.65 release evidence. The Required/Progressive boundary is recorded in the
[refined scope](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/application-styling-scope-065.md).
See [RFC-0092](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md).

## Authoring model

```python
app.styles(
    name: str,
    source: str | Path,
    *,
    scope: str | None = None,
    layer: Literal["application", "overrides"] = "application",
    global_: bool = False,
    media: tuple[str, ...] = (),
)
```

This is a candidate Stage 0 signature, not an implemented API. `source` must resolve to a local,
package-owned asset. `scope` emits a stable root hook such as `data-hedron-style-scope="app"`;
`global_` is an explicit opt-in and is rejected when the source violates the global-CSS policy.
`media` is a finite, manifest-recorded list rather than an arbitrary response-time condition.

The registration API must accept only local, package-owned assets and produce a stylesheet manifest
with source path, fingerprint, layer, scope, CSP disposition, and provenance. A stylesheet is not
implicitly loaded because a file happens to exist.

The supported authoring ladder is semantic props → theme/recipes → registered application CSS →
explicit scoped/global CSS → ejected CSS. Ordinary CSS remains ordinary CSS; Hedron adds ownership,
ordering, diagnostics, and stable hooks around it.

The precedence contract is generated reset/tokens/base/components, then registered application CSS,
then explicit utility and override layers. Existing semantic behavior, interaction ownership, route
state, and accessibility semantics are not style override points. An application stylesheet may
change presentation only within the public hook and token contracts.

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

The first Required public part/state inventory is deliberately finite:

- `AppShell.nav.link`: default, hover, current, disabled;
- `ProcessFlow.step`: current, complete, blocked, skipped;
- `Card`: heading, supporting copy, metadata;
- `FormField`: control, focus, invalid, disabled;
- `SplitView`: separator and responsive collapse.

Additional component parts, slots, and state names require a later manifest decision; private
descendant selectors and user-supplied selector values are rejected by the contract.

## Tokens and cascade

Application tokens use a namespace owned by the registering package or application. They compose
with the existing ThemeSpec/ThemePatch graph, carry provenance, and cannot overwrite a core token
without an explicit compatibility error. The proposed layer order is:

```css
@layer reset, tokens, base, components, application, utilities, overrides;
```

The `application` layer is explicit and inspectable. Global CSS requires an explicit opt-in and
cannot bypass CSP, source maps, unsafe-at-rule checks, or the public-hook policy.

Required issue slices are bounded to six named motion recipes (`instant`, `standard`, `emphasized`,
`reveal`, `elevate`, `crossfade`), semantic data-view/table chrome tokens, and native-first control
families for checkbox/radio, select, range, file, date/time, and number inputs. These slices must
provide the states and fallbacks listed in the acceptance contract; they do not imply a product-wide
restyling of every component.

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

## Implemented issue slices #712–#715

- `AmbientLayer` and `AmbientCanvas` provide ordered, inert document layers. `AmbientBackdrop`
  accepts `layers=` as a compatibility entry point.
- `AppShellChrome` is passed as `AppShell(chrome=...)` and emits finite geometry-policy markers
  for presets, sticky behavior, offsets, gaps, insets, spacing, and density.
- `presentation_token_manifest()` reports declared, consumed, overridden, and unconsumed built-in
  presentation tokens. Bundled CSS consumes the emitted typography, layout, geometry, motion, data,
  and control variables with compatibility fallbacks.
- `ResponsiveCondition` supports `viewport-max`, `container-max`, `viewport-range`, and
  `container-range` (for example `md-to-lg`), with deterministic ordering and contradiction
  diagnostics.

## Required behavior contracts

- focus-visible, invalid, disabled, busy, and reduced-motion behavior remains accessible on every
  touched surface;
- native controls retain usable browser fallback when appearance customization is unsupported;
- data views expose semantic header/body/empty/loading/error chrome rather than visual-only states;
- print, forced-colors/high-contrast, reduced-transparency, RTL where applicable, responsive
  overflow, and no-JS paths are explicit on every touched surface;
- CSS cannot change route, effect, authorization, interaction state ownership, or semantic markup;
- package and adapter support is declared per surface, with no universal compatibility claim.
