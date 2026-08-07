---
status: shipped
---

# Utility component contracts


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

!!! note "Summary page"

    This page is a **short summary** of utility built-ins. Prefer the
    [component catalog](../components/index.md) for props and [Autodoc](AUTODOC.md) for
    generated signatures when you need a full parameter list.

## Constructors (summary)

| Component | Key parameters | Returns / notes |
|---|---|---|
| `Metric(label, value, delta=...)` | label, value, optional delta | Semantic value + change (not color-only) |
| `FileUpload(accept=..., maximum_size=...)` | accept, size hint | Markup is advisory — enforce with `validate_upload_size` in the route |
| `DownloadButton(href=..., filename=...)` | `href` or `source=`, filename | Pair with `safe_download_response` for path/auth |
| `CodeViewer(code, language=...)` | code, language | Escaped; optional highlighting extra |
| `JSONViewer(value)` | structured value | Bounded, escaped; secrets redacted |
| `Progress(value, maximum=...)` | value, maximum | Accessible progress |
| `Status(...)` | state text | Live-region friendly status |
| `Toast(...)` | message | Non-blocking announcement |
| `Expander(...)` / `Tabs(...)` | children | Semantic disclosure / tabs + keyboard |
| `Sidebar(...)` | children | Complementary / navigation region |
| `Grid(columns=..., children=...)` | columns, children | Explicit layout (no mutable column handles) |

## Errors / policy

| Situation | Behavior |
|---|---|
| Upload over `maximum_size` (enforced in route) | Application returns 4xx via `validate_upload_size` |
| Download path outside allowlist | `safe_download_response` refuses |
| Untrusted HTML in viewers | Escaped / not executed |

All components have server-rendered useful fallbacks. Browser enhancement may preserve
transient interaction state but cannot become an application-wide store.
Uploads/downloads require explicit authorization and resource limits.

## See also

[Built-ins](BUILT_INS.md) · [Forms and actions](../guides/forms-and-actions.md) ·
[Component composition](../guides/component-composition.md)
