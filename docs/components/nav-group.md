---
title: NavGroup
description: Standalone grouped navigation shared by AppShell and fragment responses.
---

# `NavGroup`

Render a reusable navigation group that can be composed into `AppShell` or returned in an
out-of-band/fragment update.

```python
from hedron import NavGroup, NavLink

component = NavGroup(
    "Workspace",
    NavLink("Overview", "/"),
    NavLink("Reports", "/reports"),
)
```

When `label` is supplied, the group emits `role="group"`, `aria-label`, and a visible label.
Without a label it remains a neutral wrapper, which is useful when the surrounding `nav`
already provides the accessible name. Items retain their own link and HTMX authorization
contracts.

`AppShell(nav_groups=...)` uses this same component, so full-page and fragment rendering share
the same group markup and CSS hooks.

[AppShell](app-shell.md) · [NavLink](nav-link.md) · [All component demos](index.md)
