# Presentation APIs (0.57)

Phase 0.57 makes Hedron's shared presentation vocabulary real across built-ins
and closes remaining application-CSS gaps for a Data Mover-class workspace. See
[RFC-0084](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0084-UNIFIED-PRESENTATION.md)
and
[PRESENTATION_057](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PRESENTATION_057.md).

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

## Zero-application-CSS

Representative authenticated workspaces must compose shell, forms, tables,
uploads, identity, statuses, and flows without application-owned component or
layout CSS. Use `hedron style check --zero-app-css` and the 0.57 zero-CSS
fixture inventory.

## Compatibility

Preserve existing `variant`, `tone`, `gap`, AppShell slot, and upload-budget
behavior. Shared appearance props are opt-in unless a theme/container default is
selected. Unsupported layout lengths fail with a shared diagnostic rather than
silently falling back.
