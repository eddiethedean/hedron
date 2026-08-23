---
description: A visual guide to Hedron's presentation tokens, themes, layout, recipes, and CSS boundaries.
search:
  boost: 1.5
---

<div class="styling-guide" markdown>

<div class="sg-hero" markdown>

<p class="sg-kicker">Presentation · themes · CSS boundaries</p>

# Style the whole interface, one vocabulary at a time

Hedron styling starts with semantic Python props and ends as ordinary HTML, CSS, and
`data-hedron-*` markers. Use the built-ins for the common 80%, a `DesignSystem` for
brand-wide decisions, and scoped CSS when a component genuinely owns a visual detail.

<p class="sg-lede">This page is a visual tour of the styling surface: see the result first, then copy the smallest useful Python pattern.</p>

</div>

!!! note "What is new in 0.60"

    0.60 completes the custom-theme platform on top of the 0.59 CSS foundation: typed absolute
    colors with deterministic sRGB fallbacks, immutable `ThemeSpec` / `ThemePatch` authoring,
    registry-derived validation profiles, accessibility-mode mappings, bounded recipe families,
    server-first theme preferences, and zero-application-CSS contracts for the remaining product
    surfaces. The complete capability matrix—including the 0.59 CSS foundation and its
    Progressive, Experimental, and Deferred tiers—is in [Modern CSS in 0.60](modern-css-0.60.md).

### The 0.60 styling upgrade in one view

| Need | 0.60 path | What remains application-owned |
|---|---|---|
| Use a brand palette | `DesignSystem.brand()` or a registered `Theme` | Product identity and content |
| Author a reusable theme | Immutable `ThemeSpec` through `ThemeBuilder` | Which tokens and visual decisions to publish |
| Layer a bounded change | `ThemePatch` / `ThemeSpec.apply_patches()` | Review and approval of the change |
| Validate a theme | `validate_theme_spec()` or `style conform` | The profile that matches the package surface |
| Ship a theme | Data-only `package_theme()` archive | License metadata and distribution |
| Select a preference | `ThemePreference` + `ThemePicker` | Persistence, authorization, and the POST route |
| Style product chrome and workflows | `Brand`, `ToastHost`, `ConnectorFlow`, `ScrollRegion` | Content, state, and actions |

The rule is simple: use the smallest bounded contract that expresses the intent. A custom theme
may add tokens, modes, accessibility mappings, and presentation recipes; it may not add behavior,
private selector APIs, remote assets, or arbitrary CSS values.

## The styling stack

There are four layers. Start at the top and move down only when the layer above cannot
express the intent.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Four layers, one cascade</span><code>intent → tokens → components → local detail</code></div>
  <div class="sg-demo__body">
    <div class="sg-recipe-flow">
      <div class="sg-recipe-node"><strong>Design system</strong><small>brand, density, motion</small></div>
      <span class="sg-recipe-arrow" aria-hidden="true">→</span>
      <div class="sg-recipe-node"><strong>Presentation props</strong><small>appearance, size, gap</small></div>
      <span class="sg-recipe-arrow" aria-hidden="true">→</span>
      <div class="sg-recipe-node"><strong>Scoped CSS</strong><small>component-owned detail</small></div>
    </div>
  </div>
</div>

| Layer | Use it for | Examples |
|---|---|---|
| `DesignSystem` / `Theme` | Brand and app-wide decisions | Accent palette, geometry, typography, dark mode |
| Shared presentation props | Repeated component intent | `appearance="soft"`, `density="compact"`, `gap="lg"` |
| `StyleRecipe` | Semantic feature defaults | `primary_action`, `form_surface`, `metadata` |
| Component `styles.css` | A component's unique visual language | A callout rail, a chart legend, a custom animation |

!!! tip "The shortest path"

    If you are styling a built-in, look for a semantic prop first. If several features
    need the same combination of props, make a recipe. If the style belongs to one
    component and has no useful semantic vocabulary, colocate scoped CSS with that
    component.

## 1. Start with the shared vocabulary

