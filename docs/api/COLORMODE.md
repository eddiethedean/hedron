---
status: shipped
---

# ColorMode

**Status:** Accepted

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

## Persistence

FastAPI helpers read and write a `hedron_color_mode` cookie and optional session
key `color_mode`. Defaults favor cookie persistence with `SameSite=Lax`. Apps may
also store the preference in session or local storage; Hedron documents cookie
and session as first-party helpers.

## Accessibility

- Toggle UI exposes an accessible label and native `<select>`/`<button>` controls.
- Switching modes must preserve scoped style identifiers and contrast tokens.
- Forced-colors and reduced-motion contracts from the theme remain in force.
