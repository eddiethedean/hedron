# Package author handbook

Use this loop with **public contracts only** — no private monorepo imports.

## Authoring loop

1. **Copy** a minimal variant from `hedron-sample-kit` (Callout, web component,
   workflow, HDJ, or optional integration).
2. **Inspect** the plugin manifest / feature bundles / Explorer panel.
3. **Simulate** with `hedron-sim` (`SimApp`, subset/divergence manifest, recording).
4. **Preview** with `hedron-notebook` display handles (`update` / `snapshot` /
   `open_in_browser` / `close`).
5. **Hand off** to a real development server when ready (explicit topology print).
6. **Validate** with `hedron package doctor` before publish.

Shared fixture schema: `hedron_conformance.authoring_loop`
(`AUTHORING_LOOP_SCHEMA_VERSION = "hedron-authoring-loop-1"`).

## Package doctor vs fleet doctor

| Tool | Audience | Scope |
|---|---|---|
| `hedron package doctor PATH` | Package authors | Metadata, entry points, assets, fingerprints, docs, ranges |
| `hedron fleet` | Application operators | Installed train/extras/plugins (`package_doctor: False`) |

## Decision guide

| Need | Prefer |
|---|---|
| Offline HTMX docs demos | `hedron-sim` |
| Localhost rich preview | `hedron-notebook` (never public hosting) |
| Production interaction | Real Hedron server + polling |
| Saved notebook without runtime | Static HTML/text fallbacks from display handles |

See also: [simulator semantics](simulator-semantics.md),
[notebook preview](notebook-preview.md),
[what's new in 0.54](whats-new-0.54.md).