The presentation vocabulary is intentionally finite. That gives themes one predictable
set of hooks and makes invalid combinations fail early instead of becoming one-off CSS.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Palette seed</span><code>accent="#087f75"</code></div>
  <div class="sg-demo__body">
    <div class="sg-palette" aria-label="Example semantic palette">
      <div class="sg-color sg-color--accent"><div class="sg-color__swatch"></div><span class="sg-color__label"><strong>accent</strong>#087f75</span></div>
      <div class="sg-color sg-color--accent-soft"><div class="sg-color__swatch"></div><span class="sg-color__label"><strong>accent-soft</strong>#dff4ef</span></div>
      <div class="sg-color sg-color--ink"><div class="sg-color__swatch"></div><span class="sg-color__label"><strong>fg</strong>#12212b</span></div>
      <div class="sg-color sg-color--muted"><div class="sg-color__swatch"></div><span class="sg-color__label"><strong>muted</strong>#60727d</span></div>
      <div class="sg-color sg-color--surface"><div class="sg-color__swatch"></div><span class="sg-color__label"><strong>surface</strong>#f3f7f7</span></div>
      <div class="sg-color sg-color--danger"><div class="sg-color__swatch"></div><span class="sg-color__label"><strong>danger</strong>#c2413b</span></div>
    </div>
  </div>
</div>

The most-used values are:

<div class="sg-token-row" aria-label="Presentation tokens">
  <span class="sg-token"><b>size</b> sm · md · lg</span>
  <span class="sg-token"><b>density</b> compact · comfortable · spacious</span>
  <span class="sg-token"><b>appearance</b> solid · outline · soft · ghost</span>
  <span class="sg-token"><b>emphasis</b> primary · secondary · danger · neutral</span>
  <span class="sg-token"><b>overflow</b> wrap · break · truncate · clip</span>
  <span class="sg-token"><b>gap</b> none · xs · sm · md · lg · xl</span>
</div>

### Controls: appearance and emphasis are separate

`appearance` describes the treatment; `emphasis` describes the meaning. Keeping them
separate lets one theme make a primary action solid, a secondary action outlined, and a
danger action high-contrast without inventing a new prop for every combination.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Control gallery</span><code>Button</code></div>
  <div class="sg-demo__body">
    <div class="sg-button-row">
      <span class="sg-button sg-button--solid">Primary</span>
      <span class="sg-button sg-button--outline">Secondary</span>
      <span class="sg-button sg-button--soft">Soft</span>
      <span class="sg-button sg-button--ghost">Ghost</span>
      <span class="sg-button sg-button--danger">Danger</span>
      <span class="sg-button sg-button--disabled">Disabled</span>
    </div>
    <div class="sg-button-row sg-button-row--spaced">
      <span class="sg-button sg-button--solid sg-button--sm">Small</span>
      <span class="sg-button sg-button--solid">Medium</span>
      <span class="sg-button sg-button--solid sg-button--lg">Large</span>
    </div>
  </div>
</div>

```python
from hedron import Button

Button("Save changes", appearance="solid", emphasis="primary", size="md")
Button("Cancel", appearance="outline", emphasis="secondary")
Button("Delete workspace", appearance="solid", emphasis="danger")
```

Legacy `variant="primary|secondary|danger"` remains supported. Prefer the shared
`appearance` / `emphasis` vocabulary when you want the full presentation system to
coordinate the result.

## 2. Build hierarchy with layout primitives

Layout components keep spacing and responsive behavior in the same vocabulary as the
rest of the design. Named gaps are CSP-safe and preserve DOM order.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Layout gallery</span><code>Stack · Inline · Grid</code></div>
  <div class="sg-demo__body">
    <div class="sg-layout-grid">
      <div class="sg-layout-box">
        <span class="sg-layout-box__label">Stack(gap="sm")</span>
        <div class="sg-layout-box--stack">
          <span class="sg-layout-box__item">Heading</span>
          <span class="sg-layout-box__item">Description</span>
          <span class="sg-layout-box__item">Actions</span>
        </div>
      </div>
      <div class="sg-layout-box">
        <span class="sg-layout-box__label">Inline(gap="md")</span>
        <div class="sg-layout-box--inline">
          <span class="sg-layout-box__item">Filter</span>
          <span class="sg-layout-box__item">Sort</span>
          <span class="sg-layout-box__item">Export</span>
        </div>
      </div>
      <div class="sg-layout-box">
        <span class="sg-layout-box__label">Grid(columns=3)</span>
        <div class="sg-layout-box--grid">
          <span class="sg-layout-box__item">A</span><span class="sg-layout-box__item">B</span><span class="sg-layout-box__item">C</span>
          <span class="sg-layout-box__item">D</span><span class="sg-layout-box__item">E</span><span class="sg-layout-box__item">F</span>
        </div>
      </div>
      <div class="sg-layout-box">
        <span class="sg-layout-box__label">GridItem(span={2})</span>
        <div class="sg-layout-box--grid">
          <span class="sg-layout-box__item sg-layout-box__item--span-2">Wide item</span><span class="sg-layout-box__item">Side</span>
          <span class="sg-layout-box__item">A</span><span class="sg-layout-box__item">B</span><span class="sg-layout-box__item">C</span>
        </div>
      </div>
    </div>
  </div>
