# Implementation notes: phase 0.57 unified presentation

**Decision/RFC:** D-099, refined by D-100 /
[RFC-0084](../rfcs/RFC-0084-UNIFIED-PRESENTATION.md)<br>
**Shared authority:** `hedron_core.builtins.appearance`

## Consume shipped, do not fork (D-100)

Extend the closed presentation vocabulary and `data-hedron-*` markers. Do not
introduce component-local synonyms, free-form CSS lengths as Supported API, or
`unsafe-inline` requirements. Preserve existing call defaults.

## Stage 1 module map

| Module | Responsibility |
|---|---|
| `hedron_core.builtins.appearance` | Closed vocab (`plain`/`raised`, width, overflow, track) + markers |
| `hedron_core.builtins.layout` | CSP-safe gaps, `Grid`/`GridItem` tracks/spans |
| `hedron_core.builtins.surfaces` | `Surface`, Card appearance/elevation |
| `hedron_core.builtins.shell` | Typed `Brand`, `AccountSummary`, `EnvironmentBanner`, `NavStatus`, `AppFooter` |
| `hedron_core.builtins.content` | Table policies, overflow Text/Typography |
| `hedron_core.builtins.resources` | `ResourceList` / `ResourceRow` |
| `hedron_core.builtins.identity` | `Avatar` / `Identity` |
| `hedron_core.builtins.process_flow` | Step kinds, slots, connectors |
| `hedron_core.builtins.utilities` | Status compact/activity |
| `hedron.builtins.files` | FileUpload composition + upload-budget display |
| First-party CSS | Token selectors under strict CSP; zero-application-CSS evidence |

## Invariants

- DOM order remains authoritative (no visual-only reorder via spans).
- Truncation requires an explicit full-content path; never implicit `title`.
- Color and motion are never the sole state signal.
- Upload limits share 0.55/0.56 authority.
- `Section` stays a landmark; `Surface` owns purely visual grouping.
