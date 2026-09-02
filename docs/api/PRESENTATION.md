# Presentation APIs (0.57–0.60)

Phase 0.57 makes Hedron's shared presentation vocabulary real across built-ins
and closes remaining application-CSS gaps for a Data Mover-class workspace. Phase
0.58 adds progressive styling authoring (`DesignSystem`, `StyleRecipe`,
`StyleScope`) and 0.60 adds the modern CSS platform on the same authorities. See
[RFC-0084](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0084-UNIFIED-PRESENTATION.md),
[RFC-0085](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md),
[PRESENTATION_057](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PRESENTATION_057.md),
and
[PROGRESSIVE_AUTHORING_058](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PROGRESSIVE_AUTHORING_058.md).
For the complete 0.60 capability tiers and fallback contract, see
[Modern CSS in 1.0](../guides/modern-css.md) and
[RFC-0087](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0087-MODERN-CSS-PLATFORM.md).

Shared authority: `hedron_core.builtins.appearance`. Values emit stable
`data-hedron-*` markers styled by first-party CSS under strict CSP
(`style-src 'self'`). New APIs begin `beta`. Existing calls keep their defaults.

## Vocabulary

| Token | Values |
|---|---|
| `size` | `sm` \| `md` \| `lg` |
| `density` | `compact` \| `comfortable` \| `spacious` |
| `appearance` | `solid` \| `outline` \| `soft` \| `ghost` \| `plain` \| `raised` |
| `emphasis` | `primary` \| `secondary` \| `neutral` \| `danger` |
| `width` | `content` \| `field` \| `full` |
| `overflow` | `wrap` \| `break` \| `truncate` \| `clip` |
| `track` | `narrow` \| `default` \| `wide` \| `fluid` |

## New and extended components

- Layout: CSP-safe gap tokens, `Grid`/`FormGrid` tracks, `GridItem` spans
- Surfaces: `Surface`, Card appearance/padding/elevation
- Chrome: `Brand`, `AccountSummary`, `EnvironmentBanner`, `NavStatus`, `AppFooter`
- Data: Table responsive policies, `ResourceList` / `ResourceRow`
- Identity: `Avatar`, `Identity`
- Workflow: FileUpload composition, Status compact/activity, richer ProcessFlow

## Progressive styling (0.58)

### `DesignSystem`

Compile a coordinated light/dark `Theme` from a small design input, or wrap an
existing `Theme`:

```python
from hedron import DesignSystem, Hedron

design = DesignSystem.brand("acme", accent="#2563eb")
app = Hedron(title="App", theme=design, session_secret="replace-in-production")
```

`Hedron(theme=...)` accepts `str | Theme | DesignSystem | None`. Brand compilation
discloses contrast adjustments; it does not invent a second theme registry or CSS
compiler.

### `StyleRecipe`

Family-scoped semantic recipes (`control` / `surface` / `data` / `status` /
`content`) style generated feature roles. Built-in roles cover ordinary progressive
feature surfaces. Recipes never change authorization, routes, or reading order.

```python
from hedron import StyleRecipe

recipe = StyleRecipe.control(emphasis="primary", appearance="solid")
```

### `StyleScope`

Bound a subtree to theme, color mode, and density markers only:

```python
from hedron import StyleScope, Text

StyleScope(Text("Scoped panel"), theme="aurora", color_mode="dark", density="compact")
```

Component page: [StyleScope](../components/style-scope.md).

Inspect with `hedron explain` / `hedron style` ([CLI](CLI.md)).

## Modern CSS platform (0.60)

The 0.60 platform evolves the existing presentation ABI instead of replacing it:

| Surface | 0.60 contract |
|---|---|
| Scoped CSS | Compiler format 2, v1 manifest reader, stable symbol hashes, grammar-aware nesting/at-rules/imports, deterministic source maps and layers |
| Responsive layout | Opt-in `Container(query="inline-size", name=...)`, container/viewport fallbacks, intrinsic sizing, logical layout, RTL/writing-mode coverage, Progressive subgrid |
| Theme and tokens | Explicit finite variants, modern color with sRGB fallback, typography/content roles, Progressive `light-dark()` and selected `@property` tokens |
| Overlays and motion | Native popover/top-layer semantics, finite logical placement/collision, Progressive anchor/entry/exit/View Transitions, reduced-motion equivalence |
| Media | Print, forced colors, contrast, reduced transparency, hover/pointer, safe-area and dynamic viewport fallbacks |
| Controls and product surfaces | Validated `Button`/`LinkButton attrs=`, shared size/width, responsive shell chrome, provider-neutral pipeline/status presentation |

Required behavior has a static or native fallback. Progressive enhancements are feature-detected;
Experimental scroll-driven animation is decorative only. Styling never changes behavior, state,
authorization, DOM order, accessible names, or complete-content paths.

### 0.60 public additions

```python
from hedron import Button, Container, LinkButton, Popover, StyleScope, Text

panel = Container(
    Text("Workspace activity"),
    query="inline-size",
    name="workspace-panel",
)
scoped = StyleScope(Text("Compact dark preview"), variant="dense", color_mode="dark")
save = Button("Save", size="sm", width="full", attrs={"hx-post": "/save"})
review = LinkButton("Review", "/review", size="sm", width="full")
menu = Popover(Text("Actions"), placement="block-end", collision="flip")
```

`attrs=` accepts validated global, `aria-*`, `data-*`, approved HTMX, and popover/dialog-trigger
attributes. It rejects component-owned structural attributes, inline `style`, event handlers,
malformed ARIA/data names, and non-allowlisted HTMX attributes. See the component pages for exact
signatures.

## Zero-application-CSS

Representative authenticated workspaces must compose shell, forms, tables,
uploads, identity, statuses, and flows without application-owned component or
layout CSS. Use `hedron style check --zero-app-css` and the 0.60 zero-CSS
fixture inventory.

## Compatibility

Preserve existing `variant`, `tone`, `gap`, AppShell slot, and upload-budget
behavior. Shared appearance props are opt-in unless a theme/container default is
selected. Gap lengths are accepted only when they equal token CSS sizes exactly
(`0.5rem`→`sm`, `1rem`→`md`, `1.5rem`→`lg`, `2rem`→`xl`); ambiguous lengths such as
`0.75rem` or `12px` raise a shared diagnostic. When `overflow="truncate"` and
`lines=` are both set, `lines` wins (multi-line clamp) and no implicit `title=`
is invented.