</div>

```python
from hedron import Grid, GridItem, Heading, Inline, Stack, Text

Stack(
    Heading("Deployment history", level=2),
    Text("Recent releases and their current state."),
    Inline("Filter", "Export", gap="sm"),
    gap="lg",
)

Grid(
    GridItem(Text("Overview"), span={"base": 1, "md": 2}),
    Text("Activity"),
    columns={"base": 1, "md": 3},
    gap="md",
)
```

`Grid` and `FormGrid` accept breakpoint maps. The `base` value is the mobile-first
default; `sm`, `md`, `lg`, and `xl` progressively enhance it. `GridItem` changes span,
not reading order.

## 3. Give surfaces depth without hand-written CSS

Use `Surface` for a visual grouping and `Card` when you also need header/body/footer
slots. Appearance, padding, density, and elevation are explicit, inspectable choices.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Surface gallery</span><code>plain · raised · soft · danger</code></div>
  <div class="sg-demo__body">
    <div class="sg-surface-grid">
      <div class="sg-surface"><strong>Plain surface</strong><small>Quiet grouping with a border.</small></div>
      <div class="sg-surface sg-surface--raised"><strong>Raised surface</strong><small>Use for a panel above the page.</small></div>
      <div class="sg-surface sg-surface--soft"><strong>Soft surface</strong><small>Use for selected or contextual content.</small></div>
      <div class="sg-surface sg-surface--danger"><strong>Danger surface</strong><small>Reserve strong treatment for risk.</small></div>
      <div class="sg-surface"><strong>Compact density</strong><small>More information per viewport.</small></div>
      <div class="sg-surface"><strong>Spacious density</strong><small>More breathing room for focus.</small></div>
    </div>
  </div>
</div>

```python
from hedron import Card, Surface, Text

Surface(
    Text("Queue is healthy", role="body"),
    appearance="raised",
    padding="lg",
    elevation="md",
)

Card(
    Text("42 deployments this month"),
    title="Release activity",
    appearance="raised",
    padding="md",
    elevation="sm",
)
```

The shared components own their baseline CSS. You can still add `class_` for a local
hook, but a class should refine a semantic component rather than replace it.

## 4. Treat typography as a role, not a font-size hunt

`Text`, `Heading`, and `Typography` accept roles such as `display`, `title`, `body`,
`label`, `caption`, and `mono`. Roles let themes retune hierarchy globally.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Type scale</span><code>role=display → caption</code></div>
  <div class="sg-demo__body">
    <div class="sg-type-grid">
      <div class="sg-type sg-type--display"><span class="sg-type__sample">42,018</span><span class="sg-type__meta">display · metric</span></div>
      <div class="sg-type sg-type--title"><span class="sg-type__sample">Release activity</span><span class="sg-type__meta">title · heading</span></div>
      <div class="sg-type sg-type--body"><span class="sg-type__sample">The queue is processing normally.</span><span class="sg-type__meta">body · paragraph</span></div>
      <div class="sg-type sg-type--caption"><span class="sg-type__sample">Updated 2 minutes ago</span><span class="sg-type__meta">caption · metadata</span></div>
    </div>
  </div>
</div>

```python
from hedron import Heading, Text

Heading("Release activity", level=2, role="title")
Text("42,018", role="display", as_="strong")
Text("Updated 2 minutes ago", role="caption", overflow="truncate")
```

Keep the native heading level logical. Use `role` to change its visual treatment; do not
skip from `h2` to `h5` because the smaller size looks right.

### Overflow is also a design decision

Use `wrap` for ordinary copy, `break` for long identifiers, `truncate` for compact
single-line metadata, and `clip` only when the content is intentionally decorative.
When `lines=` is supplied, it creates a bounded multi-line clamp.

## 5. Make forms feel like part of the same system

