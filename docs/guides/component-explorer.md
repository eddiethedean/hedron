---
title: Component Explorer
description: The existing visual QA app with every button appearance, emphasis, disabled state, size, and icon example, running without a backend.
---

# Interactive Component Explorer

This is the existing [`theme-gallery` visual QA application](https://github.com/eddiethedean/hedron/tree/main/examples/theme-gallery),
opened on its **Component states** screen—not a separate set of component mockups.
It uses the same Python components and stylesheet as the app used for visual styling passes.

[Open the full-page Component Explorer](../assets/styles-explorer/components.html){ .md-button .md-button--primary }

<iframe src="../../assets/styles-explorer/components.html" title="Interactive Hedron Component Explorer" style="width:100%;height:1250px;border:1px solid var(--md-default-fg-color--lightest);border-radius:12px" loading="lazy"></iframe>

## What you can explore

- All six button appearances: solid, outline, soft, ghost, plain, and raised.
- All four emphases: primary, secondary, danger, and neutral, each with enabled and disabled examples.
- Small, medium, and large actions and icon buttons, plus full-width actions.
- Action, feedback, and loading tabs; badges, radio groups, alerts, popovers, and dialogs.
- Folio, Classic, and Aurora themes, every built-in Folio accent, light/dark modes,
  side-by-side comparison, and mobile/tablet preview widths.

Use **Gallery** or the app's navigation to visit the other eight QA screens:
dashboard, forms, surfaces, content, settings, orders, support, and media.
The token inspector, component style contracts, and canonical theme exports are also available.
Full-page URLs preserve your selections when shared or reloaded.

## Backend-free boundaries

`hedron-sim` runs the app's pre-rendered navigation locally. Native inputs, tabs,
disclosures, dialogs, and popovers work in the browser, but forms do not save data.
Charts, maps, math, and capture integrations show fallback styling rather than live services.
This gallery is not the development diagnostics app mounted at `/hedron-explorer/`;
it does not inspect a running application's routes, security, cache, or component tree.

For server-driven behavior, run the original app locally:

```bash
uv run uvicorn --app-dir examples/theme-gallery app:app --reload
```

See the [Styles Explorer](styles-explorer.md) for theme inspection details and the
[styling guide](styling.md) for the Python presentation vocabulary.
