---
description: Apply scoped, responsive, theme-aware CSS to Edron and Hedron 1.0 applications.
---

# Modern CSS in 1.0

Hedron's 1.0 styling model combines shared appearance props, application-owned CSS, scoped
component styles, design tokens, and strict-CSP-compatible responsive declarations. Start with
the highest-level mechanism that expresses the design and drop to CSS only when needed.

## Choose the styling boundary

| Need | Use |
|---|---|
| Spacing, color, typography, borders | Shared appearance props and theme tokens |
| Page-wide brand rules | Declared application stylesheet |
| Reusable component internals | `StyleScope` or package-owned assets |
| Responsive layout | Grid/layout APIs or declared media/container rules |
| Third-party HTML/template control | HDJ/Jinja with the same asset and CSP policy |

Application selectors should use stable public hooks, not generated internal identifiers.
Component packages own their class names and assets; applications own brand and composition.

## Production checklist

- Declare stylesheets and assets before the registry seals.
- Run `hedron build` and deploy the generated manifest with the application.
- Test light/dark themes, zoom, narrow widths, reduced motion, and keyboard focus.
- Keep inline/eval-dependent styling out of strict CSP deployments.
- Use browser inspection to confirm the intended cascade layer and scope.

Continue with [Comprehensive styling](styling.md), [StyleScope](../components/style-scope.md),
[Theme reference](../api/THEME.md), and [Deployment](deployment.md). The
[0.60 styling note](modern-css-0.60.md) remains available as historical implementation context.