`FormGrid` gives fields a responsive column map. Pair it with `FormField`, labels, and
the built-in controls so focus rings, spacing, and validation states stay consistent.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Responsive form gallery</span><code>FormGrid(columns={"base": 1, "md": 2})</code></div>
  <div class="sg-demo__body">
    <div class="sg-form-preview">
      <div class="sg-form-preview__grid">
        <div class="sg-field"><label for="sg-name">Workspace name</label><input id="sg-name" value="Northstar" /></div>
        <div class="sg-field"><label for="sg-region">Region</label><select id="sg-region"><option>us-east</option></select></div>
        <div class="sg-field sg-field--wide"><label for="sg-description">Description</label><input id="sg-description" value="Production data workspace" /><span class="sg-field__hint">Shown to members on the workspace switcher.</span></div>
      </div>
      <div class="sg-button-row sg-form-actions"><span class="sg-button sg-button--solid sg-button--sm">Save workspace</span><span class="sg-button sg-button--ghost sg-button--sm">Cancel</span></div>
    </div>
  </div>
</div>

```python
from hedron import FormField, FormGrid, TextInput

FormGrid(
    FormField(
        name="name",
        label="Workspace name",
        control=TextInput("name", required=True),
    ),
    FormField(
        name="region",
        label="Region",
        control=TextInput("region", value="us-east"),
    ),
    columns={"base": 1, "md": 2},
    gap="md",
)
```

For a complete POST, add [`Form`](../components/form.md), a CSRF field, and
[`SubmitButton`](../components/submit-button.md). Styling should never be the reason
to remove a native label, focusable control, or validation message.

## 6. Use status and state components consistently

Tone carries meaning; appearance carries treatment. A success badge and a success alert
can share the same semantic tone while taking different amounts of attention.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>State gallery</span><code>tone + size + appearance</code></div>
  <div class="sg-demo__body">
    <div class="sg-chip-row">
      <span class="sg-chip">Neutral</span><span class="sg-chip sg-chip--info">Info</span><span class="sg-chip sg-chip--success">Success</span><span class="sg-chip sg-chip--warning">Warning</span><span class="sg-chip sg-chip--danger">Danger</span>
    </div>
    <div class="sg-state-grid sg-state-grid--spaced">
      <div class="sg-state sg-state--success"><span class="sg-state__dot"></span><div><strong>Healthy</strong><small>All workers are responding.</small></div></div>
      <div class="sg-state sg-state--warning"><span class="sg-state__dot"></span><div><strong>Needs attention</strong><small>One connector is delayed.</small></div></div>
      <div class="sg-state sg-state--error"><span class="sg-state__dot"></span><div><strong>Action required</strong><small>Credentials expired.</small></div></div>
    </div>
  </div>
</div>

```python
from hedron import Alert, Badge, Status

Badge("Succeeded", tone="success", size="sm")
Alert("The connector needs new credentials.", tone="danger", appearance="soft")
Status("Processing", tone="info", size="sm")
```

For full-page loading, empty, permission, offline, and error branches, use
[`StateView`](../components/state-view.md). Make every branch a valid and styled state;
HTMX swaps should not turn a polished screen into an unstyled fragment.

## 7. Create a brand with `DesignSystem`

`DesignSystem.brand()` turns a small, typed set of inputs into a coordinated `Theme`
with light/dark palettes, accessibility checks, geometry, density, typography, motion,
elevation, and navigation width.

```python
from hedron import DesignSystem, Hedron, StyleRecipe

design = DesignSystem.brand(
    "northstar",
    accent="#2563eb",
    geometry="soft",
    typography="system-sans",
    density="comfortable",
    elevation="subtle",
    motion="calm",
    navigation="default",
)

app = Hedron(
    title="Northstar",
    theme=design,
    session_secret="replace-in-production",
)
```

The accent is a safe color seed, not arbitrary CSS. Hedron can adjust a generated value when
needed to satisfy the required contrast pairs and records that adjustment in the design plan.
In 0.60 the accent may be a hex string or a typed absolute `Color`; variables, gradients, URLs,
and other arbitrary CSS are rejected. `DesignSystem` also accepts an existing `Theme` through
`from_theme()` when your organization already owns the token contract.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>One brand input, many surfaces</span><code>DesignSystem.brand(...)</code></div>
  <div class="sg-demo__body">
    <div class="sg-dashboard">
      <div class="sg-dashboard__header"><strong>Northstar overview</strong><small>comfortable · soft · calm motion</small></div>
      <div class="sg-dashboard__body">
        <div class="sg-dashboard__metric"><span>Successful runs</span><strong>42,018</strong><em>↑ 12.4% this week</em></div>
        <div class="sg-dashboard__chart" aria-label="Example bar chart"><i></i><i></i><i></i><i></i><i></i></div>
      </div>
    </div>
  </div>
