# Presentation APIs (0.57 + 0.58)

Phase 0.57 makes Hedron's shared presentation vocabulary real across built-ins
and closes remaining application-CSS gaps for a Data Mover-class workspace. Phase
0.58 adds progressive styling authoring (`DesignSystem`, `StyleRecipe`,
`StyleScope`) on the same authorities. See
[RFC-0084](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0084-UNIFIED-PRESENTATION.md),
[RFC-0085](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md),
[PRESENTATION_057](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PRESENTATION_057.md),
and
[PROGRESSIVE_AUTHORING_058](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PROGRESSIVE_AUTHORING_058.md).

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

## Zero-application-CSS

Representative authenticated workspaces must compose shell, forms, tables,
uploads, identity, statuses, and flows without application-owned component or
layout CSS. Use `hedron style check --zero-app-css` and the 0.57 zero-CSS
fixture inventory.

## Compatibility

Preserve existing `variant`, `tone`, `gap`, AppShell slot, and upload-budget
behavior. Shared appearance props are opt-in unless a theme/container default is
selected. Gap lengths are accepted only when they equal token CSS sizes exactly
(`0.5rem`→`sm`, `1rem`→`md`, `1.5rem`→`lg`, `2rem`→`xl`); ambiguous lengths such as
`0.75rem` or `12px` raise a shared diagnostic. When `overflow="truncate"` and
`lines=` are both set, `lines` wins (multi-line clamp) and no implicit `title=`
is invented.
