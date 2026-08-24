---
status: shipped
---

# ColorMode (outline)


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

!!! note "Outline page"

    Narrative + Autodoc signatures. Full Parameters/Returns/Errors tables live in
    [Autodoc — Color mode](AUTODOC.md#color-mode) and
    [`ColorModeToggle`](../components/color-mode-toggle.md).

```python
from hedron import ColorMode, ColorModeToggle, resolve_color_mode
from hedron.color_mode import apply_color_mode_cookie, read_color_mode_preference

resolved = resolve_color_mode(ColorMode.SYSTEM, system_dark=True)  # "dark"
toggle = ColorModeToggle(preference=ColorMode.SYSTEM, action="/color-mode")
```

`ColorMode` preferences are `light`, `dark`, or `system`. Resolution combines the
stored preference with the system `prefers-color-scheme` when the preference is
`system`. The resolved value is applied as `data-theme` on the document root and
works with theme token modes shipped in phase 0.3.

## Parameters

| Symbol | Key inputs | Role |
|---|---|---|
| `ColorMode` | enum members `LIGHT` / `DARK` / `SYSTEM` | Preference values |
| `resolve_color_mode(preference, system_dark=…)` | preference + system signal | Resolved `"light"` / `"dark"` string |
| `ColorModeToggle` | `preference`, `action` | Control that POSTs the new preference |
| `read_color_mode_preference` / `apply_color_mode_cookie` | request / response | Cookie helpers |

## Returns

| Symbol | Returns |
|---|---|
| `resolve_color_mode(...)` | `"light"` or `"dark"` |
| `ColorModeToggle(...)` | Component node for page composition |
| Cookie helpers | Preference string or updated response cookies |

## Persistence

FastAPI helpers read and write a `hedron_color_mode` cookie and optional session
key `color_mode`. Defaults favor cookie persistence with `SameSite=Lax`. Apps may
also store the preference in session or local storage; Hedron documents cookie
and session as first-party helpers.

## Accessibility

- Toggle UI exposes an accessible label and native `<select>`/`<button>` controls.
- Switching modes must preserve scoped style identifiers and contrast tokens.
- Forced-colors and reduced-motion contracts from the theme remain in force.

## Errors

| Situation | Behavior |
|---|---|
| Unknown preference string | Treat as `system` (or reject at the validation boundary) |
| Cookie write failure | Preference falls back to default / session when configured |
| Missing toggle action route | Browser GET/POST fails normally — app-owned |

## See also

[Theme](THEME.md) · [Autodoc — Color mode](AUTODOC.md#color-mode) ·
[`ColorModeToggle`](../components/color-mode-toggle.md)