</div>

### Preview and audit the result

```bash
hedron theme check
hedron theme check --theme aurora --format json
hedron --app app:app style explain --format human
hedron --app app:app style preview --output .artifacts/northstar-gallery --mode all
hedron --app app:app style diff default northstar
```

`style preview` writes a deterministic, data-free gallery. It is useful in design review
and CI artifacts; it does not execute application callbacks or expose application data.

### The canonical 0.60 custom-theme path

Use `ThemeBuilder` for fluent authoring, but treat the immutable `ThemeSpec` it produces as the
source of truth. Start with the narrowest validation profile that covers the package or app; move
to `forms`, `data`, `workflow`, or `complete` when the theme intentionally covers those surfaces.

```python
from hedron import Hedron, ThemeBuilder, validate_theme_spec

spec = (
    ThemeBuilder("northstar")
    .tokens(
        {
            "color.bg": "#ffffff",
            "color.fg": "#111827",
            "color.muted": "#4b5563",
            "color.border": "#d1d5db",
            "color.accent": "#2563eb",
            "color.focus": "#1d4ed8",
            "color.danger": "#b91c1c",
            "font.family": "system-ui",
            "font.size": "1rem",
            "space.unit": "0.25rem",
            "motion.duration": "160ms",
            "focus.ring": "3px solid #1d4ed8",
        }
    )
    .mode("dark", **{"color.bg": "#111827", "color.fg": "#f9fafb"})
    .accessibility_mode("forced-colors", {"color.focus": "Highlight"})
    .profile("core")
    .build()
)

report = validate_theme_spec(spec, profile="core")
if not report.ok:
    raise RuntimeError(report.to_dict())

app = Hedron(title="Northstar", theme=spec.to_theme(), session_secret="replace-in-production")
```

`Color` accepts safe absolute CSS colors such as `Color.oklch(0.68, 0.18, 275)` and records a
deterministic sRGB fallback. It does not accept variables, gradients, URLs, relative colors, or
arbitrary CSS. `ThemeSpec` is immutable and serializable, so fingerprints, reports, and generated
assets can be reproduced in CI.

For a reviewed variation, apply an explicit, bounded patch. The base fingerprint prevents a patch
from silently landing on the wrong theme revision:

```python
from hedron import Color, ThemePatch

review_patch = ThemePatch(
    name="review-accent",
    base=spec.name,
    base_fingerprint=spec.fingerprint,
    tokens={"color.accent": Color.oklch(0.62, 0.16, 285).to_hex()},
)
review_spec = spec.apply_patches(review_patch)
```

To distribute a theme, use the data-only package format. Packages contain no executable hooks,
remote assets, or runtime CSS injection:

```python
from hedron import conformance_report, load_theme_package, package_theme

package = package_theme(spec, profile="core", licenses=("MIT",))
loaded = load_theme_package(package)
assert conformance_report(loaded, profile="core")["ok"]
```

The equivalent file-oriented workflow is:

```bash
hedron style init --name northstar --output themes/northstar.json
hedron style conform --spec themes/northstar.json --profile core
hedron style package --spec themes/northstar.json --profile core \
  --license MIT --output dist/northstar.hdt
```

## 8. Apply semantic style recipes

Recipes package a meaningful combination of presentation props. They are family-scoped,
immutable, and conservative: an explicit prop on the component always wins.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Recipe resolution</span><code>builtin → custom → explicit prop</code></div>
  <div class="sg-demo__body">
    <div class="sg-compare">
      <div class="sg-compare__side"><div class="sg-compare__label">Recipe defaults</div><div class="sg-compare__body"><span class="sg-button sg-button--solid">Create pipeline</span></div></div>
      <div class="sg-compare__side"><div class="sg-compare__label">Explicit prop wins</div><div class="sg-compare__body"><span class="sg-button sg-button--outline">Create pipeline</span></div></div>
    </div>
  </div>
</div>

```python
from hedron import Button, DesignSystem, StyleRecipe, Surface

primary = StyleRecipe.control(
    "team_primary",
    appearance="solid",
    emphasis="primary",
    size="md",
)
panel = StyleRecipe.surface(
    "team_panel",
    appearance="raised",
    padding="md",
    elevation="sm",
)

design = DesignSystem.brand(
    "team",
    accent="#087f75",
    recipes=(primary, panel),
)

create = design.apply("team_primary", Button("Create pipeline"))
explicit_outline = design.apply(
    "team_primary",
    Button("Create pipeline", appearance="outline"),  # explicit wins
)
panel_view = design.apply("team_panel", Surface("Recent runs"))
```

The built-in catalog includes recipes such as `primary_action`, `secondary_action`,
`destructive_action`, `form_surface`, `dashboard_panel`, `dense_data`, `inline_status`,
and `metadata`. Custom recipes stay within one family: `control`, `surface`, `data`,
`status`, or `content`.

## 9. Scope a theme, mode, or density to a subtree

`StyleScope` is deliberately small. It marks a subtree with a registered theme, a color
mode, and/or a density. It does not create hidden descendant recipe defaults.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Two visual contexts on one page</span><code>StyleScope(...)</code></div>
  <div class="sg-demo__body">
    <div class="sg-scope-grid">
      <div class="sg-scope"><div class="sg-scope__chrome"><span class="sg-scope__dot"></span><span class="sg-scope__dot"></span><code>default · light</code></div><div class="sg-scope__body"><strong>Operations</strong><p>Comfortable density for a primary workspace.</p><span class="sg-chip">Ready</span></div></div>
      <div class="sg-scope sg-scope--dark"><div class="sg-scope__chrome"><span class="sg-scope__dot"></span><span class="sg-scope__dot"></span><code>aurora · dark · compact</code></div><div class="sg-scope__body"><strong>Preview</strong><p>Compact dark context for an embedded surface.</p><span class="sg-chip">Preview</span></div></div>
    </div>
  </div>
</div>

```python
from hedron import StyleScope, Text

StyleScope(
    Text("Embedded preview", role="title"),
    Text("Uses the aurora dark palette at compact density."),
    theme="aurora",
    color_mode="dark",
    density="compact",
)
```

Use the smallest meaningful boundary. A page-level theme belongs on `Hedron`; a preview,
embedded report, or mounted surface may justify a `StyleScope`.

## 10. Use the 0.60 product-surface contracts

0.60 finishes four commonly hand-styled surfaces. They expose finite presentation props and
framework-owned fallback behavior, so they remain legible in print, forced colors, reduced motion,
narrow layouts, and no-JavaScript rendering.

```python
from hedron import (
    Brand,
    ConnectorFlow,
    ConnectorNode,
    ConnectorTrack,
    ScrollRegion,
    ToastHost,
)

brand = Brand(
    "Northstar",
    href="/",
    subtitle="Operations workspace",
    subtitle_overflow="break",
)

toast_host = ToastHost(
    placement="bottom-end",
    position="fixed",
    width="field",
    max_width="md",
    gap="sm",
)

flow = ConnectorFlow(
    ConnectorNode("Source", kind="source", state="ready"),
    ConnectorTrack(label="Transfer"),
    ConnectorNode("Warehouse", kind="target", state="running"),
    appearance="soft",
    background="dots",
    overflow="auto",
    min_size="md",
)

events = ScrollRegion(
    "Recent events",
    axis="block",
    size="md",
    affordance="always",
    label="Recent events",
)
```

Keep `Brand` and `ToastHost` in the document shell so fragment swaps do not remove product
identity or the reserved `#hedron-toast` target. Keep `ConnectorFlow` children in reading order;
its visual direction and collapse behavior must never be the only way to understand the workflow.
Use `ScrollRegion` to bound overflow without replacing the semantics of a list, table, timeline,
or log. See the focused component pages for the complete finite prop sets:
[Brand](../components/brand.md), [ToastHost](../components/toast-host.md),
[ConnectorFlow](../components/connector-flow.md), and [ScrollRegion](../components/scroll-region.md).

### Server-first theme preferences

`ThemePreference` is an allowlisted value, not a user-provided CSS string. Resolve it at the
server boundary, render `ThemePicker` as a native form, and let the application own persistence,
authorization, and the POST route. The optional boot helper only reads bounded local values to
reduce a preference flash; it does not replace server-rendered state.

```python
from hedron import ThemePicker, ThemePreference, resolve_theme_preference

preference = resolve_theme_preference(
    request.cookies.get("hedron-theme"),
    request.cookies.get("hedron-color-mode"),
    allowed_themes=("default", "aurora"),
)

picker = ThemePicker(
    themes=("default", "aurora"),
    selected=preference,
    action="/preferences/theme",
    csrf_token=csrf_token,
)
```

For custom hosts, pass the resolved preference through page asset injection so the framework emits
theme and color-mode markers before page content. Invalid or stale values fall back to the
allowlisted default; never construct a selector, CSS declaration, or persistence key from raw
request input.

## 11. Add CSS only where the component owns the detail

For a custom component, colocate `styles.css` beside the component and use the typed
style-symbol binding. Hedron rewrites local classes and keyframes to collision-free
identifiers; `:global(...)` is explicit when you intentionally target the host.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Scoped component detail</span><code>Callout/styles.css</code></div>
  <div class="sg-demo__body">
    <div class="sg-callout"><strong>Build completed</strong><p>The visual detail belongs to this callout component, so its rail and tint live with the component.</p></div>
  </div>
</div>

```text
components/Callout/
├── component.py
└── styles.css
```

```css
/* components/Callout/styles.css */
.root {
  border-left: 4px solid var(--color-accent);
  padding: var(--space-md);
}
```

```python
from hedron_core import StyleSymbols, styles_from_manifest

styles: StyleSymbols = styles_from_manifest(symbols, component_id="app:Callout")
return html.div("Build completed", class_=styles.root)
```

For a complete plugin component, register the stylesheet through the plugin manifest;
see [plugin authoring](plugin-authoring.md) and [themes and scoped styles](../api/THEME.md).
Do not copy the docs gallery CSS into the application.

## Density is a first-class mode

Density changes rhythm, not meaning. Use it for a whole workspace or a contained data
surface, and keep labels and controls understandable at every setting.

<div class="sg-demo">
  <div class="sg-demo__bar"><span>Density comparison</span><code>compact · comfortable · spacious</code></div>
  <div class="sg-demo__body">
    <div class="sg-density-row">
      <div class="sg-density"><strong>Compact</strong><small>Dense tables and tooling.</small><div class="sg-density__bars"><i class="sg-density__bar"></i><i class="sg-density__bar"></i><i class="sg-density__bar"></i></div></div>
      <div class="sg-density sg-density--comfortable"><strong>Comfortable</strong><small>Balanced default rhythm.</small><div class="sg-density__bars"><i class="sg-density__bar"></i><i class="sg-density__bar"></i><i class="sg-density__bar"></i></div></div>
      <div class="sg-density sg-density--spacious"><strong>Spacious</strong><small>Focus and presentation.</small><div class="sg-density__bars"><i class="sg-density__bar"></i><i class="sg-density__bar"></i><i class="sg-density__bar"></i></div></div>
    </div>
  </div>
</div>

## A production styling checklist

Use this sequence when a screen is ready for review:

1. Give the page a semantic structure: landmarks, heading levels, labels, and DOM order.
2. Use shared components and presentation props before adding a class.
3. Replace repeated prop combinations with a named `StyleRecipe`.
4. Set the brand through `DesignSystem.brand()` or a registered `Theme`.
5. Test both light and dark modes, at least one compact/spacious context, and narrow widths.
6. Preserve focus visibility, text contrast, readable overflow, and reduced-motion behavior.
7. Run `hedron theme check` and, for a zero-application-CSS surface,
   `hedron style check --zero-app-css PATH`.
8. Render one full page and one HTMX fragment so swapped regions retain the same styling contract.

!!! warning "What styling does not do"

    Styling does not authorize an action, validate input, protect CSRF, or make an
    inaccessible DOM accessible. Keep security and interaction boundaries in the
    server-side component and action APIs. See [accessibility](accessibility.md),
    [security](security.md), and [testing](testing.md).

## Reference map

- [Presentation API](../api/PRESENTATION.md) — shared vocabulary and progressive styling APIs
- [Modern CSS in 0.60](modern-css-0.60.md) — complete feature tiers and fallbacks
- [Themes and scoped styles](../api/THEME.md) — themes, CSS layers, and `styles.css`
- [StyleScope](../components/style-scope.md) — subtree theme/mode/density boundaries
- [Component demos](../components/index.md) — visual pages for every built-in
- [CLI reference](../api/CLI.md) — `theme check`, `style explain`, `style preview`, and `style diff`

</div>
